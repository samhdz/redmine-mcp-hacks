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

### 4. 設定 Redmine API

#### 4.1 啟用 REST API
1. 以管理員身份登入 Redmine 系統
2. 前往 **管理** → **設定** → **API**
3. 勾選 **「啟用 REST 網路服務技術（Web Service）」**
4. 點擊 **儲存** 按鈕

#### 4.2 設定 Redmine 基本資料（管理員）
在開始使用 MCP 工具之前，需要先設定 Redmine 的基本資料：

**設定角色和權限**
1. 前往 **管理** → **角色與權限**
2. 建立或編輯角色（如：開發者、測試者、專案經理）
3. 為角色分配適當的權限（建議至少包含：查看議題、新增議題、編輯議題）

**設定追蹤器**
1. 前往 **管理** → **追蹤器**
2. 建立追蹤器類型（如：缺陷、功能、支援）
3. 設定每個追蹤器的預設狀態和工作流程

**設定議題狀態**
1. 前往 **管理** → **議題狀態**
2. 建立狀態（如：新建、進行中、已解決、已關閉、已拒絕）
3. 設定狀態屬性（是否為關閉狀態等）

**設定工作流程**
1. 前往 **管理** → **工作流程**
2. 為每個角色和追蹤器組合設定允許的狀態轉換
3. 確保基本的狀態轉換路徑（新建 → 進行中 → 已解決 → 已關閉）

**建立專案**
1. 前往 **專案** → **新增專案**
2. 設定專案名稱、識別碼、描述
3. 選擇啟用的模組（至少啟用「議題跟蹤」）
4. 指派成員並設定角色

#### 4.3 取得 API 金鑰
1. 登入您的 Redmine 系統（可以是管理員或一般用戶）
2. 前往 **我的帳號** → **API 存取金鑰**
3. 點擊 **顯示** 或 **重設** 來取得 API 金鑰
4. 將金鑰複製到 `.env` 檔案中的 `REDMINE_API_KEY`

> **⚠️ 重要提醒**: 
> - 如果找不到 API 金鑰選項，請確認已完成步驟 4.1 啟用 REST API
> - 完成基本設定後才能正常建立和管理議題
> 
> **📚 詳細設定指南**: 如需完整的 Redmine 設定步驟，請參考 [Redmine 完整設定指南](docs/manuals/redmine_setup_guide.md)

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
| `get_trackers` | 取得所有可用的追蹤器列表 |
| `get_priorities` | 取得所有可用的議題優先級 |
| `get_time_entry_activities` | 取得所有可用的時間追蹤活動 |
| `get_document_categories` | 取得所有可用的文件分類 |

## 💡 使用範例

### 在 Claude Code 中使用

```
# 查看服務器狀態
請執行健康檢查

# 取得專案列表
顯示所有可存取的專案

# 查看系統設定
取得所有可用的議題狀態
取得所有可用的追蹤器列表
取得所有可用的議題優先級
取得所有可用的時間追蹤活動
取得所有可用的文件分類

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
- **檢查 Redmine 是否啟用 REST API**：前往 `管理` → `設定` → `API`，勾選「啟用 REST 網路服務技術」
- 確認用戶權限是否足夠
- 檢查網址是否正確（包含 http/https 和埠號）

**2. 連線逾時**
- 檢查網路連線
- 調整 `REDMINE_TIMEOUT` 環境變數
- 確認 Redmine 服務器狀態

**3. 議題建立失敗**
- 確認專案是否存在且有權限
- 檢查必要欄位是否已填寫
- 確認追蹤器和狀態設定
- **檢查基本資料設定**：確認已完成角色、追蹤器、狀態、工作流程設定
- 確認用戶在專案中有適當的角色和權限

**4. 狀態更新失敗**
- 檢查工作流程是否允許該狀態轉換
- 確認用戶角色有權限進行狀態變更
- 確認目標狀態 ID 是否正確

**5. 找不到專案或議題**
- 確認 ID 是否正確
- 檢查用戶是否有查看該專案/議題的權限
- 確認專案狀態是否為啟用狀態

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