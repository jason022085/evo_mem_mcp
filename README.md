# Evo-Memory MCP Server

A high-performance Model Context Protocol (MCP) server implementation of the [Evo-Memory](https://github.com/zhaosnw/evo_mem) framework. This server enables LLM agents to maintain a self-evolving memory store, allowing them to learn from past experiences in real-time.

Built with [FastMCP](https://gofastmcp.com/) for a modern, streamable HTTP/SSE experience.

## 🚀 Features

- **Self-Evolving Memory**: Implements the "Search-Synthesize-Evolve" loop from the Evo-Memory research paper.
- **Task-Centric Experience**: Stores inputs, outputs, feedback, and success states.
- **Streamable HTTP/SSE**: Optimized for low-latency interactions and remote connectivity.
- **Built-in Management UI**: Interactive web interface for testing and monitoring at `http://localhost:8000`.
- **Automatic Pruning**: Intelligent memory management to stay within capacity limits.

## 🛠️ Project Structure

```text
.
├── evo_memory/          # Core Evo-Memory module (refactored for direct import)
├── pyproject.toml       # Project metadata and dependencies
├── requirements.txt     # Environment installation helper
├── server.py            # FastMCP Server entry point
└── test_mcp_tools.py    # Protocol-compliant test client
```

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd evo_mem_mcp
   ```

2. **Set up the environment**:
   ```bash
   # Using pip
   pip install -r requirements.txt
   ```

## 🚦 Usage

### Starting the Server
Run the server in HTTP/SSE mode (default port 8000):
```bash
python server.py
```

### Accessing the Web UI
Open your browser and navigate to:
`http://localhost:8000`

### Connecting to Claude Desktop
Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "evo-memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/inspector",
        "http://localhost:8000/mcp"
      ]
    }
  }
}
```

## 🔧 Available Tools & Resources

### Tools
- **`add_experience`**: The "Evolve" step. Record a new task experience (input, output, feedback, result).
- **`search_memories`**: The "Search" step. Retrieve the most relevant/recent past experiences to inform current tasks.

### Resources
- **`memory://stats`**: Real-time JSON statistics of the memory engine (success rate, retention, etc.).
- **`memory://archive`**: Access the full history of evolved memory entries.

## 🧪 Testing
We provide a protocol-compliant test script that uses the `fastmcp.Client`:
```bash
python test_mcp_tools.py
```

## 📚 Acknowledgments
This project is an MCP adaptation of the original **Evo-Memory** research by [zhaosnw](https://github.com/zhaosnw/evo_mem).
