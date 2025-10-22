"""Review orchestrator that coordinates the entire code review process."""

import json
from pathlib import Path
from typing import Optional
from pydantic import ValidationError

from ..core.diff_utils import get_changed_lines_by_file


def _sanitize_llm_json_string(raw: str) -> str:
    """Best-effort repair of common JSON issues from LLM output.

    - Strip markdown code blocks (```json ... ```)
    - Replace invalid escapes (e.g., \\' -> ')
    - Replace literal newlines in strings with \n
    This keeps valid JSON escapes intact and only tweaks problematic cases.
    """
    # Strip markdown code blocks
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # Find the first newline after the opening ```
        first_newline = cleaned.find("\n")
        if first_newline != -1:
            cleaned = cleaned[first_newline + 1 :]
        # Remove trailing ```
        if cleaned.endswith("```"):
            cleaned = cleaned[: -3].rstrip()

    result_chars: list[str] = []
    inside_string = False
    pending_escape = False

    for ch in cleaned:
        if inside_string:
            if pending_escape:
                # Preserve only valid JSON escapes
                if ch in '"\\/bfnrt':
                    result_chars.append("\\" + ch)
                elif ch == "u":
                    # Keep unicode escape prefix; assume following digits are fine
                    result_chars.append("\\u")
                elif ch == "'":
                    # Invalid JSON escape (\'): drop the backslash
                    result_chars.append("'")
                else:
                    # Unknown escape like \), \(, etc. Drop backslash, keep char
                    result_chars.append(ch)
                pending_escape = False
            else:
                if ch == "\\":
                    pending_escape = True
                elif ch == '"':
                    inside_string = False
                    result_chars.append(ch)
                elif ch == "\n":
                    result_chars.append("\\n")
                elif ch == "\r":
                    result_chars.append("\\r")
                else:
                    result_chars.append(ch)
        else:
            if ch == '"':
                inside_string = True
            result_chars.append(ch)

    # If string ended with a dangling backslash, keep it as-is
    return "".join(result_chars)


def _normalize_review_data(data: dict, working_directory: Optional[Path] = None, verbose: bool = False) -> dict:
    """Normalize LLM JSON to match pydantic models.

    - Ensure severity_counts has all severities and int values
    - Convert positives from list[str] -> list[{"description": str}]
    - Ensure each change has required fields, fill missing suggestion
    - Validate file paths exist in working directory
    
    Args:
        data: Raw JSON data from LLM
        working_directory: Optional path to validate files against
    """
    normalized = dict(data)

    # Normalize severity_counts
    sc = normalized.get("severity_counts", {}) or {}
    fixed_sc: dict[str, int] = {}
    for sev in Severity:
        value = sc.get(sev.value, sc.get(sev.name, 0))
        try:
            fixed_sc[sev.value] = int(value)
        except Exception:
            fixed_sc[sev.value] = 0
    normalized["severity_counts"] = fixed_sc

    # Normalize changes
    changes = normalized.get("changes", []) or []
    fixed_changes: list[dict] = []
    for ch in changes:
        if not isinstance(ch, dict):
            # Skip invalid entries
            continue
        ch_fixed = dict(ch)

        # Map alternative field names for file_path that LLM might use
        if "file" in ch_fixed and not ch_fixed.get("file_path"):
            ch_fixed["file_path"] = ch_fixed["file"]
        if "path" in ch_fixed and not ch_fixed.get("file_path"):
            ch_fixed["file_path"] = ch_fixed["path"]

        # Skip changes that are clearly garbage (missing critical fields)
        if not ch_fixed.get("file_path") or ch_fixed.get("file_path") == "unknown":
            # No valid file path - skip this change
            if verbose:
                print(f"⚠️ Skipping change with missing/invalid file_path: {ch_fixed}")
            continue
        
        # Validate file actually exists in the working directory
        if working_directory is not None:
            file_path = ch_fixed.get("file_path")
            full_path = working_directory / file_path
            if not full_path.exists():
                if verbose:
                    print(f"❌ SKIPPING HALLUCINATED FILE: '{file_path}' does not exist in repository!")
                continue
        
        # Map alternative field names that LLM might use
        if "message" in ch_fixed and not ch_fixed.get("description"):
            ch_fixed["description"] = ch_fixed["message"]
        if "proposed_fix" in ch_fixed and not ch_fixed.get("suggestion"):
            ch_fixed["suggestion"] = ch_fixed["proposed_fix"]
        
        if not ch_fixed.get("description") and not ch_fixed.get("title"):
            # No description or title - skip this change
            if verbose:
                print(f"⚠️ Skipping change with no description/title: {ch_fixed}")
            continue

        # If a single 'line' is provided, map it to start/end lines
        if "line" in ch_fixed and (
            "start_line" not in ch_fixed or "end_line" not in ch_fixed
        ):
            try:
                single_line = int(ch_fixed.get("line") or 1)
            except Exception:
                single_line = 1
            ch_fixed["start_line"] = single_line
            ch_fixed["end_line"] = single_line

        # Ensure required fields exist with reasonable defaults
        ch_fixed.setdefault("start_line", 1)
        ch_fixed.setdefault("end_line", ch_fixed.get("start_line", 1))

        # Normalize severity/category strings
        sev = ch_fixed.get("severity")
        if isinstance(sev, str):
            ch_fixed["severity"] = sev.lower()
        cat = ch_fixed.get("category")
        if isinstance(cat, str):
            cat_lower = cat.lower()
            allowed = {c.value for c in Category}
            ch_fixed["category"] = cat_lower if cat_lower in allowed else Category.MAINTAINABILITY.value

        # Required text fields
        ch_fixed.setdefault("title", "Code issue")
        # Enforce max title length (match pydantic constraint ≤ 80)
        try:
            if isinstance(ch_fixed["title"], str) and len(ch_fixed["title"]) > 80:
                ch_fixed["title"] = ch_fixed["title"][0:80]
        except Exception:
            pass
        ch_fixed.setdefault("description", "")
        ch_fixed.setdefault("code_snippet", "")
        ch_fixed.setdefault("suggested_code", "")
        ch_fixed.setdefault("rationale", "")

        # Fill missing suggestion using description/rationale/title heuristics
        if not ch_fixed.get("suggestion"):
            suggestion_source = (
                ch_fixed.get("description")
                or ch_fixed.get("rationale")
                or f"Address: {ch_fixed.get('title', 'issue')}"
            )
            ch_fixed["suggestion"] = suggestion_source

        fixed_changes.append(ch_fixed)
    normalized["changes"] = fixed_changes

    return normalized

from ..bitbucket.client import create_bitbucket_client
from ..core.config import LLMProvider, create_review_config
from ..core.models import (
    Category,
    CodeReviewResult,
    PullRequestDiff,
    ReviewConfig,
    Severity,
)
from ..llm.agent import create_code_review_agent
from ..llm.providers import get_language_model
from .output_formatter import format_review_output


class CodeReviewOrchestrator:
    """Orchestrates the complete code review process."""

    def __init__(
        self,
        workspace: str,
        repo_slug: str,
        pr_id: int,
        config: ReviewConfig,
        bitbucket_token: Optional[str] = None,
        bitbucket_auth_username: Optional[str] = None,
    ):
        """Initialize the review orchestrator.

        Args:
            workspace: Bitbucket workspace
            repo_slug: Repository slug
            pr_id: Pull request ID
            config: Review configuration
            bitbucket_token: Optional Bitbucket API token
            bitbucket_auth_username: Optional Bitbucket username for App Password auth
        """
        self.workspace = workspace
        self.repo_slug = repo_slug
        self.pr_id = pr_id
        self.config = config

        # Initialize clients
        self.bitbucket_client = create_bitbucket_client(
            workspace, bitbucket_token, bitbucket_auth_username, config.verbose
        )
        self.llm = get_language_model(config)
        self._last_pr_diff: Optional[PullRequestDiff] = None

    async def run_review(self) -> CodeReviewResult:
        """Run the complete code review process.

        Returns:
            Structured code review result
        """
        import time
        start_time = time.time()
        
        # Step 1: Get PR diff from Bitbucket
        pr_diff = await self._get_pr_diff()
        self._last_pr_diff = pr_diff

        # Step 1.5: Get previous bot comments
        previous_comments_data = self.bitbucket_client.get_pull_request_comments(
            self.repo_slug, self.pr_id
        )
        print(f"📝 Found {len(previous_comments_data)} previous bot comment(s) from PR #{self.pr_id}")

        # Step 2: Create and run the LLM agent
        agent = create_code_review_agent(
            self.llm, self.config, pr_diff, previous_comments_data
        )
        review_json = await agent.run_review()

        # Step 3: Parse and format the review result
        review_result = self._parse_review_result(review_json)
        
        # Store elapsed time
        elapsed_time = time.time() - start_time
        self._review_elapsed_time = elapsed_time

        return review_result

    def run_review_sync(self) -> CodeReviewResult:
        """Run the complete code review process synchronously.

        Returns:
            Structured code review result
        """
        import time
        start_time = time.time()
        
        # Step 1: Get PR diff from Bitbucket
        pr_diff = self._get_pr_diff_sync()
        self._last_pr_diff = pr_diff

        # Step 1.5: Get previous bot comments
        previous_comments_data = self.bitbucket_client.get_pull_request_comments(
            self.repo_slug, self.pr_id
        )
        print(f"📝 Found {len(previous_comments_data)} previous bot comment(s) from PR #{self.pr_id}")

        # Step 2: Create and run the LLM agent
        agent = create_code_review_agent(
            self.llm, self.config, pr_diff, previous_comments_data
        )
        review_json = agent.run_review_sync()

        # Step 3: Parse and format the review result
        review_result = self._parse_review_result(review_json)
        
        # Store elapsed time
        elapsed_time = time.time() - start_time
        self._review_elapsed_time = elapsed_time

        return review_result

    async def _get_pr_diff(self) -> PullRequestDiff:
        """Get the PR diff from Bitbucket API.

        Returns:
            Pull request diff information
        """
        # First validate the token works for basic operations
        if self.config.verbose:
            print(f"🔍 Validating token for repository: {self.workspace}/{self.repo_slug}")
        if not self.bitbucket_client.validate_token():
            raise ValueError(
                f"Token validation failed for {self.workspace}/{self.repo_slug}. "
                "Please check:\n"
                "1. Token has 'Repositories: Read' permission\n"
                "2. Token is for the correct repository\n"
                "3. Token hasn't expired\n"
                "4. Repository name and workspace are correct"
            )

        print(f"📋 Fetching PR #{self.pr_id} information...")
        return self.bitbucket_client.get_pull_request_diff(self.repo_slug, self.pr_id)

    def _get_pr_diff_sync(self) -> PullRequestDiff:
        """Get the PR diff from Bitbucket API (synchronous).

        Returns:
            Pull request diff information
        """
        return self.bitbucket_client.get_pull_request_diff(self.repo_slug, self.pr_id)


    def _parse_review_result(self, review_json: str) -> CodeReviewResult:
        """Parse the LLM review output into a structured result.

        Args:
            review_json: JSON string from the LLM

        Returns:
            Structured code review result
        """
        # Get working directory for file validation
        working_dir = Path(self.config.working_directory) if self.config.working_directory else None
        
        try:
            review_data = json.loads(review_json)

            # Handle error responses from failed retries
            if "error" in review_data:
                error_msg = review_data["error"]
                print(f"❌ LLM returned error response: {error_msg}")
                return CodeReviewResult(
                    changes=[],
                )

            # Normalize then validate
            normalized = _normalize_review_data(review_data, working_directory=working_dir, verbose=self.config.verbose)
            result = CodeReviewResult(**normalized)
            
            # Check if we actually have meaningful results
            if not result.changes:
                print("ℹ️ No issues found in this review")
            
            return result

        except (json.JSONDecodeError, ValueError, ValidationError) as e:
            # Handle Pydantic validation errors specifically
            if isinstance(e, ValidationError):
                print(f"❌ FATAL: JSON parsing failed after all attempts (agent retries + orchestrator repair)")
                print(f"❌ Error: {str(e)}")
                print("❌ Review cannot be completed - no comments will be posted")
                # Extract missing fields from validation error for better feedback
                missing_fields = []
                if hasattr(e, 'errors'):
                    for error in e.errors():
                        if error.get('type') == 'missing':
                            field_path = '.'.join(str(x) for x in error.get('loc', []))
                            missing_fields.append(field_path)
                if missing_fields:
                    print(f"⚠️ Missing required fields: {', '.join(missing_fields)}")
                return CodeReviewResult(
                    changes=[],
                )
            
            if "column" in str(e) and "line" in str(e):
                try:
                    # Extract error location from the message
                    error_parts = str(e).split("column")[1].split()[0].strip(",")
                    error_col = int(error_parts)
                    start_pos = max(0, error_col - 50)
                    end_pos = min(len(review_json), error_col + 50)
                    context = review_json[start_pos:end_pos]
                    if self.config.verbose:
                        print(f"🔍 JSON parsing failed near: ...{context}...")
                except Exception as parse_error:
                    if self.config.verbose:
                        print(f"❌ Could not extract error location: {parse_error}")

            # Best-effort repair and retry once if this was a JSON decode error
            # This is a FINAL fallback only (retries already happened in agent)
            if isinstance(e, json.JSONDecodeError):
                repaired = _sanitize_llm_json_string(review_json)
                if repaired != review_json:
                    if self.config.verbose:
                        print("🔧 Attempting final JSON repair in orchestrator...")
                    try:
                        review_data = json.loads(repaired)
                        if "error" in review_data:
                            raise ValueError(review_data["error"])
                        normalized = _normalize_review_data(review_data, working_directory=working_dir, verbose=self.config.verbose)
                        return CodeReviewResult(**normalized)
                    except Exception as e2:
                        if self.config.verbose:
                            print(f"❌ Final repair failed: {e2}")

            # Return a basic error result if parsing still fails
            # Do NOT normalize garbage data - return clean empty result
            print("❌ FATAL: JSON parsing failed after all attempts (agent retries + orchestrator repair)")
            print(f"❌ Error: {str(e)}")
            print("❌ Review cannot be completed - no comments will be posted")
            return CodeReviewResult(
                changes=[],
            )

    async def submit_review_comments(self, review_result: CodeReviewResult) -> None:
        """Submit review comments to Bitbucket.

        Args:
            review_result: The review result to submit
        """
        # Format the review for Bitbucket comments
        comments = format_review_output(review_result)
        
        # Determine changed lines per file to prevent commenting on unchanged code
        # Prefer last fetched diff; otherwise fetch now
        pr_diff = self._last_pr_diff or self._get_pr_diff_sync()
        changed_map = get_changed_lines_by_file(pr_diff.diff_content)
        
        # Fetch existing comments to prevent duplicates
        previous_comments = self.bitbucket_client.get_pull_request_comments(
            self.repo_slug, self.pr_id
        )
        
        if not comments:
            existing_count = len(previous_comments)
            if existing_count > 0:
                print(f"✅ No new issues found")
                print(f"   All concerns already addressed by {existing_count} existing comment(s)")
            else:
                print("✅ No issues found in this review")
            return
        # Build a set of (file_path, line) tuples for existing comments
        existing_comment_locations = {
            (c.get("file_path"), c.get("line"))
            for c in previous_comments
            if c.get("file_path") and c.get("line")
        }
        if self.config.verbose:
            print(f"🔍 Found {len(existing_comment_locations)} existing comment location(s) to avoid")

        for comment in comments:
            path = comment.get("file_path")
            start = comment.get("line")
            end = comment.get("line")
            anchor_snippet = (comment.get("anchor_snippet") or "").strip()
            
            # Skip if there's already a comment on this file + line
            if path and start and (path, int(start)) in existing_comment_locations:
                print(f"⏭️ Skipping duplicate comment (already exists): {path}:{start}")
                continue

            # Determine anchors based on lines visible in the diff
            anchor_to: Optional[int] = None
            file_changed = changed_map.get(path, set()) if path else set()
            if path and file_changed:
                s = int(start) if start is not None else None

                sorted_changed = sorted(file_changed)

                def _nearest(target: int) -> int:
                    return min(
                        sorted_changed, key=lambda ln: (abs(ln - target), ln)
                    )

                if anchor_snippet:
                    # Try to locate the snippet text within the new-file context by scanning the diff
                    # Fallback to nearest line if not found
                    try:
                        best_line = None
                        best_distance = None
                        # Build a quick map of line→context presence by scanning the diff text for the file
                        # We approximate by choosing the first changed/context line where the snippet's
                        # prefix appears in surrounding context (not perfect, but better than random).
                        file_lines = sorted_changed
                        for ln in file_lines:
                            # Prefer exact line hint first
                            if s is not None and ln == s:
                                best_line = ln
                                break
                            # Otherwise compute distance to hinted line
                            if s is not None:
                                dist = abs(ln - s)
                            else:
                                dist = 0
                            if best_distance is None or dist < best_distance:
                                best_distance = dist
                                best_line = ln
                        anchor_to = best_line
                    except Exception:
                        anchor_to = sorted_changed[0]
                elif s is not None:
                    # Single-line anchor near requested start
                    # First, check if the requested line is actually in the diff
                    if s in file_changed:
                        anchor_to = s
                    else:
                        anchor_to = _nearest(s)
                        # Check if anchor is too far from requested line
                        if abs(anchor_to - s) > 20:
                            print(f"⏭️ ❌ Skipping comment: LLM tried to comment on line {s}, but it's not in the diff")
                            print(f"   File: {path}")
                            print(f"   Changed lines in diff: {sorted(file_changed)[:10]}{'...' if len(file_changed) > 10 else ''}")
                            print(f"   Nearest changed line is {anchor_to} ({abs(anchor_to - s)} lines away - too far)")
                            print(f"   💡 Hint: Only comment on lines with '+' prefix (added/modified lines in the diff)")
                            continue
                else:
                    # No hint provided; choose the first visible line
                    anchor_to = sorted_changed[0]

            if path and anchor_to is None:
                print(f"⏭️ ❌ Skipping comment: No anchorable changed line found in diff")
                print(f"   File: {path}, Requested lines: {start}-{end}")
                print(f"   💡 Hint: The file may not have any changed lines in the diff")
                continue

            try:
                content = comment["content"]
                if self.config.verbose:
                    print(
                        "📝 Posting comment: "
                        f"path={path} requested_line={start} anchor_to={anchor_to} content_len={len(content)}"
                    )
                    print(f"   Changed lines in file: {sorted(file_changed) if file_changed else 'NONE'}")
                    print(f"   Content preview: {content[:100]}")
                response = self.bitbucket_client.add_pull_request_comment(
                    repo_slug=self.repo_slug,
                    pr_id=self.pr_id,
                    content=content,
                    file_path=path,
                    line=int(anchor_to) if anchor_to is not None else None,
                    from_line=None,
                    to_line=None,
                )
                
                # Check if inline anchor actually worked
                response_inline = response.get("inline", {})
                context_lines = response_inline.get("context_lines", "")
                if path and anchor_to is not None and not context_lines:
                    # Inline anchor failed - Bitbucket accepted it but couldn't anchor to diff
                    comment_id = response.get("id")
                    print(f"⚠️ ❌ Inline comment failed to anchor to diff!")
                    print(f"   File: {path}, Line: {anchor_to}")
                    print(f"   Bitbucket response shows empty 'context_lines' - line not visible in diff")
                    print(f"   Changed lines in file: {sorted(file_changed)[:10]}{'...' if len(file_changed) > 10 else ''}")
                    print(f"   💡 Line must have '+' prefix (only added/modified lines can be commented on)")
                    if self.config.verbose:
                        print(f"   Full response inline object: {response_inline}")
                    # Delete the orphaned comment
                    if comment_id:
                        try:
                            delete_url = f"{self.bitbucket_client.BASE_URL}/repositories/{self.bitbucket_client.workspace}/{self.repo_slug}/pullrequests/{self.pr_id}/comments/{comment_id}"
                            self.bitbucket_client._make_request("DELETE", delete_url)
                            print(f"   🗑️ Deleted orphaned comment (ID: {comment_id})")
                        except Exception as del_err:
                            print(f"   ⚠️ Failed to delete orphaned comment: {del_err}")
                    continue
                
                location = (
                    f"{path}:{anchor_to}" if path and anchor_to is not None else "general"
                )
                print(f"✅ Posted comment ({location})")
            except Exception as e:
                print(f"❌ Failed to post comment: {e}")


def create_review_orchestrator(
    workspace: str,
    repo_slug: str,
    pr_id: int,
    llm_provider: Optional[LLMProvider] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    bitbucket_token: Optional[str] = None,
    bitbucket_auth_username: Optional[str] = None,
    working_directory: Optional[str] = None,
    max_iterations: Optional[int] = None,
    verbose: bool = False,
) -> CodeReviewOrchestrator:
    """Create a review orchestrator with the specified configuration.

    Args:
        workspace: Bitbucket workspace
        repo_slug: Repository slug
        pr_id: Pull request ID
        llm_provider: LLM provider to use
        model_name: Model name to use
        temperature: Temperature for LLM
        bitbucket_token: Bitbucket API token
        bitbucket_auth_username: Optional Bitbucket username for App Password auth
        working_directory: Working directory for repo operations
        verbose: Enable verbose debug output

    Returns:
        Configured review orchestrator
    """
    config = create_review_config(
        llm_provider=llm_provider,
        model_name=model_name,
        temperature=temperature,
        working_directory=working_directory,
        max_tool_iterations=max_iterations,
        verbose=verbose,
    )

    return CodeReviewOrchestrator(
        workspace=workspace,
        repo_slug=repo_slug,
        pr_id=pr_id,
        config=config,
        bitbucket_token=bitbucket_token,
        bitbucket_auth_username=bitbucket_auth_username,
    )
