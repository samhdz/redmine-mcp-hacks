#!/bin/bash
#
# Redmine MCP 快速啟動腳本
# ============================
# 
# 這個腳本會自動執行以下步驟：
# 1. 檢查 Docker 環境
# 2. 啟動 Redmine 測試環境 (http://localhost:3000)
# 3. 建立測試專案和 API 金鑰
# 4. 執行完整的 MCP 功能測試
#
# 適用場景：
# - 新開發者第一次設定環境
# - 發布前的完整功能驗證
# - CI/CD 自動化測試
# - 環境重置後的驗證
#
# 執行時間：約 2-3 分鐘
# 前置需求：Docker, Docker Compose, uv

echo "🚀 Redmine MCP 快速啟動"
echo "=" * 50

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安裝，請先安裝 Docker Compose"
    exit 1
fi

echo "✅ Docker 環境檢查通過"

# 步驟 1: 啟動 Redmine
echo ""
echo "🚀 步驟 1: 啟動 Redmine 環境"
echo "----------------------------------------"
./redmine/scripts/setup.sh

# 步驟 2: 配置 Redmine
echo ""
echo "🔧 步驟 2: 配置 Redmine 測試資料"
echo "----------------------------------------"
uv run python redmine/scripts/configure.py

if [ $? -ne 0 ]; then
    echo "❌ Redmine 配置失敗"
    exit 1
fi

# 步驟 3: 測試 MCP 整合
echo ""
echo "🧪 步驟 3: 執行 MCP 功能測試"
echo "----------------------------------------"
uv run python tests/scripts/mcp_integration.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 所有測試完成！"
    echo "----------------------------------------"
    echo "✅ Redmine 環境已啟動: http://localhost:3000"
    echo "✅ MCP 功能測試通過"
    echo "✅ 環境已準備好進行開發和測試"
    echo ""
    echo "💡 接下來可以:"
    echo "   - 在 Claude Code 中配置並測試 MCP 工具"
    echo "   - 繼續開發新的 MCP 功能"
    echo "   - 執行 'cd redmine/docker && docker-compose down' 關閉測試環境"
else
    echo ""
    echo "❌ MCP 測試失敗，請檢查上述錯誤訊息"
    exit 1
fi