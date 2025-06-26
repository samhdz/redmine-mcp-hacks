# 安裝指南

本文件提供 Redmine MCP Server 的詳細安裝步驟和設定說明。

## 📋 目錄

1. [系統需求](#系統需求)
2. [安裝方式](#安裝方式)
3. [環境設定](#環境設定)
4. [Claude Code 整合](#claude-code-整合)
5. [驗證安裝](#驗證安裝)
6. [故障排除](#故障排除)

## 🖥️ 系統需求

### 基本需求

- **作業系統**: Windows 10+, macOS 10.14+, 或 Linux (Ubuntu 18.04+)
- **Python**: 3.12 或更高版本
- **網路**: 能存取 Redmine 服務器的網路連線

### Redmine 伺服器需求

- **Redmine 版本**: 4.0 或更高版本（建議 5.0+）
- **REST API**: 必須啟用 REST API 功能
- **用戶權限**: 具有 API 存取權限的用戶帳號

### 套件管理器

建議使用以下任一套件管理器：

1. **uv** (推薦) - 高效能的 Python 套件管理器
   ```bash
   # 安裝 uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **pip** - Python 內建套件管理器
   ```bash
   # 通常已隨 Python 安裝
   python -m pip --version
   ```

## 📦 安裝方式

### 方式一：從原始碼安裝（推薦）

#### 步驟 1: 克隆專案

```bash
# 克隆專案儲存庫
git clone https://github.com/your-username/redmine-mcp.git
cd redmine-mcp
```

#### 步驟 2: 安裝依賴

使用 uv（推薦）：
```bash
# 建立虛擬環境並安裝依賴
uv sync

# 或者僅安裝依賴到現有環境
uv pip install -e .
```

使用 pip：
```bash
# 建立虛擬環境（可選但建議）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝專案
pip install -e .
```

### 方式二：透過 PyPI 安裝

```bash
# 使用 uv
uv pip install redmine-mcp

# 使用 pip
pip install redmine-mcp
```

### 方式三：開發者安裝

```bash
# 克隆專案
git clone https://github.com/your-username/redmine-mcp.git
cd redmine-mcp

# 安裝開發依賴
uv sync --all-extras
# 或
pip install -e ".[dev,test]"
```

## ⚙️ 環境設定

### 步驟 1: 建立環境設定檔

```bash
# 複製環境變數範本
cp .env.example .env
```

### 步驟 2: 設定環境變數

編輯 `.env` 檔案：

```env
# Redmine 服務器網域（必填）
REDMINE_DOMAIN=https://your-redmine-domain.com

# Redmine API 金鑰（必填）
REDMINE_API_KEY=your_api_key_here

# API 請求逾時時間（可選，預設 30 秒）
REDMINE_TIMEOUT=30

# 除錯模式（可選，預設 false）
DEBUG_MODE=false
```

### 步驟 3: 取得 Redmine API 金鑰

#### 方法一：透過 Redmine 網頁介面

1. 登入您的 Redmine 系統
2. 點擊右上角的用戶名稱
3. 選擇「我的帳號」
4. 在右側面板找到「API 存取金鑰」
5. 點擊「顯示」或「重設」
6. 複製顯示的 API 金鑰

#### 方法二：聯絡管理員

如果您無法看到 API 存取金鑰選項：

1. 聯絡 Redmine 系統管理員
2. 請求啟用 REST API 功能
3. 請求為您的帳號產生 API 金鑰

### 步驟 4: 驗證 Redmine 設定

確認 Redmine 服務器已正確設定：

#### 檢查 REST API 是否啟用

1. 登入 Redmine 管理介面
2. 前往「管理」→「設定」→「API」
3. 確認「啟用 REST Web 服務」已勾選
4. 儲存設定

#### 測試 API 連線

```bash
# 使用 curl 測試 API 連線
curl -H "X-Redmine-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     https://your-redmine-domain.com/issues.json?limit=1
```

預期回應應包含 JSON 格式的議題資料。

## 🔗 Claude Code 整合

### 步驟 1: 安裝 MCP 服務器

```bash
# 安裝為系統工具
uv tool install .

# 或使用 pip
pip install .
```

### 步驟 2: 新增到 Claude Code

#### 方法一：使用命令列

```bash
claude mcp add redmine "redmine-mcp" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here"
```

#### 方法二：手動編輯設定檔

編輯 Claude Code 的 MCP 設定檔案：

**macOS/Linux 位置：**
```
~/.config/claude-code/mcp_servers.json
```

**Windows 位置：**
```
%APPDATA%\claude-code\mcp_servers.json
```

**設定內容：**
```json
{
  "servers": {
    "redmine": {
      "command": "redmine-mcp",
      "env": {
        "REDMINE_DOMAIN": "https://your-redmine-domain.com",
        "REDMINE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 步驟 3: 重啟 Claude Code

重新啟動 Claude Code 以載入新的 MCP 服務器設定。

## ✅ 驗證安裝

### 測試 1: MCP 服務器測試

```bash
# 測試 MCP 服務器是否正常運作
uv run python -m redmine_mcp.server

# 如果看到服務器啟動訊息而無錯誤，表示安裝成功
```

### 測試 2: Claude Code 整合測試

```bash
# 執行 Claude Code 整合測試
uv run python test_claude_integration.py
```

預期輸出：
```
✅ MCP 服務器啟動成功
✅ 服務器資訊取得成功
✅ 健康檢查通過
✅ 工具列表載入成功 (14 個工具)
```

### 測試 3: 完整功能測試

```bash
# 執行完整的 MCP 功能測試
uv run python test_mcp_integration.py
```

預期看到所有測試項目都通過：
```
📊 測試結果摘要
==================================================
總測試數: 13
通過: 13
失敗: 0
成功率: 100.0%

🎉 測試通過！MCP 功能運作正常
```

### 測試 4: Claude Code 中的手動測試

在 Claude Code 中輸入：

```
請執行健康檢查
```

如果看到類似以下回應，表示整合成功：
```
✓ 服務器正常運作，已連接到 https://your-redmine-domain.com
```

## 🔧 故障排除

### 常見問題 1: Python 版本不相容

**錯誤訊息：**
```
Python 3.12 or higher is required
```

**解決方案：**
```bash
# 檢查 Python 版本
python --version

# 如果版本過舊，請升級 Python
# macOS 使用 Homebrew
brew install python@3.12

# Ubuntu/Debian
sudo apt update
sudo apt install python3.12

# Windows 請到 python.org 下載最新版本
```

### 常見問題 2: uv 找不到

**錯誤訊息：**
```
uv: command not found
```

**解決方案：**
```bash
# 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新載入 shell 設定
source ~/.bashrc  # 或 ~/.zshrc
```

### 常見問題 3: API 金鑰無效

**錯誤訊息：**
```
認證失敗：請檢查 API 金鑰是否正確
```

**解決方案：**
1. 確認 `.env` 檔案中的 `REDMINE_API_KEY` 正確
2. 檢查 Redmine 中的 API 金鑰是否仍然有效
3. 確認 API 金鑰對應的用戶有足夠權限

### 常見問題 4: REST API 未啟用

**錯誤訊息：**
```
權限不足：您沒有執行此操作的權限
```

**解決方案：**
1. 聯絡 Redmine 管理員確認 REST API 已啟用
2. 確認您的用戶帳號有 API 存取權限
3. 檢查用戶在相關專案中的權限設定

### 常見問題 5: 網路連線問題

**錯誤訊息：**
```
連線失敗：請檢查網路連線和 Redmine 伺服器狀態
```

**解決方案：**
1. 檢查網路連線
2. 確認 Redmine 服務器 URL 正確
3. 檢查防火牆設定
4. 嘗試增加逾時時間：
   ```env
   REDMINE_TIMEOUT=60
   ```

### 常見問題 6: Claude Code 無法載入 MCP 服務器

**解決方案：**
1. 檢查 MCP 設定檔案格式是否正確
2. 確認 `redmine-mcp` 命令可在命令列中執行
3. 重啟 Claude Code
4. 檢查 Claude Code 錯誤日誌

### 除錯技巧

#### 啟用除錯模式

在 `.env` 檔案中設定：
```env
DEBUG_MODE=true
```

#### 檢查設定載入

```bash
# 執行設定檢查
uv run python -c "
from redmine_mcp.config import get_config
config = get_config()
print(f'Domain: {config.redmine_domain}')
print(f'API Key: {config.redmine_api_key[:10]}...')
print(f'Timeout: {config.redmine_timeout}')
"
```

#### 手動測試 API 連線

```bash
# 執行連線測試腳本
uv run python debug_auth.py
```

## 🔄 升級指南

### 從舊版本升級

```bash
# 更新原始碼
git pull origin main

# 更新依賴
uv sync

# 或使用 pip
pip install -e . --upgrade
```

### 檢查設定相容性

升級後請檢查：
1. `.env` 檔案格式是否需要更新
2. 新版本是否有新的設定選項
3. Claude Code MCP 設定是否需要調整

## 📖 下一步

安裝完成後，建議閱讀：

1. [使用範例](USAGE_EXAMPLES.md) - 學習如何使用各種功能
2. [API 參考](API_REFERENCE.md) - 詳細的工具參數說明
3. [README.md](../README.md) - 專案概述和快速開始

如有任何安裝問題，歡迎開啟 Issue 尋求協助。