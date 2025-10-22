"""Utilities for parsing and analyzing unified diffs."""

import re
from collections import defaultdict


def get_changed_lines_by_file(diff_text: str) -> dict[str, set[int]]:
    """Parse unified diff into anchorable new-file line numbers per file.
    
    Returns a map of file_path -> set of line numbers that are anchorable for
    inline comments. Only lines with '+' prefix (added/modified lines) are included.
    Context lines and removed lines are excluded.
    
    Args:
        diff_text: Unified diff text (from git diff or Bitbucket API)
    
    Returns:
        Dictionary mapping file paths to sets of line numbers that can be
        anchored for inline comments (lines with '+' prefix in the diff)
    """
    changed: dict[str, set[int]] = defaultdict(set)
    current_file: str | None = None
    new_line_num: int | None = None
    
    for line in diff_text.splitlines():
        if line.startswith('diff --git'):
            current_file = None
            new_line_num = None
            continue
        if line.startswith('+++ '):
            path = line[4:].strip()
            if path.startswith('b/'):
                path = path[2:]
            current_file = path if path != '/dev/null' else None
            continue
        if line.startswith('@@'):
            # Example: @@ -53,7 +55,9 @@
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                new_line_num = int(m.group(1))
            else:
                new_line_num = None
            continue
        if current_file is None or new_line_num is None:
            continue
        if line.startswith('+') and not line.startswith('+++ '):
            # Added line in new file → anchorable
            changed[current_file].add(new_line_num)
            new_line_num += 1
        elif line.startswith('-') and not line.startswith('--- '):
            # Removed line; belongs to old file → not anchorable
            continue
        elif line.startswith('\\'):
            # Diff metadata (e.g., "\ No newline at end of file") - don't advance counter
            continue
        else:
            # Context line - advance counter but DON'T add to anchorable lines
            # (only lines with '+' prefix can be anchored for inline comments)
            new_line_num += 1
    
    return dict(changed)  # Return plain dict to avoid defaultdict side effects

