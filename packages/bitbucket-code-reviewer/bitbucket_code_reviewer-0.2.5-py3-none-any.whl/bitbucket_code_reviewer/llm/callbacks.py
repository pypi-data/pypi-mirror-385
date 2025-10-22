"""Callback handlers for instrumenting LLM behavior (e.g., timing)."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import HumanMessage


class LLMTimingCallback(BaseCallbackHandler):
    """Measure and print the duration of each LLM roundtrip.

    Stores timing to be picked up by the next tool execution, so timing
    appears inline with the action it triggered.
    """

    # Class variable to store the most recent timing for tools to consume
    _pending_timing: Optional[str] = None

    def __init__(self, provider_name: str, model_name: str) -> None:
        self.provider_name = provider_name
        self.model_name = model_name
        self._start_times: Dict[str, float] = {}

    # LLM lifecycle ---------------------------------------------------------
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: list[str],
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        self._start_times[str(run_id)] = time.perf_counter()

    def on_llm_end(
        self,
        response: Any,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        key = str(run_id)
        start = self._start_times.pop(key, None)
        if start is None:
            return

        elapsed = time.perf_counter() - start

        # Try to extract token usage information if present.
        tokens_suffix = self._format_token_usage_suffix(response)

        # Extract and display reasoning content if present (GPT-5 Responses API)
        timing_str = f"[{elapsed:.2f}s{tokens_suffix}]"
        self._print_reasoning_if_present(response, timing_str)

        # Store timing to be consumed by next tool/action
        LLMTimingCallback._pending_timing = timing_str

    def on_llm_error(
        self,
        error: Exception,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        key = str(run_id)
        start = self._start_times.pop(key, None)
        if start is None:
            return

        elapsed = time.perf_counter() - start
        # For errors, print immediately since there may not be a next action
        print(
            (
                f"❌ LLM roundtrip ({self.provider_name}/{self.model_name}) "
                f"failed after {elapsed:.2f}s: {error}"
            ),
            flush=True,
        )
        LLMTimingCallback._pending_timing = None  # Clear any pending timing

    # Public API for tools to consume timing ----------------------------
    @classmethod
    def get_and_clear_timing(cls) -> str:
        """Get pending timing suffix and clear it.
        
        Returns:
            Timing string like '[2.34s]' or empty string if none pending
        """
        timing = cls._pending_timing or ""
        cls._pending_timing = None
        return timing

    # Helpers ---------------------------------------------------------------
    @staticmethod
    def _print_reasoning_if_present(response: Any, timing: str = "") -> None:
        """Print reasoning content if available in response (GPT-5 Responses API).
        
        The Responses API returns reasoning in response_metadata or as separate
        reasoning items in the output array.
        
        Args:
            response: LLM response object
            timing: Optional timing string to append (e.g., "[2.5s]")
        """
        try:
            # Extract reasoning from generations -> message -> additional_kwargs -> reasoning -> summary
            if hasattr(response, "generations"):
                for gen_list in response.generations:
                    for gen in gen_list:
                        if hasattr(gen, "message") and hasattr(gen.message, "additional_kwargs"):
                            reasoning = gen.message.additional_kwargs.get("reasoning")
                            if reasoning and isinstance(reasoning, dict):
                                summary = reasoning.get("summary")
                                if summary and isinstance(summary, list):
                                    for item in summary:
                                        if isinstance(item, dict):
                                            text = item.get("text")
                                            if text:
                                                # Clean up: strip markdown, collapse multiple newlines into single dash
                                                import re
                                                clean = text.replace("**", "")
                                                clean = re.sub(r'\n+', ' - ', clean).strip()
                                                print(f"🧠 {clean}", flush=True)
        except Exception:
            # Be resilient - don't fail callback if reasoning extraction has issues
            pass

    @staticmethod
    def _format_token_usage_suffix(response: Any) -> str:
        """Return a formatted token usage suffix if available on response.

        Supports common shapes like
        response.llm_output["token_usage"] or ["usage"].
        """
        try:
            llm_output = getattr(response, "llm_output", None)
            if isinstance(llm_output, dict):
                usage = (
                    llm_output.get("token_usage")
                    or llm_output.get("usage")
                    or {}
                )
                if isinstance(usage, dict):
                    prompt = usage.get("prompt_tokens")
                    completion = usage.get("completion_tokens")
                    total = usage.get("total_tokens")
                    if total is None and (
                        isinstance(prompt, int) or isinstance(completion, int)
                    ):
                        total = (prompt or 0) + (completion or 0)

                    if any(v is not None for v in (prompt, completion, total)):
                        return (
                            f" | tokens p/c/t="
                            f"{prompt if prompt is not None else '-'}"
                            f"/"
                            f"{completion if completion is not None else '-'}"
                            f"/"
                            f"{total if total is not None else '-'}"
                        )
        except Exception:
            # Be resilient to schema differences.
            return ""
        return ""


class IterationLimitCallback(BaseCallbackHandler):
    """Callback that tracks iterations and injects wrap-up messages when approaching limits.

    When the agent approaches max_iterations - wrap_up_threshold, this attempts to inject
    a human message telling the LLM to wrap up and submit the review.
    
    NOTE: Message injection in callbacks may not reliably reach the LLM due to timing.
    The AgentExecutor's early_stopping_method="generate" provides a more reliable fallback
    by forcing the agent to generate a final answer when hitting max_iterations.
    """

    def __init__(self, max_iterations: int, wrap_up_threshold: int = 10):
        self.max_iterations = max_iterations
        self.wrap_up_threshold = wrap_up_threshold
        self.current_iteration = 0
        self.wrap_up_injected = False

    def on_agent_action(
        self,
        action: Any,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Track agent iterations (called per action/tool call) and log when approaching limit."""
        self.current_iteration += 1

        # Check if we should inject a wrap-up message
        remaining_iterations = self.max_iterations - self.current_iteration
        if (remaining_iterations <= self.wrap_up_threshold and
            not self.wrap_up_injected):

            self.wrap_up_injected = True
            print(f"🚨 APPROACHING ITERATION LIMIT: {remaining_iterations} iterations remaining")
            print(f"   Agent should wrap up and call submit_review() soon!")

    def reset(self):
        """Reset iteration tracking for new agent runs."""
        self.current_iteration = 0
        self.wrap_up_injected = False


