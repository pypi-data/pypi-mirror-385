"""LangChain tools for the code review agent."""

from ._shared import initialize_tools
from .get_file_info import get_file_info
from .list_directory import list_directory
from .read_diff import read_diff
from .read_file import read_file
from .search_files import search_files
from .submit_review import submit_review, get_submitted_review, reset_submitted_review
from .think import think

__all__ = [
    "read_diff",
    "read_file",
    "list_directory",
    "get_file_info",
    "search_files",
    "think",
    "submit_review",
    "create_code_review_tools",
]


def create_code_review_tools(working_directory: str = ".", pr_diff=None) -> list:
    """Create a list of code review tools.

    Args:
        working_directory: Base directory for file operations
        pr_diff: Optional PR diff for read_diff tool

    Returns:
        List of LangChain tools
    """
    initialize_tools(working_directory, pr_diff)

    return [
        think,
        read_diff,  # PRIMARY TOOL - start here
        read_file,
        list_directory,
        get_file_info,
        search_files,
        submit_review,
    ]

