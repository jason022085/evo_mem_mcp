import asyncio
from fastmcp import Client

async def test_tools():
    print("Connecting to FastMCP server via HTTP...")
    
    # FastMCP Client handles the protocol details over HTTP
    async with Client("http://localhost:8000/mcp") as client:
        print("\n[1/3] Testing: add_experience")
        # Call tool via MCP protocol
        result = await client.call_tool("add_experience", {
            "input_text": "What is TSMC?",
            "output_text": "A Taiwanese semiconductor manufacturer.",
            "feedback": "Correct",
            "is_successful": True
        })
        print(f"Server Response: {result}")

        print("\n[2/3] Testing: search_memories")
        result = await client.call_tool("search_memories", {"query": "What is TSMC?", "k": 1})
        print(f"Search Results:\n{result}")

        print("\n[3/3] Testing Resource: memory://stats")
        # Resources are read via the protocol
        stats = await client.read_resource("memory://stats")
        print(f"Stats:\n{stats}")

if __name__ == "__main__":
    try:
        asyncio.run(test_tools())
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure 'python server.py' is running.")
