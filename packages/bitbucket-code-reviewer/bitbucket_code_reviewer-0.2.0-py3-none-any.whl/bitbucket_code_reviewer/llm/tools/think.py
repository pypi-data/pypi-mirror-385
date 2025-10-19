"""Tool for LLM to communicate its thinking and intentions."""

from langchain_core.tools import tool


@tool
def think(thought: str) -> str:
    """Express your current thinking in 1-2 SHORT sentences (max ~80 chars).
    
    BE BRIEF! Examples:
    ✅ GOOD: "Checking auth.py for input validation. Found 2 issues."
    ✅ GOOD: "Reading tests next to verify coverage."
    ❌ BAD: Long explanations, detailed reasoning, or multiple paragraphs.
    
    Keep thoughts SHORT and actionable - just state what you're doing or found!
    
    Args:
        thought: Your BRIEF (1-2 sentences, ~80 chars) thinking or plan
        
    Returns:
        Acknowledgment message
    """
    print(f"💭 Thinking ... {thought}")
    return "Noted. Continue."

