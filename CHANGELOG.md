# 變更日誌

所有對此專案的重要變更都將記錄在此檔案中。

本專案遵循 [語義化版本](https://semver.org/lang/zh-TW/) 規範。

## [未發布]

### 新增
- 待發布的新功能

### 變更
- 待發布的變更

### 修復
- 待發布的錯誤修復

## [0.1.0] - 2024-01-24

### 新增
- 🎉 首次發布 Redmine MCP Server
- ✅ 實作完整的 MCP 服務器架構
- 🔧 提供 14 個核心 MCP 工具
- 📋 議題管理功能
  - `get_issue` - 取得議題詳細資訊
  - `create_new_issue` - 建立新議題
  - `update_issue_status` - 更新議題狀態
  - `update_issue_content` - 更新議題內容
  - `add_issue_note` - 新增議題備註
  - `assign_issue` - 指派議題
  - `close_issue` - 關閉議題
- 🗂️ 專案管理功能
  - `get_projects` - 取得專案列表
  - `list_project_issues` - 列出專案議題
  - `get_issue_statuses` - 取得議題狀態
- 🔍 搜尋功能
  - `search_issues` - 搜尋議題
  - `get_my_issues` - 取得我的議題
- 🔧 系統工具
  - `server_info` - 服務器資訊
  - `health_check` - 健康檢查
- 🔐 完整的認證和權限管理
- 🛡️ 資料驗證和錯誤處理機制
- 🐳 Docker 測試環境支援
- 🧪 完整的測試套件（100% 測試通過率）
- 📚 完善的文件和使用說明
- 🔗 Claude Code 整合支援

### 技術實現
- 使用 FastMCP 框架建立 MCP 服務器
- 支援 Python 3.12+
- 使用 uv 作為套件管理器
- 包含完整的 Redmine REST API 客戶端
- 支援環境變數配置管理
- 實作友善的錯誤訊息和中文介面

### 文件
- 📖 README.md - 專案概述和快速開始指南
- 🚀 INSTALLATION.md - 詳細安裝指南
- 💡 USAGE_EXAMPLES.md - 實用範例和最佳實務
- 📋 API_REFERENCE.md - 完整的 API 參考文件
- 🧪 TESTING.md - 測試指南和說明

### 相容性
- Redmine 4.0+ (建議 5.0+)
- Claude Code MCP 整合
- 跨平台支援 (Windows, macOS, Linux)

---

## 版本規範說明

- **新增 (Added)** - 新功能
- **變更 (Changed)** - 現有功能的變更
- **已棄用 (Deprecated)** - 即將移除的功能
- **已移除 (Removed)** - 已移除的功能
- **修復 (Fixed)** - 錯誤修復
- **安全性 (Security)** - 安全性相關的變更

[未發布]: https://github.com/your-username/redmine-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-username/redmine-mcp/releases/tag/v0.1.0