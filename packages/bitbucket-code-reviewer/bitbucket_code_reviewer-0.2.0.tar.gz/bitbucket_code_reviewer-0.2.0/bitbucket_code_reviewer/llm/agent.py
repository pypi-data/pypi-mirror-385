"""LangChain agent for code review with tool-calling capabilities."""

import json
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..core.models import PullRequestDiff, ReviewConfig
from ..prompts import get_system_prompt
from .tools import create_code_review_tools
from .callbacks import LLMTimingCallback


class CodeReviewAgent:
    """LangChain agent for performing code reviews."""

    def __init__(
        self,
        llm: BaseLanguageModel,
        config: ReviewConfig,
        pr_diff: PullRequestDiff,
        previous_comments: list = None,
    ):
        """Initialize the code review agent.

        Args:
            llm: Configured language model
            config: Review configuration
            pr_diff: Pull request diff information
            previous_comments: List of previous bot comments on this PR
        """
        self.llm = llm
        self.config = config
        self.pr_diff = pr_diff
        self.previous_comments = previous_comments or []

        # Create tools with working directory and PR diff
        self.tools = create_code_review_tools(config.working_directory, pr_diff)

        # Create the agent
        self.agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with tools.

        Returns:
            Configured agent executor
        """
        try:
            # Get the system prompt
            system_prompt = get_system_prompt(language=self.config.language)
            
            # Escape curly braces in system prompt for ChatPromptTemplate
            # (it interprets { } as template variables, but our prompt has JSON examples)
            escaped_system_prompt = system_prompt.replace("{", "{{").replace("}", "}}")

            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", escaped_system_prompt),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
        except Exception as e:
            print(f"❌ ERROR during agent creation: {str(e)}")
            raise

        # Attach per-LLM roundtrip timing via callback
        try:
            provider_name = getattr(self.config.llm_provider, "value", str(self.config.llm_provider))
            timing_callback = LLMTimingCallback(
                provider_name=provider_name,
                model_name=self.config.model_name,
            )
            instrumented_llm = self.llm.with_config(callbacks=[timing_callback])
        except Exception:
            # Fall back gracefully to the raw LLM if instrumentation fails
            instrumented_llm = self.llm

        # Create the agent
        agent = create_openai_tools_agent(
            llm=instrumented_llm,
            tools=self.tools,
            prompt=prompt,
        )

        # Create the agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,  # Disable verbose output
            max_iterations=self.config.max_tool_iterations,
            handle_parsing_errors=True,
        )

    def _create_initial_message(self) -> str:
        """Create the initial human message with PR context.

        Returns:
            Initial message for the agent
        """
        pr_info = self.pr_diff.pull_request

        message_parts = [
            "Please review this pull request:",
            f"Title: {pr_info.title}",
            f"Author: {pr_info.author}",
            f"Source Branch: {pr_info.source_branch}",
            f"Target Branch: {pr_info.target_branch}",
            "",
            "Files changed:",
        ]

        for file_change in self.pr_diff.files:
            status_emoji = {
                "added": "➕",
                "modified": "✏️",
                "removed": "➖",
                "renamed": "📝",
            }.get(file_change.status, "❓")

            message_parts.append(
                f"{status_emoji} {file_change.filename} "
                f"(+{file_change.additions}, -{file_change.deletions})"
            )

        # Add previous comments section if any exist
        if self.previous_comments:
            message_parts.extend(
                [
                    "",
                    "=" * 60,
                    "PREVIOUS COMMENTS ON THIS PR (ALL AUTHORS):",
                    "=" * 60,
                ]
            )
            
            for comment in self.previous_comments:
                comment_location = "General comment"
                if comment.get("file_path"):
                    location_str = comment["file_path"]
                    if comment.get("line"):
                        location_str += f":{comment['line']}"
                    comment_location = f"Inline comment at {location_str}"
                
                author = comment.get("author", "Unknown")
                message_parts.extend(
                    [
                        f"• {comment_location}",
                        f"  Author: {author}",
                        f"  Created: {comment.get('created_date', 'Unknown')}",
                        f"  Content: {comment.get('content', '')[:200]}...",
                        "",
                    ]
                )
            
            message_parts.extend(
                [
                    "=" * 60,
                    "🚨 CRITICAL: DUPLICATE PREVENTION 🚨",
                    "",
                    "These issues have ALREADY been commented on!",
                    "",
                    "MANDATORY WORKFLOW STEP:",
                    "BEFORE you submit your review with submit_review(), you MUST:",
                    "",
                    "1. List out each issue you plan to report",
                    "2. For EACH issue, check if it's a SEMANTIC DUPLICATE:",
                    "",
                    "🔍 A comment is a DUPLICATE if:",
                    "   ✓ Same CODE REGION (~5 lines, not exact line match)",
                    "   ✓ Same UNDERLYING ISSUE (same root cause)",
                    "   ✓ Developer would fix BOTH by making ONE change",
                    "",
                    "🎯 THE DECISIVE TEST:",
                    "Ask yourself: \"If the developer adds ONE code change (e.g., ONE try/except block,",
                    "ONE validation check, ONE null check), would that fix BOTH the existing comment",
                    "AND my issue?\"",
                    "   → If YES = DUPLICATE, skip it!",
                    "   → If NO = DIFFERENT, include it!",
                    "",
                    "3. If it's a semantic duplicate → SKIP IT COMPLETELY",
                    "4. Only submit issues that are genuinely NEW and distinct",
                    "",
                    "📚 Examples of DUPLICATES (DO NOT SUBMIT):",
                    "",
                    "❌ DUPLICATE Example 1 (indexing vs exception - SAME FIX):",
                    "   Existing: 'Line 194: Aggregation indexing assumes [0][0] structure'",
                    "   Your plan: 'Line 195: Firestore .get() can raise network exceptions'",
                    "   TEST: Would ONE try/except around lines 194-196 fix both?",
                    "   → YES! Same fix: wrap in try/except",
                    "   → DUPLICATE! SKIP YOUR ISSUE!",
                    "",
                    "❌ DUPLICATE Example 2 (different wording, same issue):",
                    "   Existing: 'Line 194: Missing error handling for count aggregation'",
                    "   Your plan: 'Line 195: No try/except for count().get() call'",
                    "   TEST: Would ONE try/except fix both?",
                    "   → YES! Same code block, same fix",
                    "   → DUPLICATE! SKIP YOUR ISSUE!",
                    "",
                    "❌ DUPLICATE Example 3 (API errors):",
                    "   Existing: 'Lines 50-60: Missing try/except for API call'",
                    "   Your plan: 'Line 55: API request can timeout'",
                    "   TEST: Would ONE try/except fix both?",
                    "   → YES! Same error handling block",
                    "   → DUPLICATE! SKIP YOUR ISSUE!",
                    "",
                    "📚 Examples of NOT DUPLICATES (OK to submit):",
                    "",
                    "✅ NOT DUPLICATE Example 1 (separate concerns):",
                    "   Existing: 'Line 194: Aggregation count needs error handling'",
                    "   Your plan: 'Line 220: Pagination query needs error handling'",
                    "   TEST: Would ONE try/except fix both?",
                    "   → NO! Different code sections, need separate try/except blocks",
                    "   → NOT DUPLICATE! OK to include!",
                    "",
                    "✅ NOT DUPLICATE Example 2 (different types of issues):",
                    "   Existing: 'Line 60: Missing input validation for email'",
                    "   Your plan: 'Line 65: SQL injection risk in query parameter'",
                    "   TEST: Would ONE code change fix both?",
                    "   → NO! Validation vs query parameterization are different fixes",
                    "   → NOT DUPLICATE! OK to include!",
                    "",
                    "✅ NOT DUPLICATE Example 3 (error handling vs performance):",
                    "   Existing: 'Line 194: Count aggregation lacks try/except'",
                    "   Your plan: 'Line 250: Streaming query is inefficient (N+1 problem)'",
                    "   TEST: Would ONE code change fix both?",
                    "   → NO! Error handling vs performance optimization are different",
                    "   → NOT DUPLICATE! OK to include!",
                    "",
                    "⚠️ CRITICAL DECISION RULE:",
                    "Would ONE code change (one try/except, one check, one fix) solve BOTH issues?",
                    "   → If YES = DUPLICATE, SKIP IT!",
                    "   → If NO = DIFFERENT, include it!",
                    "",
                    "✅ ZERO ISSUES IS OKAY:",
                    "If all your findings are semantic duplicates, submit with empty 'changes' array!",
                    "That shows you're correctly avoiding duplicates, not that you failed to review.",
                    "=" * 60,
                    "",
                ]
            )

        # Add explicit file path reminder
        file_paths = [f.filename for f in self.pr_diff.files]
        message_parts.extend(
            [
                "",
                "=" * 60,
                "⚠️  VALID FILE PATHS FOR THIS REVIEW (use ONLY these):",
                "=" * 60,
            ]
        )
        for fp in file_paths:
            message_parts.append(f"  - {fp}")
        
        message_parts.extend(
            [
                "=" * 60,
                "",
                "CRITICAL RULES:",
                "1. You MUST ONLY use file paths from the list above",
                "2. COPY the exact file path - do NOT invent variations",
                "3. If you use a file path NOT in the list above, your comment will be REJECTED",
                "",
                "IMPORTANT: Respond ONLY with valid JSON. Use EXACT field names as shown:",
                "",
                "🚨 YOU ARE A CODE CRITIC, NOT A NARRATOR! 🚨",
                "DO NOT create 'changes' to describe what the developer did!",
                "ONLY create 'changes' for ACTUAL PROBLEMS in the new code!",
                "",
                "Examples of what NOT to report as 'changes':",
                "❌ 'A typo was fixed' - That's GOOD! Put in positives!",
                "❌ 'A constant was added' - That's just describing! Put in positives if it's good!",
                "❌ 'Docstring was added' - That's an improvement! Put in positives!",
                "❌ 'Tests were updated' - That's expected! Put in positives if done well!",
                "",
                "Required top-level fields:",
                "- summary: string describing overall code quality",
                "- severity_counts: object with integer counts {critical: 0, major: 0, minor: 0, info: 0}",
                "- changes: array of PROBLEMS/ISSUES in new code (NOT descriptions of what changed!)",
                "- positives: array of {description: string} objects (for good changes/fixes)",
                "- recommendations: array of strings (for overall suggestions)",
                "",
                "Each change object MUST have ALL these EXACT field names (ALL REQUIRED, NO OPTIONAL FIELDS):",
                "- file_path (string) ✅ REQUIRED - exact match from 'Files changed' list",
                "- start_line (number) ✅ REQUIRED",
                "- end_line (number) ✅ REQUIRED", 
                "- severity (string) ✅ REQUIRED - one of: 'critical'|'major'|'minor'|'info'",
                "- category (string) ✅ REQUIRED - one of: 'security'|'performance'|'maintainability'|'architecture'|'style'",
                "- title (string) ✅ REQUIRED - ⚠️⚠️ MAX 80 CHARACTERS! Keep it SHORT! ⚠️⚠️",
                "- description (string) ✅ REQUIRED - detailed explanation",
                "- suggestion (string) ✅ REQUIRED - how to fix",
                "- code_snippet (string) ✅ REQUIRED - problematic code (can be empty string if not applicable)",
                "- suggested_code (string) ✅ REQUIRED - improved code (can be empty string if not applicable)",
                "- rationale (string) ✅ REQUIRED - why this improves the code",
                "",
                "⚠️ EVERY change object MUST include ALL 11 fields above. Missing ANY field will cause validation to fail!",
                "",
                "🚨🚨🚨 CRITICAL: TITLE FIELD MUST BE ≤ 80 CHARACTERS! 🚨🚨🚨",
                "- BAD (82 chars):  'The aggregation count query result indexing may fail if response structure changes'",
                "- GOOD (54 chars): 'Aggregation count indexing lacks error handling'",
                "- Think: SHORT newspaper headline, NOT a full sentence with explanation!",
                "- ALWAYS count characters before submitting! This error happens CONSTANTLY!",
                "",
                "📋 EXAMPLE CHANGE OBJECT (copy this structure EXACTLY):",
                "```json",
                "{",
                '  "file_path": "src/api/auth.py",  // NOT "file" or "path"',
                '  "start_line": 42,  // ⚠️ MUST be ACTUAL line number where issue starts',
                '  "end_line": 45,    // ⚠️ MUST be ACTUAL line number where issue ends',
                '  "severity": "major",',
                '  "category": "security",  // NOT "type" or "issue_type"',
                '  "title": "Missing input validation",  // ⚠️ MAX 80 CHARS! (this is 27)',
                '  "description": "The login function accepts user input without validation...",',
                '  "suggestion": "Add schema validation using Pydantic...",',
                '  "code_snippet": "def login(data): user = db.get(data[id])",',
                '  "suggested_code": "def login(data: LoginRequest): user = db.get(data.id)",',
                '  "rationale": "Schema validation prevents injection attacks and improves type safety"',
                "}",
                "```",
                "",
                "🎯 LINE NUMBER REQUIREMENTS:",
                "- start_line and end_line MUST be the ACTUAL line numbers where the issue exists",
                "- DO NOT use 1, 0, or 9999 as placeholder line numbers",
                "- If you can't find the exact line, re-read the file to locate it",
                "- Line numbers are critical for developers to find issues quickly",
                "",
                "=" * 60,
                "⚠️⚠️⚠️ CRITICAL: VALID FILE PATHS (copy EXACTLY) ⚠️⚠️⚠️",
                "=" * 60,
            ]
        )
        for fp in file_paths:
            message_parts.append(f"✓ {fp}")
        
        message_parts.extend(
            [
                "=" * 60,
                "",
                "Do NOT use alternative field names like 'message', 'proposed_fix', or 'fix'.",
                "Do NOT include markdown code blocks, explanations, or text outside the JSON structure.",
                "Do NOT invent file paths - use ONLY the paths marked with ✓ above.",
                "If you find an issue but are unsure which file, SKIP that issue rather than guessing the path.",
                "",
                "🎯 WORKFLOW REQUIREMENT:",
                "1. Call think() IMMEDIATELY to share your plan (1-2 sentences max)",
                "2. Call think() AFTER reading each file with brief findings (~80 chars)",
                "3. Call think() when discovering issues with quick notes",
                "4. Call think() BEFORE submitting with brief conclusions",
                "5. When ready, call submit_review(json_string) with your complete review JSON",
                "6. If submit_review() returns errors, FIX the JSON and call submit_review() again",
                "7. Keep think() calls SHORT - minimum 5 times, no paragraphs!",
                "",
                "⚠️ CRITICAL: When you're done investigating, call submit_review() tool with the JSON.",
                "Do NOT return JSON as your response - use the submit_review() TOOL!",
                "The tool will validate your JSON and tell you if there are errors to fix.",
                "",
                "Focus on changed files. If strictly necessary to validate correctness (imports/config), you may read up to 2 non-diff files; keep it minimal and explain why.",
            ]
        )

        return "\n".join(message_parts)

    def _sanitize_json_string(self, raw: str) -> str:
        """Best-effort repair of common JSON issues from LLM output.
        
        Args:
            raw: Raw JSON string from LLM
            
        Returns:
            Cleaned JSON string
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
        
        return cleaned

    def _validate_json(self, json_string: str) -> tuple[bool, str, str]:
        """Validate JSON and return error details if invalid.
        
        Args:
            json_string: JSON string to validate
            
        Returns:
            Tuple of (is_valid, error_message, error_context)
        """
        try:
            cleaned = self._sanitize_json_string(json_string)
            parsed = json.loads(cleaned)
            
            # Validate required structure
            if "changes" not in parsed:
                return False, "Missing required field 'changes'", ""
            if not isinstance(parsed["changes"], list):
                return False, "Field 'changes' must be a list", ""
            
            return True, "", ""
            
        except json.JSONDecodeError as e:
            # Extract context around the error
            error_pos = e.pos
            context_start = max(0, error_pos - 100)
            context_end = min(len(json_string), error_pos + 100)
            error_context = json_string[context_start:context_end]
            
            error_message = f"JSON parsing error: {e.msg} (line {e.lineno}, column {e.colno})"
            return False, error_message, error_context
            
        except Exception as e:
            return False, f"JSON validation error: {str(e)}", ""

    def _create_retry_feedback(self, error_message: str, error_context: str) -> str:
        """Create feedback message for LLM when JSON parsing fails.
        
        Args:
            error_message: Description of the JSON error
            error_context: Text context around the error
            
        Returns:
            Feedback message for the LLM
        """
        feedback_parts = [
            "❌ JSON PARSING ERROR DETECTED",
            "",
            f"Error: {error_message}",
            "",
        ]
        
        if error_context:
            feedback_parts.extend([
                "Context around error:",
                "```",
                f"...{error_context}...",
                "```",
                "",
            ])
        
        # Add file path reminder to prevent hallucination
        file_paths = [f.filename for f in self.pr_diff.files]
        
        feedback_parts.extend([
            "⚠️ CRITICAL: Your previous attempt had a JSON formatting error, NOT a content error.",
            "",
            "DO NOT re-investigate or make up new issues!",
            "DO NOT call any tools (think, read_file, etc.) - you already did the investigation.",
            "DO NOT invent file paths - use ONLY the paths from this PR:",
            "",
        ])
        
        for fp in file_paths:
            feedback_parts.append(f"  ✓ {fp}")
        
        feedback_parts.extend([
            "",
            "YOUR TASK:",
            "1. Take the SAME findings you already discovered in your investigation",
            "2. Format them as valid JSON with proper escaping",
            "3. Use ONLY the file paths marked with ✓ above",
            "4. Use the EXACT field names specified (NOT alternatives)",
            "",
            "⚠️ COMMON MISTAKES TO AVOID:",
            '- ❌ DON\'T use "file" - use "file_path"',
            '- ❌ DON\'T use "type" or "issue_type" - use "category"',
            '- ❌ DON\'T use "message" - use "description"',
            '- ❌ DON\'T use "proposed_fix" - use "suggestion"',
            "- ❌ DON'T omit ANY of the 11 required fields",
            "- ❌ DON'T make title longer than 80 characters (keep it SHORT!)",
            "",
            "✅ REQUIRED FIELDS (ALL 11 in EVERY change object):",
            "file_path, start_line, end_line, severity, category, title, description, suggestion, code_snippet, suggested_code, rationale",
            "",
            "Requirements for the JSON:",
            "- All strings must be properly escaped (especially quotes, newlines, backslashes)",
            "- All brackets and braces must be balanced",
            "- No trailing commas in arrays or objects",
            "- Valid JSON structure throughout",
            "- Use ONLY file paths from the ✓ list above",
            "",
            "Generate the corrected JSON now (ONLY valid JSON, no markdown or explanations):",
        ])
        
        return "\n".join(feedback_parts)

    async def run_review(self) -> str:
        """Run the code review process using submit_review tool.

        Returns:
            Review result as JSON string from submit_review tool, or error
        """
        from .tools import reset_submitted_review, get_submitted_review
        
        try:
            # Reset any previous submission
            reset_submitted_review()
            
            # Create initial message and invoke agent
            initial_message = self._create_initial_message()
            result = await self.agent_executor.ainvoke({"input": initial_message})
            
            # Debug: print what the agent's final output was
            agent_output = result.get('output', 'No output')
            print(f"🔍 AGENT FINAL OUTPUT: {agent_output[:500]}")  # First 500 chars
            
            # Check if submit_review() was called successfully
            submitted = get_submitted_review()
            if submitted:
                # Success! Convert back to JSON string for compatibility
                return submitted.model_dump_json()
            else:
                # Agent didn't call submit_review() - this shouldn't happen
                print("⚠️ WARNING: Agent completed without calling submit_review() tool!")
                return '{"error": "Agent did not submit review using submit_review() tool"}'
            
        except Exception as e:
            return f'{{"error": "Review failed: {str(e)}"}}'

    def run_review_sync(self) -> str:
        """Run the code review process synchronously using submit_review tool.

        Returns:
            Review result as JSON string from submit_review tool, or error
        """
        from .tools import reset_submitted_review, get_submitted_review
        
        try:
            # Reset any previous submission
            reset_submitted_review()
            
            # Create initial message and invoke agent
            initial_message = self._create_initial_message()
            result = self.agent_executor.invoke({"input": initial_message})
            
            # Debug: print what the agent's final output was
            agent_output = result.get('output', 'No output')
            print(f"🔍 AGENT FINAL OUTPUT: {agent_output[:500]}")  # First 500 chars
            
            # Check if submit_review() was called successfully
            submitted = get_submitted_review()
            if submitted:
                # Success! Convert back to JSON string for compatibility
                return submitted.model_dump_json()
            else:
                # Agent didn't call submit_review() - this shouldn't happen
                print("⚠️ WARNING: Agent completed without calling submit_review() tool!")
                return '{"error": "Agent did not submit review using submit_review() tool"}'
            
        except Exception as e:
            error_msg = f'{{"error": "Review failed: {str(e)}"}}'
            print(f"❌ LLM ERROR: {str(e)}")
            return error_msg


def create_code_review_agent(
    llm: BaseLanguageModel,
    config: ReviewConfig,
    pr_diff: PullRequestDiff,
    previous_comments: list = None,
) -> CodeReviewAgent:
    """Create a code review agent instance.

    Args:
        llm: Configured language model
        config: Review configuration
        pr_diff: Pull request diff information
        previous_comments: List of previous bot comments on this PR

    Returns:
        Configured code review agent
    """
    return CodeReviewAgent(llm, config, pr_diff, previous_comments)
