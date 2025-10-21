"""Tool for LLM to communicate its thinking and intentions."""

from langchain_core.tools import tool
from ..callbacks import LLMTimingCallback


@tool
def think(thought: str) -> str:
    """Express your current thinking, reasoning, and plans in 2-3 sentences.
    
    Use this tool FREQUENTLY throughout your review to share what you're doing and what you're finding.
    You should call this 8-15 times during a typical review.
    
    Examples of good usage:
    ✅ "Starting review by reading the diff for override_repository.py. Want to check if the aggregation 
       count change includes proper error handling. Will also verify the collection name constant is used 
       consistently."
    ✅ "Found a potential issue in the aggregation count - accessing [0][0] without checking if results 
       exist. This could throw IndexError if query returns empty. Need to check if there are tests covering 
       this edge case."
    ✅ "Reviewed 3 files so far. Found 1 critical issue with error handling and 2 minor style improvements. 
       Going to check the test files next to see if the new aggregation behavior is tested."
    
    Args:
        thought: Your thinking, observations, or next steps in 2-3 sentences
        
    Returns:
        Acknowledgment message
    """
    timing = LLMTimingCallback.get_and_clear_timing()
    print(f"💭 {thought} {timing}")
    return "Noted. Continue with your review."

