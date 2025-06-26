# Redmine 環境設定詳細說明

本文件提供 Redmine 測試環境的詳細設定步驟和故障排除說明。

## 📋 前置需求

### 系統需求
- **作業系統**: macOS, Linux, Windows (with WSL2)
- **記憶體**: 至少 2GB 可用
- **磁碟空間**: 至少 1GB
- **網路**: 需要網際網路連線下載 Docker 映像

### 必要軟體
- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0 (或 docker-compose >= 1.29)
- **Python**: >= 3.8 (用於設定腳本)
- **curl**: 用於健康檢查

### 檢查安裝
```bash
# 檢查 Docker
docker --version
docker-compose --version  # 或 docker compose version

# 檢查 Python
python3 --version

# 檢查 curl
curl --version
```

## 🚀 安裝步驟

### 步驟 1: 準備環境

```bash
# 確保沒有其他服務佔用端口 3000
lsof -i :3000

# 如果有服務在運行，停止它
sudo kill -9 $(lsof -ti:3000)
```

### 步驟 2: 啟動 Redmine

```bash
# 方法 1: 使用便捷腳本（推薦）
./redmine/scripts/setup.sh

# 方法 2: 手動啟動
cd redmine/docker
docker-compose up -d
```

### 步驟 3: 驗證啟動

```bash
# 檢查容器狀態
docker-compose ps

# 檢查 Redmine 日誌
docker-compose logs redmine

# 測試 Web 介面
curl -I http://localhost:3000
```

預期輸出：
```
HTTP/1.1 200 OK
```

### 步驟 4: 初始設定

#### 4.1 Web 介面設定
1. 開啟瀏覽器前往 http://localhost:3000
2. 使用帳號密碼 `admin` / `admin` 登入
3. 首次登入時會要求更改密碼（可跳過）

#### 4.2 API 設定
```bash
# 自動設定（推薦）
cd redmine/scripts
python configure.py

# 手動設定
python manual_api_setup.py
```

### 步驟 5: 建立測試資料

自動設定腳本會建立：
- **MCP 測試專案** (`mcp-test`)
- **軟體開發** (`software-dev`)  
- **Bug 追蹤** (`bug-tracking`)

每個專案包含 5 個不同狀態的測試議題。

## ⚙️ 詳細配置

### Docker Compose 說明

```yaml
# redmine/docker/docker-compose.yml
version: '3.8'

services:
  redmine-db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: redmine
      MYSQL_USER: redmine
      MYSQL_PASSWORD: redmine_password
    volumes:
      - redmine_db_data:/var/lib/mysql
      
  redmine:
    image: redmine:5.1
    ports:
      - "3000:3000"
    environment:
      REDMINE_DB_MYSQL: redmine-db
      REDMINE_DB_USERNAME: redmine
      REDMINE_DB_PASSWORD: redmine_password
      REDMINE_DB_DATABASE: redmine
      REDMINE_SECRET_KEY_BASE: supersecretkey
    volumes:
      - redmine_data:/usr/src/redmine/files
      - redmine_plugins:/usr/src/redmine/plugins
      - ./init:/docker-entrypoint-initdb.d
```

### 環境變數設定

```bash
# 複製範例配置
cp redmine/configs/.env.example .env

# 編輯配置（可選）
vim .env
```

範例內容：
```bash
REDMINE_DOMAIN=http://localhost:3000
REDMINE_API_KEY=your_api_key_here
REDMINE_MCP_TIMEOUT=30
REDMINE_MCP_LOG_LEVEL=INFO
```

## 🔧 進階設定

### 修改端口

如果端口 3000 被佔用：

```yaml
# 編輯 redmine/docker/docker-compose.yml
services:
  redmine:
    ports:
      - "3001:3000"  # 改為其他端口
```

對應的環境變數也需要更新：
```bash
REDMINE_DOMAIN=http://localhost:3001
```

### 資料持久化

Docker 卷會自動建立：
- `redmine_db_data`: 資料庫資料
- `redmine_data`: Redmine 檔案
- `redmine_plugins`: Redmine 插件

### 自訂初始化

在 `redmine/docker/init/` 目錄放置初始化腳本：
```bash
# 範例：建立初始用戶
echo "CREATE USER 'testuser'@'%' IDENTIFIED BY 'testpass';" > redmine/docker/init/01-users.sql
```

## 🐛 故障排除

### 常見問題

#### Q1: Docker 容器啟動失敗
```bash
# 檢查 Docker 服務狀態
docker info

# 檢查端口佔用
lsof -i :3000

# 查看詳細錯誤
docker-compose logs
```

#### Q2: Redmine 啟動時間過長
```bash
# 正常啟動需要 60-90 秒，可查看進度
docker-compose logs -f redmine
```

預期的啟動日誌：
```
redmine-app | => Booting WEBrick
redmine-app | => Rails 6.1.4 application starting
redmine-app | => Creating database
redmine-app | => Migrating database
redmine-app | => Rails application started on 0.0.0.0:3000
```

#### Q3: 無法連接到 Redmine
```bash
# 檢查容器狀態
docker-compose ps

# 測試網路連接
curl -v http://localhost:3000

# 檢查防火牆設定（macOS）
sudo pfctl -s all
```

#### Q4: API 設定失敗
```bash
# 手動取得 API 金鑰
# 1. 登入 http://localhost:3000
# 2. 前往 我的帳戶 > API 存取金鑰
# 3. 點擊 '顯示'

# 測試 API 連接
python redmine/scripts/manual_api_setup.py
```

#### Q5: 資料庫連接錯誤
```bash
# 檢查 MySQL 容器
docker-compose logs redmine-db

# 重啟 MySQL 容器
docker-compose restart redmine-db

# 完全重建
docker-compose down -v
docker-compose up -d
```

### 日誌分析

#### 查看所有服務日誌
```bash
docker-compose logs
```

#### 查看特定服務日誌
```bash
# Redmine 應用日誌
docker-compose logs redmine

# MySQL 資料庫日誌
docker-compose logs redmine-db

# 實時追蹤日誌
docker-compose logs -f redmine
```

### 效能調整

#### 分配更多記憶體
```yaml
# 編輯 docker-compose.yml
services:
  redmine:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

#### 使用 SSD 儲存
```bash
# 確保 Docker 資料位於 SSD
docker info | grep "Docker Root Dir"
```

## 🔄 重設環境

### 完全重設
```bash
# 停止並刪除所有容器和資料
cd redmine/docker
docker-compose down -v

# 清理 Docker 資源
docker system prune -f

# 重新啟動
cd ../scripts
./setup.sh
```

### 保留資料重啟
```bash
cd redmine/docker
docker-compose restart
```

### 只重建 Redmine 容器
```bash
cd redmine/docker
docker-compose up -d --force-recreate redmine
```

## 📊 健康檢查

建立健康檢查腳本：
```bash
#!/bin/bash
# redmine/scripts/health_check.sh

echo "🔍 Redmine 健康檢查"
echo "==================="

# 檢查容器狀態
echo "📦 容器狀態:"
docker-compose -f redmine/docker/docker-compose.yml ps

# 檢查網路連接
echo ""
echo "🌐 網路連接:"
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Redmine Web 介面正常"
else
    echo "❌ Redmine Web 介面無法連接"
fi

# 檢查 API
echo ""
echo "🔌 API 連接:"
if [ -f .env ]; then
    source .env
    if [ ! -z "$REDMINE_API_KEY" ]; then
        if curl -s -H "X-Redmine-API-Key: $REDMINE_API_KEY" http://localhost:3000/projects.json > /dev/null; then
            echo "✅ Redmine API 正常"
        else
            echo "❌ Redmine API 無法連接"
        fi
    else
        echo "⚠️  API 金鑰未設定"
    fi
else
    echo "⚠️  .env 檔案不存在"
fi
```

## 🚀 自動化部署

建立自動化部署腳本：
```bash
#!/bin/bash
# redmine/scripts/deploy.sh

set -e

echo "🚀 自動化 Redmine 部署"
echo "====================="

# 檢查前置需求
./redmine/scripts/health_check.sh

# 啟動環境
./redmine/scripts/setup.sh

# 配置資料
cd redmine/scripts
python configure.py

# 驗證安裝
python manual_api_setup.py

echo "✅ Redmine 環境部署完成！"
```

## 📝 開發工作流程

### 日常開發
```bash
# 1. 啟動環境
./redmine/scripts/setup.sh

# 2. 開發 MCP 功能
vim src/redmine_mcp/server.py

# 3. 測試功能
python tests/scripts/mcp_integration.py

# 4. 停止環境
cd redmine/docker
docker-compose down
```

### 版本升級
```bash
# 1. 備份資料
docker run --rm -v redmine_db_data:/source -v $(pwd):/backup alpine tar czf /backup/redmine_backup.tar.gz -C /source .

# 2. 更新映像版本
# 編輯 docker-compose.yml 中的版本號

# 3. 重建服務
docker-compose down
docker-compose pull
docker-compose up -d
```