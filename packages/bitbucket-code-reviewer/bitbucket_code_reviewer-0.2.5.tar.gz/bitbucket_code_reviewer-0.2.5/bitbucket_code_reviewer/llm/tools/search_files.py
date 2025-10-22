"""Search files tool for code review agent."""

from langchain_core.tools import tool
import subprocess

from ._shared import get_working_directory
from ..callbacks import LLMTimingCallback


@tool
def search_files(pattern: str, path: str = ".") -> list[str]:
    """Search for files by FILENAME pattern (glob). This searches filenames ONLY, NOT file contents.

    Use this to find files when you know part of the filename but not the exact path.
    This does NOT search inside files - use read_file for that.

    Args:
        pattern: Glob pattern to match FILENAMES (e.g., "*.py", "**/*test*.py", "*config*")
                 Use * as wildcard. Examples:
                 - "*.py" = all Python files in current dir
                 - "**/*.test.py" = all test files recursively
                 - "*repository*" = files with "repository" in filename
        path: Starting directory path (default: ".")

    Returns:
        List of matching file paths

    Example: To find test files, use pattern="**/*test*.py", NOT pattern="test" or pattern="TestClass"
    """
    working_dir = get_working_directory()
    full_path = working_dir / path

    if not full_path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")

    try:
        matches = list(full_path.glob(pattern))
    except ValueError as err:
        raise ValueError(f"Invalid glob pattern: {pattern}") from err

    # Convert to relative paths
    relative_matches = []
    for match in matches:
        if match.is_file():
            relative_matches.append(str(match.relative_to(working_dir)))

    matches_sorted = sorted(relative_matches)

    timing = LLMTimingCallback.get_and_clear_timing()
    print(
        f"🛠️ search_files: '{path}' pattern='{pattern}' matches={len(matches_sorted)} {timing}",
        flush=True,
    )
    return matches_sorted


@tool
def grep_codebase(search_text: str, file_pattern: str = "*.py") -> str:
    """Search for text/code inside files (like grep). Use this to find where code is used or imported.

    This searches FILE CONTENTS, not filenames. Perfect for finding:
    - Where a class is imported or used
    - Where a function is called
    - Where a variable is referenced

    Args:
        search_text: Text to search for (e.g., "OverrideRepository", "get_override", "import override")
        file_pattern: Limit to file types (default: "*.py"). Examples: "*.ts", "*.java", "*"

    Returns:
        List of matches showing file:line:content for each occurrence
        
    Example: grep_codebase("OverrideRepository") finds all files using that class
    """
    working_dir = get_working_directory()
    
    try:
        # Use ripgrep if available (faster), fall back to grep
        try:
            result = subprocess.run(
                ["rg", "--no-heading", "--line-number", "--glob", file_pattern, search_text, str(working_dir)],
                capture_output=True,
                text=True,
                timeout=10
            )
        except FileNotFoundError:
            # Fall back to grep
            result = subprocess.run(
                ["grep", "-r", "-n", "--include", file_pattern, search_text, str(working_dir)],
                capture_output=True,
                text=True,
                timeout=10
            )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # Limit to first 50 matches to avoid token overflow
            limited = lines[:50]
            match_count = len(lines)
            
            timing = LLMTimingCallback.get_and_clear_timing()
            print(f"🛠️ grep_codebase: '{search_text}' pattern='{file_pattern}' matches={match_count} {timing}", flush=True)
            
            if match_count > 50:
                return '\n'.join(limited) + f"\n\n... and {match_count - 50} more matches (showing first 50)"
            return '\n'.join(limited)
        else:
            timing = LLMTimingCallback.get_and_clear_timing()
            print(f"🛠️ grep_codebase: '{search_text}' pattern='{file_pattern}' matches=0 {timing}", flush=True)
            return f"No matches found for '{search_text}' in {file_pattern} files"
            
    except subprocess.TimeoutExpired:
        return "Search timed out - try a more specific search term"
    except Exception as e:
        return f"Search failed: {str(e)}"

