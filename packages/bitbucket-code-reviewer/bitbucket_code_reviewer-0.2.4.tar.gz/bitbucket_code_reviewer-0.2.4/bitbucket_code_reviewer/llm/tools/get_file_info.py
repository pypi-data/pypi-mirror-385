"""Get file info tool for code review agent."""

from langchain_core.tools import tool

from ._shared import get_working_directory
from ..callbacks import LLMTimingCallback


@tool
def get_file_info(file_path: str) -> dict:
    """Get basic information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information
    """
    working_dir = get_working_directory()
    full_path = working_dir / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    stat = full_path.stat()

    info = {
        "file_path": file_path,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "is_file": full_path.is_file(),
        "extension": full_path.suffix,
    }

    timing = LLMTimingCallback.get_and_clear_timing()
    print(
        f"🛠️ get_file_info: '{file_path}' size={info['size']} modified={info['modified']} {timing}",
        flush=True,
    )
    return info

