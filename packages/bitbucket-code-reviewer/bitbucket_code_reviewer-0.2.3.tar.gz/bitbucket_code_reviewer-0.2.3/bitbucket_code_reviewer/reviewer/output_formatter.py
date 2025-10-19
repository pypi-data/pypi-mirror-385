"""Format code review results for Bitbucket PR comments."""

from typing import Any

from ..core.models import CodeReviewResult, Severity


def format_review_output(review_result: CodeReviewResult) -> list[dict[str, Any]]:
    """Format a code review result into Bitbucket PR comments.

    Creates ONE inline comment per issue (change):
    - First line: brief description of the issue (plain text)
    - Then: "Proposed fix:" followed by either a short suggestion (text) or a fenced
      code snippet with the proposed change when available.
    """
    comments: list[dict[str, Any]] = []

    for change in review_result.changes:
        change_comment = _format_change_comment(change)
        comments.append(change_comment)

    return comments




def _looks_like_code(text: str) -> bool:
    """Heuristic to decide if a string is code-like for fencing."""
    if not text:
        return False
    indicators = [
        "\n",
        "def ",
        "class ",
        "import ",
        "from ",
        "return ",
        "=",
        "{",
        "}",
        "(",
        ")",
        ":",
        ";",
    ]
    lowered = text.strip().lower()
    return any(tok in text for tok in indicators) or lowered.startswith(("#", "//"))


def _format_change_comment(change) -> dict[str, Any]:
    """Format a code change as a single inline suggested-change comment."""
    # Get severity and format as emoji + label
    severity = getattr(change, "severity", "info")
    severity_emoji = {
        "critical": "🚨",
        "major": "⚠️",
        "minor": "ℹ️",
        "info": "💡",
    }.get(severity.lower(), "ℹ️")
    severity_label = severity.upper()
    
    description_text = (
        change.description.strip() if hasattr(change, "description") else "Issue"
    )
    suggestion_text = (getattr(change, "suggestion", "") or "").strip()
    proposed_code = (getattr(change, "suggested_code", "") or "").strip()

    lines: list[str] = [
        f"{severity_emoji} **{severity_label}**",
        "",
        description_text,
        "",
        "Proposed fix:"
    ]
    if proposed_code and _looks_like_code(proposed_code):
        # Prefer a code block only if it looks like code
        lines += ["```", proposed_code, "```"]
    elif suggestion_text:
        lines.append(suggestion_text)
    else:
        lines.append("(see diff)")

    # Prefer single-line anchoring; rely on orchestrator to snap to diff
    anchor_line = getattr(change, "line", None)
    if anchor_line is None:
        anchor_line = getattr(change, "start_line", None)

    # Provide an anchor snippet derived from the first line of code_snippet
    anchor_snippet = None
    if proposed_code:
        # If proposed_code provided, it often reflects the desired change, not current line
        pass
    code_snip = (getattr(change, "code_snippet", "") or "").strip()
    if code_snip:
        first_line = code_snip.splitlines()[0].strip()
        if first_line:
            anchor_snippet = first_line[:160]
    return {
        "content": "\n".join(lines),
        "file_path": change.file_path,
        "line": anchor_line,
        "anchor_snippet": anchor_snippet,
    }




