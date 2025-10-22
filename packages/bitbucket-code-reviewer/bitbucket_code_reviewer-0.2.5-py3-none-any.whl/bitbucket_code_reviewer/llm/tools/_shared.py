"""Shared utilities for code review tools."""

from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.models import PullRequestDiff

# Global variables
_working_directory = Path(".")
_pr_diff: Optional["PullRequestDiff"] = None


def get_working_directory() -> Path:
    """Get the current working directory for tools."""
    return _working_directory


def get_pr_diff() -> Optional["PullRequestDiff"]:
    """Get the current PR diff for tools."""
    return _pr_diff


def initialize_tools(working_directory: str = ".", pr_diff: Optional["PullRequestDiff"] = None, verbose: bool = False) -> None:
    """Initialize tools with working directory and PR diff.
    
    Args:
        working_directory: Base directory for file operations
        pr_diff: Optional PR diff for read_diff tool
        verbose: Enable verbose debug output
    """
    global _working_directory, _pr_diff
    _working_directory = Path(working_directory).resolve()
    _pr_diff = pr_diff
    print(f"🔧 Initializing tools: working_directory='{_working_directory}'", flush=True)

