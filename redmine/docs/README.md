# Redmine 測試環境說明

本目錄包含了 Redmine MCP 專案的所有 Redmine 相關設定和管理工具。

## 📁 目錄結構

```
redmine/
├── docker/                    # Docker 相關設定
│   ├── docker-compose.yml     # MySQL 8.0 + Redmine 5.1 容器配置
│   └── init/                  # Docker 初始化腳本目錄
├── scripts/                   # 設定和管理腳本
│   ├── setup.sh              # 啟動 Redmine 環境
│   ├── configure.py           # 自動建立測試資料和 API 金鑰
│   ├── manual_api_setup.py    # 手動 API 設定和測試
│   └── enable_rest_api.py     # 啟用 REST API 功能
├── docs/                      # 設定說明文檔
│   ├── README.md             # 本檔案 - 總覽說明
│   ├── setup.md              # 詳細設定步驟
│   └── api.md                # API 使用說明
└── configs/                   # 配置模板
    └── .env.example          # 環境變數範例
```

## 🚀 快速開始

### 一鍵啟動（推薦）

```bash
# 從專案根目錄執行
./redmine/scripts/setup.sh
```

### 完整設定流程

```bash
# 1. 啟動 Redmine 環境
./redmine/scripts/setup.sh

# 2. 自動配置測試資料
cd redmine/scripts
python configure.py

# 3. 測試 API 連接
python manual_api_setup.py
```

## 🌐 服務資訊

### Redmine 實例
- **URL**: http://localhost:3000
- **管理員帳號**: admin
- **管理員密碼**: admin
- **版本**: Redmine 5.1

### 資料庫
- **類型**: MySQL 8.0
- **容器名稱**: redmine-mysql
- **內部端口**: 3306

### Docker 容器
- **redmine-app**: Redmine 應用服務 (端口 3000)
- **redmine-mysql**: MySQL 資料庫服務

## 📝 配置說明

### 環境變數
參考 `configs/.env.example` 建立你的 `.env` 檔案：

```bash
# 複製範例檔案
cp redmine/configs/.env.example .env

# 編輯配置
vim .env
```

### 測試資料
自動配置腳本會建立：
- 3 個測試專案
- 每個專案 5 個測試議題
- API 金鑰設定

## 🔧 管理指令

### 環境控制
```bash
# 啟動服務
cd redmine/docker
docker-compose up -d

# 檢查狀態
docker-compose ps

# 查看日誌
docker-compose logs redmine

# 停止服務
docker-compose down

# 完全清理（包含資料）
docker-compose down -v
```

### 重新設定
```bash
# 重設 Redmine 環境
cd redmine/docker
docker-compose down -v
cd ../scripts
./setup.sh
```

## 🧪 測試驗證

### API 連接測試
```bash
cd redmine/scripts
python manual_api_setup.py
```

### MCP 功能測試
```bash
# 從專案根目錄執行
python tests/scripts/mcp_integration.py
```

## 📚 更多說明

- [詳細設定步驟](setup.md) - 完整的環境建置說明
- [API 使用指南](api.md) - Redmine REST API 參考

## ⚠️ 注意事項

- 此環境僅供開發和測試使用
- 首次啟動需要約 60-90 秒進行資料庫初始化
- 請確保端口 3000 未被其他服務佔用
- 測試完成後請記得停止 Docker 容器以節省資源