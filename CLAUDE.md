# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個 MCP (Model Context Protocol) 伺服器專案，用於與 Redmine 系統整合。使用 Python 3.12+ 和 uv 包管理器。

## 開發環境設置

### 依賴管理
- 使用 `uv` 作為包管理器
- 安裝依賴：`uv sync`
- 執行測試：`uv run python -m pytest`

### 專案結構  
```
redmine-mcp/
├── src/redmine_mcp/          # 主要原始碼
│   ├── __init__.py           # 套件初始化
│   ├── server.py             # MCP 服務器主程式 ✓ 已完成
│   ├── redmine_client.py     # Redmine API 客戶端 ✓ 已完成
│   ├── config.py             # 配置管理 ✓ 已完成
├── tests/                    # 測試檔案
├── docs/                     # 文件目錄
│   ├── issues/               # 開發問題記錄
│   └── manuals/              # 技術手冊
├── pyproject.toml            # 專案配置和依賴
├── uv.lock                   # 鎖定的依賴版本
└── .env                      # 環境變數 (待建立)
```

## MCP 開發說明

### 技術棧
- **MCP SDK**: mcp[cli] >= 1.9.4 (使用 FastMCP)
- **HTTP 客戶端**: requests >= 2.31.0
- **配置管理**: python-dotenv >= 1.0.0
- **Python 版本**: >= 3.12

### MCP 服務器架構
- 使用 FastMCP 建立服務器
- 工具註冊使用 `@mcp.tool()` 裝飾器
- 支援非同步操作和類型安全

### Redmine API 整合
- **議題管理**: 查詢、建立、更新、刪除議題
- **專案管理**: 查詢、建立、更新、刪除、封存專案
- **用戶管理**: 查詢用戶、取得當前用戶資訊
- **元數據查詢**: 狀態、優先級、追蹤器列表
- **觀察者管理**: 新增/移除議題觀察者
- **完整篩選支援**: 多條件篩選和排序

## Claude Code 整合

### 安裝到 Claude Code
```bash
# 安裝 MCP 服務器
uv tool install .

# 或使用 pip
pip install .

# 添加到 Claude Code
claude mcp add redmine "redmine-mcp" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here" \
  -e REDMINE_MCP_LOG_LEVEL="INFO" \
  -e REDMINE_MCP_TIMEOUT="30"
```

### 環境變數說明

為避免與其他專案的環境變數衝突，redmine-mcp 使用專屬前綴：

- **專屬變數**（優先）：
  - `REDMINE_MCP_LOG_LEVEL`: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - `REDMINE_MCP_TIMEOUT`: 請求超時時間（秒）

- **向後相容**（備用）：
  - `LOG_LEVEL`: 如果未設定 REDMINE_MCP_LOG_LEVEL 時使用
  - `REDMINE_TIMEOUT`: 如果未設定 REDMINE_MCP_TIMEOUT 時使用

- **必要變數**：
  - `REDMINE_DOMAIN`: Redmine 伺服器網址
  - `REDMINE_API_KEY`: Redmine API 金鑰

### 可用的 MCP 工具（14 個）
- **管理工具**: server_info, health_check
- **查詢工具**: get_issue, list_project_issues, get_projects, get_issue_statuses, search_issues, get_my_issues
- **編輯工具**: update_issue_status, update_issue_content, add_issue_note, assign_issue, close_issue
- **建立工具**: create_new_issue

## 常用指令

```bash
# 安裝依賴
uv sync

# 執行 MCP 服務器
uv run python -m redmine_mcp.server

# 測試 Claude Code 整合
uv run python tests/scripts/claude_integration.py

# 執行單元測試
uv run python -m pytest tests/unit/

# 執行所有測試
uv run python -m pytest tests/

# 添加新依賴
uv add <package-name>
```

## 注意事項

- 專案正在開發初期階段
- 後續會根據開發進度更新此檔案內容