from typing import Optional, Dict, Any
from fastmcp import FastMCP
from evo_memory.memory.base import Memory, MemoryEntry
from evo_memory.memory.retriever import EmbeddingRetriever
import json
import os

# Create a FastMCP server
mcp = FastMCP("Evo-Memory")

# Default storage path
STORAGE_PATH = os.path.join(os.getcwd(), "memory_state.json")

# [CONFIG] Global toggle for semantic embeddings
# Set to False to disable Vector Search and avoid loading the heavy model (saves RAM/Network)
USE_EMBEDDINGS = False

# Initialize the core memory engine
memory_engine = Memory(
    max_size=1000,
    enable_pruning=True,
    store_successful_only=False
)

# Initialize Semantic Retriever ONLY if enabled
retriever = None
if USE_EMBEDDINGS:
    retriever = EmbeddingRetriever(
        model_name="BAAI/bge-base-en-v1.5",
        device=None # Auto-detect GPU/CPU
    )

# Load existing memory if available
if os.path.exists(STORAGE_PATH):
    try:
        memory_engine.load(STORAGE_PATH)
        print(f"Loaded {len(memory_engine)} experiences from {STORAGE_PATH}")
    except Exception as e:
        print(f"Error loading initial memory: {e}")

@mcp.tool()
def add_experience(
    input_text: str,
    output_text: str,
    feedback: Optional[str] = None,
    is_successful: bool = True
) -> str:
    """
    Records a new task experience. Automatically computes embeddings if enabled.
    """
    entry = MemoryEntry(
        task_id="", 
        input_text=input_text,
        output_text=output_text,
        feedback=feedback,
        is_successful=is_successful
    )
    
    # Compute embedding ONLY if enabled and retriever is ready
    if USE_EMBEDDINGS and retriever:
        try:
            entry.embedding = retriever.encode(entry.to_text())
        except Exception as e:
            print(f"Warning: Could not compute embedding: {e}")

    if memory_engine.add(entry):
        try:
            memory_engine.save(STORAGE_PATH)
            status = "embedded and persisted" if entry.embedding else "persisted (no embedding)"
            return f"Experience evolved, {status}. Task ID: {entry.task_id}"
        except Exception as e:
            return f"Evolved in-memory, but failed to save: {str(e)}"
    return "Failed to evolve memory."

@mcp.tool()
def search_memories(query: str, k: int = 3) -> str:
    """
    Search for relevant past experiences. 
    Uses Semantic Vector Search if enabled, otherwise falls back to Recency Search.
    
    Args:
        query: The current task or question.
        k: Number of memories to retrieve.
    """
    if len(memory_engine) == 0:
        return "No memories stored yet."

    # OPTION 1: Semantic Vector Search
    if USE_EMBEDDINGS and retriever:
        try:
            results = retriever.retrieve(query, memory_engine, top_k=k)
            if not results:
                return "No relevant memories found for this query."
            
            output = [f"[Semantic Relevance: {res.score:.2f}]\n{res.entry.to_text()}" for res in results]
            return "\n\n---\n\n".join(output)
        except Exception as e:
            return f"Error during semantic search: {str(e)}"
    
    # OPTION 2: Fallback to Recency Search (if embeddings are disabled)
    entries = memory_engine.get_recent(k)
    output = ["[Recency Search Result]\n" + e.to_text() for e in entries]
    return "\n\n---\n\n".join(output)

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
    mcp.run(transport="http", host="127.0.0.1", port=8000)
