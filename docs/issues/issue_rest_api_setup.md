# Issue: Redmine REST API 設定步驟補充

## 問題描述

用戶在設定 Redmine MCP 時，無法在「我的帳號」中找到 API 金鑰選項，這是因為 Redmine 預設沒有啟用 REST API 功能。

## 發現經過

1. 使用 admin/admin 登入 http://127.0.0.1:3000/
2. 在「我的帳號」頁面找不到 API 金鑰選項
3. 前往 http://127.0.0.1:3000/settings?tab=api
4. 勾選「啟用 REST 網路服務技術（Web Service）」
5. 執行儲存後，才能在「我的帳號」中找到 API 金鑰選項

## 解決方案

### 1. 更新 README.md
- 在第 4 節新增「4.1 啟用 REST API」步驟
- 明確說明需要管理員權限來啟用此功能
- 在故障排除區段加強相關說明

### 2. 設定步驟
```
4.1 啟用 REST API（需要管理員權限）
1. 以管理員身份登入 Redmine 系統
2. 前往 管理 → 設定 → API
3. 勾選「啟用 REST 網路服務技術（Web Service）」
4. 點擊儲存按鈕

4.2 取得 API 金鑰
1. 登入您的 Redmine 系統（可以是管理員或一般用戶）
2. 前往 我的帳號 → API 存取金鑰
3. 點擊 顯示 或 重設 來取得 API 金鑰
4. 將金鑰複製到 .env 檔案中的 REDMINE_API_KEY
```

## 影響

- 這是所有使用 Redmine MCP 的前置條件
- 如果沒有啟用 REST API，所有 MCP 工具都會失敗
- 需要管理員權限才能啟用此功能

## 狀態

✅ **已解決** - README.md 已更新，包含完整的設定步驟和故障排除指南

## 相關檔案

- `/README.md` - 主要文件，包含設定步驟
- `/docs/issues/issue_rest_api_setup.md` - 此問題記錄

## 建議

未來考慮在快速設定腳本 (`quick_start.sh`) 中加入檢查 REST API 是否啟用的功能，並提供相應的設定指導。