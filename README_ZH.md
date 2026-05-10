# Evo-Memory MCP Server (中文版)

這是一個基於 [Evo-Memory](https://github.com/zhaosnw/evo_mem) 框架的高效能 Model Context Protocol (MCP) 伺服器實現。此伺服器使 LLM 智能體（Agents）能夠維護一個自我演進的記憶庫，從而實現即時的經驗學習與回饋。

本專案採用 [FastMCP](https://gofastmcp.com/) 構建，提供現代化的 Streamable HTTP/SSE 體驗。

## 🚀 核心特性

- **自我演進記憶**：實現了 Evo-Memory 研究論文中的「搜索-合成-演進」（Search-Synthesize-Evolve）循環。
- **以任務為中心的經驗存儲**：記錄輸入、輸出、反饋以及任務成功狀態。
- **Streamable HTTP/SSE**：針對低延遲互動和遠程連接進行了優化。
- **內建管理介面**：在 `http://localhost:8000` 提供互動式 Web UI，方便測試與監控。
- **自動剪枝**：智能記憶管理機制，確保記憶庫容量維持在設定限制內。

## 🛠️ 專案結構

```text
.
├── evo_memory/          # 核心 Evo-Memory 模組（已重構為直接導入模式）
├── pyproject.toml       # 專案元數據與依賴定義
├── requirements.txt     # 環境安裝輔助檔案
├── server.py            # FastMCP 伺服器入口點
└── test_mcp_tools.py    # 符合 MCP 協議的測試客戶端
```

## 📦 安裝步驟

1. **複製存儲庫**：
   ```bash
   git clone <您的-repo-網址>
   cd evo_mem_mcp
   ```

2. **配置環境**：
   ```bash
   # 使用 pip 安裝所有依賴
   pip install -r requirements.txt
   ```

## 🚦 使用指南

### 啟動伺服器
以 HTTP/SSE 模式啟動伺服器（預設端口 8000）：
```bash
python server.py
```

### 訪問 Web UI
啟動後，在瀏覽器中打開：
`http://localhost:8000`

### 在 Claude Desktop 中配置
將以下內容加入您的 `claude_desktop_config.json`：
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

## 🔧 可用的工具與資源

### 工具 (Tools)
- **`add_experience`**：「演進」（Evolve）步驟。記錄新的任務經驗（包括輸入、輸出、反饋與結果）。
- **`search_memories`**：「搜索」（Search）步驟。檢索最相關或最近的過去經驗，以輔助當前任務。

### 資源 (Resources)
- **`memory://stats`**：記憶引擎的即時 JSON 統計數據（如成功率、保留率等）。
- **`memory://archive`**：訪問完整的演進記憶歷史記錄。

## 🧪 測試
我們提供了一個使用 `fastmcp.Client` 的協議相容測試腳本：
```bash
python test_mcp_tools.py
```

## 📚 致謝
本專案是 [zhaosnw](https://github.com/zhaosnw/evo_mem) 所研發的 **Evo-Memory** 研究成果之 MCP 適配版本。
