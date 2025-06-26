# 測試目錄結構說明

這個目錄包含了 redmine-mcp 專案的所有測試檔案，組織成三個主要類別：

## 📁 目錄結構

```
tests/
├── unit/              # 單元測試 (pytest)
│   ├── test_config.py         # 配置管理測試
│   ├── test_redmine_client.py # Redmine 客戶端測試
│   └── test_validators.py     # 資料驗證測試
├── integration/       # 整合測試 (pytest)
│   ├── test_mcp_tools.py          # MCP 工具整合測試
│   └── test_advanced_mcp_tools.py # 進階 MCP 工具測試
└── scripts/          # 測試腳本 (直接執行)
    ├── claude_integration.py # Claude Code 整合測試
    ├── claude_setup.py       # Claude Code 設定測試
    ├── installation.py       # 套件安裝測試
    └── mcp_integration.py    # 完整 MCP 功能測試
```

## 🧪 測試類型

### 單元測試 (Unit Tests)
- **目的**: 測試個別模組和函數的功能
- **特點**: 獨立、快速、可重複
- **框架**: pytest
- **執行**: `uv run python -m pytest tests/unit/`

### 整合測試 (Integration Tests)  
- **目的**: 測試不同模組間的互動
- **特點**: 需要外部服務（如 Redmine）
- **框架**: pytest + mock
- **執行**: `uv run python -m pytest tests/integration/`

### 測試腳本 (Test Scripts)
- **目的**: 端到端功能驗證和環境設定
- **特點**: 獨立執行、包含設定邏輯
- **框架**: 原生 Python
- **執行**: `uv run python tests/scripts/<script_name>.py`

## 🚀 快速開始

### 執行所有測試
```bash
# 執行所有 pytest 測試
uv run python -m pytest tests/

# 執行完整功能測試
uv run python tests/scripts/mcp_integration.py
```

### 執行特定類型測試
```bash
# 只執行單元測試
uv run python -m pytest tests/unit/

# 只執行整合測試  
uv run python -m pytest tests/integration/

# 測試 Claude Code 整合
uv run python tests/scripts/claude_integration.py

# 測試套件安裝
uv run python tests/scripts/installation.py
```

### 開發時測試流程
```bash
# 1. 修改程式碼後先執行單元測試
uv run python -m pytest tests/unit/ -v

# 2. 如果通過，執行整合測試
uv run python -m pytest tests/integration/ -v

# 3. 最後執行完整功能測試
uv run python tests/scripts/mcp_integration.py
```

## 📝 測試檔案說明

### 單元測試檔案

#### `test_config.py`
- 測試配置管理模組 (`config.py`)
- 驗證環境變數讀取和驗證邏輯
- 測試新的專屬環境變數機制

#### `test_redmine_client.py`
- 測試 Redmine API 客戶端 (`redmine_client.py`)
- Mock HTTP 請求和回應
- 驗證錯誤處理機制

#### `test_validators.py`
- 測試資料驗證器 (`validators.py`)
- 驗證輸入資料格式和範圍檢查
- 測試錯誤訊息生成

### 整合測試檔案

#### `test_mcp_tools.py`
- 測試 MCP 工具的基本功能
- 模擬 Redmine 服務回應
- 驗證工具間的資料流

#### `test_advanced_mcp_tools.py`
- 測試進階 MCP 工具功能
- 複雜情境和邊界條件測試
- 效能和穩定性驗證

### 測試腳本檔案

#### `claude_integration.py`
- 測試與 Claude Code 的整合
- 驗證 MCP 伺服器可執行性
- 檢查工具註冊和可用性

#### `claude_setup.py`
- 測試 Claude Code MCP 配置
- 驗證配置檔案生成
- 測試環境變數設定

#### `installation.py`
- 測試套件安裝和導入
- 驗證命令列工具可用性
- 檢查相依套件

#### `mcp_integration.py`
- 完整的端到端功能測試
- 需要運行中的 Redmine 服務
- 測試所有 14 個 MCP 工具

## 🔧 環境需求

### 單元測試
- Python 3.12+
- pytest
- 相關 mock 套件

### 整合測試
- 單元測試的所有需求
- 可選的 Redmine 服務（使用 mock 時不需要）

### 測試腳本
- 完整的開發環境
- Docker 和 Docker Compose（用於 Redmine 服務）
- 網路連線（用於 Claude Code 整合測試）

## 📊 測試覆蓋率

使用 pytest-cov 來檢查測試覆蓋率：

```bash
# 安裝覆蓋率工具
uv add --dev pytest-cov

# 執行測試並生成覆蓋率報告
uv run python -m pytest tests/ --cov=src/redmine_mcp --cov-report=html

# 檢視覆蓋率報告
open htmlcov/index.html
```

## 🐛 故障排除

### 常見問題

**Q: pytest 找不到模組**
```bash
# 確保從專案根目錄執行
cd /path/to/redmine-mcp
uv run python -m pytest tests/
```

**Q: 整合測試失敗**
- 檢查是否需要啟動 Redmine 服務
- 確認網路連線和 API 金鑰設定

**Q: 測試腳本執行錯誤**
- 檢查 import 路徑是否正確
- 確認所有相依套件已安裝

### 除錯技巧

```bash
# 執行特定測試檔案
uv run python -m pytest tests/unit/test_config.py -v

# 執行特定測試函數
uv run python -m pytest tests/unit/test_config.py::TestRedmineConfig::test_config_with_valid_env -v

# 顯示詳細輸出
uv run python -m pytest tests/ -v -s

# 在第一個失敗時停止
uv run python -m pytest tests/ -x
```

## 🚀 持續整合

在 CI/CD 流程中，建議執行順序：

1. **快速檢查**: 單元測試
2. **深度驗證**: 整合測試
3. **最終確認**: 關鍵測試腳本

```bash
# CI 流程範例
uv run python -m pytest tests/unit/ --maxfail=5
uv run python -m pytest tests/integration/ --maxfail=3
uv run python tests/scripts/installation.py
```