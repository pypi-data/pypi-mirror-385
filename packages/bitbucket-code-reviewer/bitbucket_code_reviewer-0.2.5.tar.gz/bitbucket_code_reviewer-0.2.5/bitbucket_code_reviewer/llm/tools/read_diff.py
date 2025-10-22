"""Tool for reading PR diffs with context."""

from langchain.tools import tool

from ._shared import get_working_directory
from ..callbacks import LLMTimingCallback


@tool
def read_diff(file_path: str) -> str:
    """Read only the CHANGED portions of a file from the PR diff.
    
    This tool shows you EXACTLY what changed in this PR for the given file,
    including generous surrounding context (10-15 lines before/after changes).
    
    **THIS SHOULD BE YOUR PRIMARY TOOL** for reviewing files.
    Only use read_file() if you need to see the entire file for broader context.
    
    Args:
        file_path: Relative path to the file (e.g., "src/api/auth.py")
        
    Returns:
        The diff sections showing changed lines with surrounding context,
        including function/class signatures for better understanding.
        
    Example:
        read_diff("src/api/middleware.py")
        
    **IMPORTANT**: Focus your review comments ONLY on lines shown in this diff.
    Do NOT comment on code that isn't visible in the changed sections.
    """
    from pathlib import Path
    
    working_dir = get_working_directory()
    if not working_dir:
        return "Error: Working directory not initialized"
    
    try:
        # Get the PR diff from shared state
        from ._shared import get_pr_diff
        
        pr_diff = get_pr_diff()
        if not pr_diff:
            return "Error: No PR diff available. Use read_file() instead."
        
        # Parse the diff to find changed sections for this file
        diff_content = pr_diff.diff_content
        
        # Extract sections for this specific file
        file_sections = _extract_file_diff(diff_content, file_path)
        
        if not file_sections:
            return f"No changes found for {file_path} in this PR diff. File may not be modified."
        
        # Log tool activity
        hunk_count = file_sections.count('Lines around')
        char_count = len(file_sections)
        timing = LLMTimingCallback.get_and_clear_timing()
        print(f"🛠️ read_diff: '{file_path}' hunks={hunk_count} chars={char_count} {timing}", flush=True)
        
        return file_sections
        
    except Exception as e:
        return f"Error reading diff for {file_path}: {str(e)}\nTry using read_file() for the complete file."


def _extract_file_diff(diff_content: str, target_file: str) -> str:
    """Extract diff sections for a specific file with context.
    
    Args:
        diff_content: Full PR diff content
        target_file: Target file path
        
    Returns:
        Formatted diff sections with context
    """
    lines = diff_content.split('\n')
    
    # Find the diff section for this file
    file_start = None
    for i, line in enumerate(lines):
        # Look for diff header like: diff --git a/path/file.py b/path/file.py
        if line.startswith('diff --git') and target_file in line:
            file_start = i
            break
    
    if file_start is None:
        return ""
    
    # Find where this file's diff ends (next file or end of diff)
    file_end = len(lines)
    for i in range(file_start + 1, len(lines)):
        if lines[i].startswith('diff --git'):
            file_end = i
            break
    
    file_diff_lines = lines[file_start:file_end]
    
    # Parse hunks and format with context
    output = [
        f"=== Changed sections in {target_file} ===",
        "",
        "🚨🚨🚨 READ THIS CAREFULLY 🚨🚨🚨",
        "Lines with NO number and '-' prefix = OLD CODE BEING DELETED (already gone!)",
        "Lines with number and '+' prefix = NEW CODE BEING ADDED (review this!)",
        "Lines with number and no prefix = CONTEXT (unchanged)",
        "",
        "⚠️  IF A BUG IS IN '-' LINE AND FIXED IN '+' LINE → THAT'S GOOD! Add to positives!",
        "⚠️  ONLY create 'change' objects for PROBLEMS IN '+' LINES (new code issues)",
        "⚠️  DO NOT create 'change' objects for things that are already fixed!",
        "⚠️  When reporting an issue, use the line number from the '+' line (with + prefix)!",
        "⚠️  DO NOT use context line numbers - ONLY use line numbers from '+' lines!",
        ""
    ]
    
    current_hunk = []
    hunk_header = None
    
    for line in file_diff_lines:
        if line.startswith('@@'):
            # Save previous hunk
            if current_hunk:
                output.append(_format_hunk(hunk_header, current_hunk))
                current_hunk = []
            
            hunk_header = line
            
        elif line.startswith('+') and not line.startswith('+++'):
            current_hunk.append(('add', line[1:]))
        elif line.startswith('-') and not line.startswith('---'):
            current_hunk.append(('del', line[1:]))
        elif line.startswith(' '):
            current_hunk.append(('ctx', line[1:]))
    
    # Save last hunk
    if current_hunk:
        output.append(_format_hunk(hunk_header, current_hunk))
    
    if len(output) == 1:
        return ""
    
    output.append("\n💡 TIP: Use read_file() if you need to see more context beyond these changes.")
    
    return '\n'.join(output)


def _format_hunk(header: str, lines: list[tuple[str, str]]) -> str:
    """Format a diff hunk with line numbers and change markers.
    
    Args:
        header: Hunk header (e.g., @@ -10,5 +10,6 @@)
        lines: List of (type, content) tuples
        
    Returns:
        Formatted hunk string
    """
    import re
    
    # Extract line numbers from header
    match = re.search(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', header)
    if not match:
        old_line = 1
        new_line = 1
    else:
        old_line = int(match.group(1))
        new_line = int(match.group(2))
    
    output = [f"\nLines around {new_line} (changed):"]
    
    for line_type, content in lines:
        if line_type == 'add':
            output.append(f"  {new_line:4d} + {content}")
            new_line += 1
        elif line_type == 'del':
            # Deleted lines - don't show line number since they're removed
            output.append(f"       - {content}")
            old_line += 1
        else:  # context
            output.append(f"  {new_line:4d}   {content}")
            old_line += 1
            new_line += 1
    
    return '\n'.join(output)

