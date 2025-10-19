"""Tool for LLM to submit the final code review JSON."""

import json
from typing import Any
from pydantic import ValidationError
from langchain_core.tools import tool

from ...core.models import CodeReviewResult
from ..callbacks import LLMTimingCallback


# Global to store the validated review result
_submitted_review: CodeReviewResult | None = None


def get_submitted_review() -> CodeReviewResult | None:
    """Get the most recently submitted and validated review."""
    return _submitted_review


def reset_submitted_review() -> None:
    """Reset the submitted review (call before each review session)."""
    global _submitted_review
    _submitted_review = None


@tool
def submit_review(review_json: str) -> str:
    """Submit your final code review as JSON. This will validate the JSON structure.
    
    Call this tool when you've completed your investigation and are ready to submit findings.
    
    The JSON MUST have this EXACT structure with ALL required fields:
    - summary (string)
    - severity_counts (object with critical/major/minor/info counts)
    - changes (array of issue objects - each MUST have ALL 11 fields)
    - positives (array of objects with description field)
    - recommendations (array of strings)
    
    Each change object MUST include ALL 11 fields:
    file_path, start_line, end_line, severity, category, title, description, 
    suggestion, code_snippet, suggested_code, rationale
    
    If validation fails, you'll get an error message - fix the JSON and call submit_review again!
    
    Args:
        review_json: Complete review as valid JSON string (no markdown, no explanations)
        
    Returns:
        Success message or detailed validation error
    """
    global _submitted_review
    
    try:
        # Parse JSON
        review_data = json.loads(review_json)
        
        # Validate with Pydantic
        result = CodeReviewResult(**review_data)
        
        # Check for placeholder line numbers
        bad_line_issues = []
        for idx, change in enumerate(result.changes):
            # Flag obviously wrong line numbers
            if (change.start_line == 1 and change.end_line >= 9000) or change.start_line == 0:
                bad_line_issues.append(
                    f"  - Change #{idx+1} ({change.file_path}): line {change.start_line}-{change.end_line} looks like a placeholder"
                )
        
        # Count how many issues are at line 1 (if > 50% of issues, likely lazy)
        line_1_count = sum(1 for c in result.changes if c.start_line == 1)
        if line_1_count > len(result.changes) * 0.5 and len(result.changes) > 2:
            bad_line_issues.append(
                f"  - {line_1_count} out of {len(result.changes)} issues at line 1 - use ACTUAL line numbers!"
            )
        
        if bad_line_issues:
            error_msg = (
                f"❌ Validation errors:\n"
                f"  - Line numbers must be ACTUAL line numbers from the file, not placeholders\n"
                f"  - DO NOT use line 1 or 9999 unless that's truly where the issue is\n"
                f"\nIssues with suspicious line numbers:\n" + "\n".join(bad_line_issues) +
                f"\n\nPlease re-read the files to find the EXACT line numbers where these issues occur."
            )
            print(f"🛠️ submit_review: ❌ Validation failed (placeholder line numbers)")
            return error_msg
        
        # Store the validated result
        _submitted_review = result
        
        change_count = len(result.changes)
        timing = LLMTimingCallback.get_and_clear_timing()
        print(f"🛠️ submit_review: ✅ Review validated! Found {change_count} issue(s). {timing}")
        
        return f"✅ SUCCESS! Review validated and submitted with {change_count} issue(s). Your work is complete."
        
    except json.JSONDecodeError as e:
        error_msg = f"❌ JSON parsing error: {str(e)}"
        if hasattr(e, 'lineno') and hasattr(e, 'colno'):
            error_msg += f" at line {e.lineno}, column {e.colno}"
        print(f"🛠️ submit_review: ❌ JSON parsing failed - {error_msg}")
        return f"{error_msg}\n\nFix the JSON syntax and call submit_review() again with corrected JSON."
        
    except ValidationError as e:
        # Extract detailed field errors
        errors = []
        title_too_long = False
        for error in e.errors():
            field_path = '.'.join(str(x) for x in error.get('loc', []))
            error_type = error.get('type', 'unknown')
            msg = error.get('msg', 'validation failed')
            errors.append(f"  - {field_path}: {msg} (type: {error_type})")
            
            # Check if this is a title length error
            if 'title' in field_path and 'string_too_long' in error_type:
                title_too_long = True
        
        error_msg = "❌ Validation errors:\n" + "\n".join(errors)
        print(f"🛠️ submit_review: ❌ Schema validation failed ({len(errors)} error(s))")
        print(error_msg)  # Print detailed errors to STDOUT
        
        tips = "\nMost common issues:\n- Missing required field (add ALL 11 fields to each change)\n- Wrong field name (use 'file_path' not 'file', 'category' not 'type')\n- Wrong data type (severity_counts values must be integers)\n"
        
        if title_too_long:
            tips += "\n🚨 TITLE TOO LONG! Keep titles ≤ 80 characters:\n- BAD: 'The code replaces len() with aggregation query but indexing may fail'\n- GOOD: 'Aggregation count indexing lacks safety checks'\n- Think SHORT newspaper headline!\n"
        
        return f"{error_msg}{tips}\nFix the errors and call submit_review() again."
        
    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        print(f"🛠️ submit_review: ❌ Unexpected error - {error_msg}")
        return f"{error_msg}\n\nCheck your JSON structure and try again."

