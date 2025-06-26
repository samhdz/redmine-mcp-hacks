#!/bin/bash

echo "🚀 正在啟動 Redmine 開發環境..."

# 啟動 Docker 服務
echo "📦 啟動 Docker 容器..."
cd "$(dirname "$0")/../docker"
docker-compose up -d

echo "⏳ 等待 Redmine 啟動（約 60 秒）..."
sleep 60

# 檢查 Redmine 是否啟動
echo "🔍 檢查 Redmine 狀態..."
until curl -f http://localhost:3000 > /dev/null 2>&1; do
    echo "等待 Redmine 完全啟動..."
    sleep 5
done

echo "✅ Redmine 已啟動！"
echo ""
echo "📋 Redmine 資訊:"
echo "   - URL: http://localhost:3000"
echo "   - 預設管理員帳號: admin"
echo "   - 預設密碼: admin"
echo ""
echo "🔧 接下來的設定步驟:"
echo "1. 開啟瀏覽器前往 http://localhost:3000"
echo "2. 使用 admin/admin 登入"
echo "3. 前往 我的帳戶 > API 存取金鑰"
echo "4. 點擊 '顯示' 取得 API 金鑰"
echo "5. 建立測試專案和議題"
echo ""
echo "💡 或執行以下指令進行自動設定:"
echo "   python configure.py"