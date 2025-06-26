# Redmine REST API 使用指南

本文件說明如何使用 Redmine REST API 進行各種操作，以及與 MCP 工具的整合。

## 🔑 API 認證

### 取得 API 金鑰

#### 自動取得（推薦）
```bash
cd redmine/scripts
python configure.py
```

#### 手動取得
1. 登入 Redmine: http://localhost:3000
2. 使用 `admin` / `admin` 登入
3. 前往 **我的帳戶** > **API 存取金鑰**
4. 點擊 **顯示** 按鈕
5. 複製顯示的金鑰

#### 手動測試
```bash
cd redmine/scripts
python manual_api_setup.py
```

### API 金鑰格式
```
範例: a1b2c3d4e5f6789012345678901234567890abcd
長度: 40 字元的十六進位字串
```

## 📡 API 端點

### 基本設定

#### HTTP 標頭
```http
X-Redmine-API-Key: your_api_key_here
Content-Type: application/json
Accept: application/json
```

#### 基礎 URL
```
http://localhost:3000
```

### 專案 (Projects)

#### 取得所有專案
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/projects.json
```

#### 取得特定專案
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/projects/mcp-test.json
```

#### 建立專案
```bash
curl -X POST \
     -H "X-Redmine-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "project": {
         "name": "測試專案",
         "identifier": "test-project",
         "description": "這是一個測試專案"
       }
     }' \
     http://localhost:3000/projects.json
```

### 議題 (Issues)

#### 取得所有議題
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/issues.json
```

#### 取得特定議題
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/issues/1.json
```

#### 建立議題
```bash
curl -X POST \
     -H "X-Redmine-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "issue": {
         "project_id": 1,
         "subject": "測試議題",
         "description": "這是一個測試議題的描述"
       }
     }' \
     http://localhost:3000/issues.json
```

#### 更新議題
```bash
curl -X PUT \
     -H "X-Redmine-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "issue": {
         "subject": "更新的議題標題",
         "notes": "添加備註"
       }
     }' \
     http://localhost:3000/issues/1.json
```

#### 關閉議題
```bash
curl -X PUT \
     -H "X-Redmine-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "issue": {
         "status_id": 5,
         "done_ratio": 100,
         "notes": "議題已完成"
       }
     }' \
     http://localhost:3000/issues/1.json
```

### 議題狀態 (Issue Statuses)

#### 取得所有狀態
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/issue_statuses.json
```

預期回應：
```json
{
  "issue_statuses": [
    {"id": 1, "name": "新建"},
    {"id": 2, "name": "進行中"},
    {"id": 3, "name": "已解決"},
    {"id": 4, "name": "意見反應"},
    {"id": 5, "name": "關閉"},
    {"id": 6, "name": "拒絕"}
  ]
}
```

### 用戶 (Users)

#### 取得當前用戶
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/users/current.json
```

#### 取得所有用戶
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/users.json
```

## 🔍 進階查詢

### 篩選和排序

#### 按專案篩選議題
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?project_id=1"
```

#### 按狀態篩選
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?status_id=open"
```

#### 分頁查詢
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?limit=10&offset=0"
```

#### 排序
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?sort=updated_on:desc"
```

#### 搜尋
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?subject=~測試"
```

### 包含關聯資料

#### 包含專案資訊
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?include=project"
```

#### 包含多種資訊
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues/1.json?include=journals,watchers,attachments"
```

## 🛠️ MCP 工具整合

### 可用的 MCP 工具

#### 基本查詢工具
- `server_info`: 伺服器資訊
- `health_check`: 健康檢查
- `get_projects`: 取得專案列表
- `get_issue_statuses`: 取得議題狀態

#### 議題管理工具
- `get_issue`: 取得議題詳情
- `list_project_issues`: 列出專案議題
- `search_issues`: 搜尋議題
- `get_my_issues`: 取得我的議題

#### 議題操作工具
- `create_new_issue`: 建立新議題
- `update_issue_content`: 更新議題內容
- `update_issue_status`: 更新議題狀態
- `add_issue_note`: 新增議題備註
- `assign_issue`: 指派議題
- `close_issue`: 關閉議題

### MCP 工具範例

#### 使用 Python 直接呼叫
```python
from src.redmine_mcp.server import get_projects, create_new_issue

# 取得專案列表
projects = get_projects()
print(projects)

# 建立新議題
issue = create_new_issue(
    project_id=1,
    subject="透過 MCP 建立的議題",
    description="這是使用 MCP 工具建立的測試議題"
)
print(issue)
```

#### 在 Claude Code 中使用
1. 設定 MCP 配置
2. 使用自然語言指令：
   - "幫我建立一個新的議題"
   - "列出所有開放的議題"
   - "更新議題 #5 的狀態為已完成"

## 📊 API 回應格式

### 成功回應
```json
{
  "issue": {
    "id": 1,
    "project": {
      "id": 1,
      "name": "MCP 測試專案"
    },
    "subject": "測試議題",
    "description": "議題描述",
    "status": {
      "id": 1,
      "name": "新建"
    },
    "priority": {
      "id": 2,
      "name": "普通"
    },
    "author": {
      "id": 1,
      "name": "admin"
    },
    "created_on": "2024-01-01T10:00:00Z",
    "updated_on": "2024-01-01T10:00:00Z"
  }
}
```

### 錯誤回應
```json
{
  "errors": [
    "主題不能為空白"
  ]
}
```

## 🚨 錯誤處理

### 常見 HTTP 狀態碼

| 狀態碼 | 說明 | 解決方案 |
|--------|------|----------|
| 200 | 成功 | - |
| 201 | 已建立 | - |
| 401 | 未授權 | 檢查 API 金鑰 |
| 403 | 禁止存取 | 檢查用戶權限 |
| 404 | 找不到 | 檢查資源 ID |
| 422 | 驗證錯誤 | 檢查必要欄位 |
| 500 | 伺服器錯誤 | 檢查 Redmine 日誌 |

### 除錯技巧

#### 啟用詳細日誌
```bash
export REDMINE_MCP_LOG_LEVEL=DEBUG
```

#### 檢查 API 回應
```bash
curl -v -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/projects.json
```

#### 檢查 Redmine 日誌
```bash
cd redmine/docker
docker-compose logs redmine | grep -i error
```

## 🔒 安全性考量

### API 金鑰保護
- 不要在程式碼中硬編碼 API 金鑰
- 使用環境變數儲存敏感資訊
- 定期更換 API 金鑰

### 權限控制
- 為不同用途建立不同的用戶
- 設定適當的專案權限
- 使用最小權限原則

### 網路安全
- 在生產環境中使用 HTTPS
- 設定防火牆規則
- 監控 API 使用情況

## 📈 效能最佳化

### 批次操作
```python
# 避免：逐一建立議題
for i in range(100):
    create_issue(f"議題 {i}")

# 建議：使用批次 API（如果可用）
batch_create_issues(issue_list)
```

### 快取常用資料
```python
# 快取專案列表
projects_cache = get_projects()

# 快取議題狀態
statuses_cache = get_issue_statuses()
```

### 分頁處理
```python
def get_all_issues():
    issues = []
    offset = 0
    limit = 100
    
    while True:
        page = list_issues(limit=limit, offset=offset)
        if not page:
            break
        issues.extend(page)
        offset += limit
    
    return issues
```

## 📚 參考資源

### 官方文件
- [Redmine REST API 文件](https://www.redmine.org/projects/redmine/wiki/Rest_api)
- [Redmine 使用手冊](https://www.redmine.org/projects/redmine/wiki/User_Guide)

### 社群資源
- [Redmine 論壇](https://www.redmine.org/boards)
- [Redmine GitHub](https://github.com/redmine/redmine)

### 相關工具
- [Postman Redmine 集合](https://www.postman.com/collections)
- [Redmine Python 客戶端](https://pypi.org/project/python-redmine/)

## 🧪 測試 API

### 測試腳本
```python
#!/usr/bin/env python3
"""
API 功能測試腳本
"""
import requests
import json

API_KEY = "your_api_key_here"
BASE_URL = "http://localhost:3000"
HEADERS = {
    "X-Redmine-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_api():
    # 測試連接
    response = requests.get(f"{BASE_URL}/projects.json", headers=HEADERS)
    assert response.status_code == 200
    
    # 測試建立專案
    project_data = {
        "project": {
            "name": "API 測試專案",
            "identifier": "api-test"
        }
    }
    response = requests.post(f"{BASE_URL}/projects.json", 
                           headers=HEADERS, 
                           json=project_data)
    assert response.status_code == 201
    
    print("✅ API 測試通過")

if __name__ == "__main__":
    test_api()
```

### 執行測試
```bash
cd redmine/scripts
python api_test.py
```