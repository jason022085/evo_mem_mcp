from typing import Optional, Dict, Any
from fastmcp import FastMCP
from evo_memory.memory.base import Memory, MemoryEntry
import json
import os

# Create a FastMCP server
# Reference: https://gofastmcp.com/
mcp = FastMCP("Evo-Memory")

# Initialize the core memory engine
memory_engine = Memory(
    max_size=1000,
    enable_pruning=True,
    store_successful_only=False
)

@mcp.tool()
def add_experience(
    input_text: str,
    output_text: str,
    feedback: Optional[str] = None,
    is_successful: bool = True
) -> str:
    """
    Records a new task experience. This is the 'Evolve' step.
    
    Args:
        input_text: The user prompt or task description.
        output_text: The model generated response.
        feedback: Evaluation or correction.
        is_successful: Boolean indicating if the task was completed successfully.
    """
    entry = MemoryEntry(
        task_id="", 
        input_text=input_text,
        output_text=output_text,
        feedback=feedback,
        is_successful=is_successful
    )
    
    if memory_engine.add(entry):
        return f"Experience synthesized and evolved. Task ID: {entry.task_id}"
    return "Failed to evolve memory."

@mcp.tool()
def search_memories(k: int = 3) -> str:
    """
    Search for relevant past experiences. Currently uses recency-based retrieval.
    """
    entries = memory_engine.get_recent(k)
    if not entries:
        return "No relevant memories found."
    
    return "\n---\n".join([e.to_text() for e in entries])

@mcp.resource("memory://stats")
def get_stats() -> str:
    """Real-time performance metrics of the memory engine."""
    return json.dumps(memory_engine.get_statistics(), indent=2)

@mcp.resource("memory://archive")
def get_archive() -> str:
    """The full history of evolved memory entries."""
    entries = [e.to_dict() for e in memory_engine.get_all()]
    return json.dumps(entries, indent=2)

if __name__ == "__main__":
    # Run as a streamable HTTP server (SSE)
    # This enables remote access and modern MCP transport
    mcp.run(transport="http", host="127.0.0.1", port=8000)
