"""LangChain tools for the code review agent."""

from ._shared import initialize_tools
from .get_file_info import get_file_info
from .list_directory import list_directory
from .read_diff import read_diff
from .read_file import read_file
from .search_files import search_files, grep_codebase
from .submit_review import submit_review, get_submitted_review, reset_submitted_review

__all__ = [
    "read_diff",
    "read_file",
    "list_directory",
    "get_file_info",
    "search_files",
    "grep_codebase",
    "submit_review",
    "create_code_review_tools",
]


def create_code_review_tools(working_directory: str = ".", pr_diff=None, verbose: bool = False) -> list:
    """Create a list of code review tools.

    Args:
        working_directory: Base directory for file operations
        pr_diff: Optional PR diff for read_diff tool
        verbose: Enable verbose debug output

    Returns:
        List of LangChain tools
    """
    initialize_tools(working_directory, pr_diff, verbose)

    return [
        read_diff,  # PRIMARY TOOL - start here
        read_file,
        grep_codebase,  # Search file contents
        list_directory,
        get_file_info,
        search_files,
        submit_review,
    ]

