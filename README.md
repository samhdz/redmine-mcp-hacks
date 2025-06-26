# Redmine MCP Server

一個使用 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 與 Redmine 系統整合的伺服器，讓 Claude Code 能夠直接操作 Redmine 專案管理系統。

## 🚀 功能特色

### ✅ 議題管理
- **查詢議題**: 取得議題詳細資訊和列表
- **建立議題**: 建立新的議題並設定相關屬性
- **更新議題**: 修改議題內容、狀態、優先級等
- **指派議題**: 指派或取消指派議題給特定用戶
- **新增備註**: 為議題新增公開或私有備註
- **關閉議題**: 自動設定議題為已完成狀態

### ✅ 專案管理
- **專案列表**: 取得可存取的專案清單
- **專案議題**: 依狀態篩選並列出專案中的所有議題

### ✅ 搜尋功能
- **關鍵字搜尋**: 在議題標題和描述中搜尋關鍵字
- **我的議題**: 快速查看指派給當前用戶的議題

### ✅ 系統工具
- **健康檢查**: 確認 MCP 服務器和 Redmine 連線狀態
- **狀態查詢**: 取得可用的議題狀態列表

## 📋 系統需求

- **Python**: 3.12 或更高版本
- **Redmine**: 支援 REST API 的版本（建議 4.0+）
- **套件管理器**: [uv](https://docs.astral.sh/uv/) 或 pip

## 🔧 安裝設定

### 1. 克隆專案

```bash
git clone <repository-url>
cd redmine-mcp
```

### 2. 安裝依賴

使用 uv（推薦）：
```bash
uv sync
```

或使用 pip：
```bash
pip install -e .
```

### 3. 環境設定

建立 `.env` 檔案：
```bash
cp .env.example .env
```

編輯 `.env` 檔案，設定以下環境變數：
```env
REDMINE_DOMAIN=https://your-redmine-domain.com
REDMINE_API_KEY=your_api_key_here
REDMINE_TIMEOUT=30
DEBUG_MODE=false
```

### 4. 取得 Redmine API 金鑰

1. 登入您的 Redmine 系統
2. 前往 **我的帳號** → **API 存取金鑰**
3. 點擊 **顯示** 或 **重設** 來取得 API 金鑰
4. 將金鑰複製到 `.env` 檔案中的 `REDMINE_API_KEY`

## 🔗 Claude Code 整合

### 安裝到 Claude Code

```bash
# 從本地安裝
uv tool install .

# 或使用 pip
pip install .

# 新增到 Claude Code MCP 配置
claude mcp add redmine "redmine-mcp" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here"
```

### 驗證安裝

```bash
# 測試 MCP 服務器
uv run python -m redmine_mcp.server

# 測試 Claude Code 整合
uv run python test_claude_integration.py
```

## 🛠️ 可用的 MCP 工具

### 基本工具
| 工具名稱 | 功能描述 |
|---------|---------|
| `server_info` | 顯示服務器資訊和配置狀態 |
| `health_check` | 檢查服務器和 Redmine 連線健康狀態 |

### 議題操作
| 工具名稱 | 功能描述 |
|---------|---------|
| `get_issue` | 取得指定議題的詳細資訊 |
| `create_new_issue` | 建立新的議題 |
| `update_issue_status` | 更新議題狀態 |
| `update_issue_content` | 更新議題內容（標題、描述等） |
| `add_issue_note` | 為議題新增備註 |
| `assign_issue` | 指派或取消指派議題 |
| `close_issue` | 關閉議題並設定完成度 |

### 查詢工具
| 工具名稱 | 功能描述 |
|---------|---------|
| `list_project_issues` | 列出專案中的議題 |
| `get_my_issues` | 取得指派給我的議題列表 |
| `search_issues` | 搜尋包含關鍵字的議題 |
| `get_projects` | 取得可存取的專案列表 |
| `get_issue_statuses` | 取得所有可用的議題狀態 |

## 💡 使用範例

### 在 Claude Code 中使用

```
# 查看服務器狀態
請執行健康檢查

# 取得專案列表
顯示所有可存取的專案

# 查看特定議題
取得議題 #123 的詳細資訊

# 建立新議題
在專案 ID 1 中建立議題：
- 標題：修復登入錯誤
- 描述：用戶無法正常登入系統
- 優先級：高

# 搜尋議題
搜尋包含「登入」關鍵字的議題

# 更新議題狀態
將議題 #123 狀態更新為「進行中」，備註「開始處理此問題」
```

## 🧪 測試

### 執行測試套件

```bash
# 執行所有測試
uv run python -m pytest

# 執行 MCP 整合測試
uv run python test_mcp_integration.py

# 執行 Claude Code 整合測試  
uv run python test_claude_integration.py
```

### Docker 環境測試

如果您想在本地 Docker 環境中測試：

```bash
# 啟動 Redmine 測試環境
docker-compose up -d

# 快速啟動完整測試環境
./quick_start.sh
```

## 🔍 故障排除

### 常見問題

**1. API 認證失敗 (401/403 錯誤)**
- 確認 API 金鑰是否正確
- 檢查 Redmine 是否啟用 REST API
- 確認用戶權限是否足夠

**2. 連線逾時**
- 檢查網路連線
- 調整 `REDMINE_TIMEOUT` 環境變數
- 確認 Redmine 服務器狀態

**3. 議題建立失敗**
- 確認專案是否存在且有權限
- 檢查必要欄位是否已填寫
- 確認追蹤器和狀態設定

### 除錯模式

啟用除錯模式以取得更詳細的錯誤資訊：

```env
DEBUG_MODE=true
```

## 📁 專案結構

```
redmine-mcp/
├── src/redmine_mcp/          # 主要原始碼
│   ├── __init__.py           # 套件初始化
│   ├── server.py             # MCP 服務器主程式
│   ├── redmine_client.py     # Redmine API 客戶端
│   ├── config.py             # 配置管理
│   └── validators.py         # 資料驗證
├── tests/                    # 測試檔案
├── docs/                     # 文件目錄
├── docker-compose.yml        # Docker 測試環境
├── pyproject.toml            # 專案配置
└── README.md                 # 專案說明
```

## 🤝 貢獻指南

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## 🔗 相關連結

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Code](https://claude.ai/code)
- [Redmine](https://www.redmine.org/)
- [FastMCP](https://github.com/jlowin/fastmcp)

---

如有任何問題或建議，歡迎開啟 Issue 或聯絡專案維護者。