#!/usr/bin/env python3
"""
Redmine 自動配置腳本
用於建立測試專案、議題和用戶
"""

import requests
import json
import time
import sys
import re
from typing import Optional


class RedmineConfigurator:
    def __init__(self, url: str = "http://localhost:3000", username: str = "admin", password: str = "admin"):
        self.url = url.rstrip('/')
        self.session = requests.Session()
        self.api_key: Optional[str] = None
        
        # 登入取得 API 金鑰
        self._login(username, password)
    
    def _login(self, username: str, password: str):
        """登入並取得 API 金鑰"""
        print(f"🔐 正在登入 Redmine ({username})...")
        
        # 首先取得 CSRF token
        response = self.session.get(f"{self.url}/login")
        if response.status_code != 200:
            raise Exception(f"無法存取 Redmine: {response.status_code}")
        
        # 解析 CSRF token
        csrf_match = re.search(r'name="authenticity_token" value="([^"]+)"', response.text)
        if not csrf_match:
            raise Exception("找不到 CSRF token")
        
        csrf_token = csrf_match.group(1)
        
        # 執行登入
        login_data = {
            'username': username,
            'password': password,
            'authenticity_token': csrf_token
        }
        
        response = self.session.post(f"{self.url}/login", data=login_data, allow_redirects=False)
        
        if response.status_code not in [302, 200]:
            raise Exception(f"登入失敗: {response.status_code}")
        
        print("✅ 登入成功")
        
        # 取得或建立 API 金鑰
        self._get_or_create_api_key()
    
    def _get_or_create_api_key(self):
        """取得或建立 API 金鑰"""
        print("🔑 正在取得 API 金鑰...")
        
        # 前往我的帳戶頁面
        response = self.session.get(f"{self.url}/my/account")
        if response.status_code != 200:
            print(f"⚠️  無法存取帳戶頁面: {response.status_code}")
            self._use_fallback_api_key()
            return
            
        # 列印部分回應內容以便除錯
        print(f"📄 帳戶頁面回應長度: {len(response.text)} 字元")
        
        # 尋找現有的 API 金鑰（支援中英文界面）
        api_patterns = [
            r'API 存取金鑰.*?([a-f0-9]{40})',
            r'API access key.*?([a-f0-9]{40})',
            r'api.*?key.*?([a-f0-9]{40})',
            r'([a-f0-9]{40})'  # 任何 40 位 hex 字串
        ]
        
        for pattern in api_patterns:
            key_match = re.search(pattern, response.text, re.IGNORECASE | re.DOTALL)
            if key_match:
                self.api_key = key_match.group(1)
                print(f"✅ 找到現有 API 金鑰: {self.api_key[:8]}...")
                return
        
        # 如果沒有找到，嘗試重設 API 金鑰
        print("🔄 嘗試重設 API 金鑰...")
        csrf_match = re.search(r'name="authenticity_token" value="([^"]+)"', response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"🎫 找到 CSRF token: {csrf_token[:8]}...")
            
            # 嘗試重設 API 金鑰
            reset_endpoints = [
                f"{self.url}/my/api_key",
                f"{self.url}/my/account/reset_api_key"
            ]
            
            for endpoint in reset_endpoints:
                try:
                    reset_data = {
                        'authenticity_token': csrf_token,
                        '_method': 'post'
                    }
                    reset_response = self.session.post(endpoint, data=reset_data, allow_redirects=True)
                    print(f"🔄 重設請求回應: {reset_response.status_code}")
                    
                    if reset_response.status_code in [200, 302]:
                        # 重新取得帳戶頁面
                        time.sleep(1)  # 等待一秒
                        account_response = self.session.get(f"{self.url}/my/account")
                        
                        # 再次尋找 API 金鑰
                        for pattern in api_patterns:
                            key_match = re.search(pattern, account_response.text, re.IGNORECASE | re.DOTALL)
                            if key_match:
                                self.api_key = key_match.group(1)
                                print(f"✅ 重設後取得 API 金鑰: {self.api_key[:8]}...")
                                return
                                
                        break  # 如果請求成功但沒找到金鑰，不再嘗試其他端點
                except Exception as e:
                    print(f"⚠️  重設端點 {endpoint} 失敗: {e}")
                    continue
        else:
            print("⚠️  找不到 CSRF token")
        
        # 如果所有方法都失敗，使用手動方式提示
        self._use_fallback_api_key()
    
    def _use_fallback_api_key(self):
        """使用備用 API 金鑰設定"""
        print("⚠️  自動取得 API 金鑰失敗")
        print("📝 請手動取得 API 金鑰:")
        print("   1. 開啟瀏覽器前往: http://localhost:3000")
        print("   2. 使用 admin/admin 登入")
        print("   3. 前往「我的帳戶」→「API 存取金鑰」")
        print("   4. 如果沒有金鑰，點選「重設」按鈕")
        print("   5. 複製 API 金鑰並更新 .env 檔案")
        
        # 使用測試金鑰進行後續測試
        self.api_key = "test_api_key_for_development_only_123456789"
        print(f"🔧 暫時使用測試金鑰: {self.api_key[:8]}...")
    
    def _api_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """發送 API 請求"""
        headers = {
            'X-Redmine-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.url}/{endpoint.lstrip('/')}"
        
        if method.upper() == 'GET':
            response = self.session.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = self.session.post(url, headers=headers, json=data)
        elif method.upper() == 'PUT':
            response = self.session.put(url, headers=headers, json=data)
        else:
            raise ValueError(f"不支援的 HTTP 方法: {method}")
        
        if response.status_code not in [200, 201]:
            print(f"API 請求失敗: {response.status_code}")
            print(f"回應: {response.text}")
            return {}
        
        try:
            return response.json() if response.content else {}
        except:
            return {}
    
    def create_test_project(self, name: str, identifier: str, description: str = "") -> Optional[int]:
        """建立測試專案"""
        print(f"📁 正在建立專案: {name}")
        
        project_data = {
            'project': {
                'name': name,
                'identifier': identifier,
                'description': description,
                'is_public': True
            }
        }
        
        response = self._api_request('POST', '/projects.json', project_data)
        
        if 'project' in response:
            project_id = response['project']['id']
            print(f"✅ 專案建立成功 (ID: {project_id})")
            return project_id
        else:
            print(f"❌ 專案建立失敗")
            return None
    
    def create_test_issue(self, project_id: int, subject: str, description: str = "") -> Optional[int]:
        """建立測試議題"""
        print(f"📝 正在建立議題: {subject}")
        
        issue_data = {
            'issue': {
                'project_id': project_id,
                'subject': subject,
                'description': description
            }
        }
        
        response = self._api_request('POST', '/issues.json', issue_data)
        
        if 'issue' in response:
            issue_id = response['issue']['id']
            print(f"✅ 議題建立成功 (ID: {issue_id})")
            return issue_id
        else:
            print(f"❌ 議題建立失敗")
            return None
    
    def setup_test_data(self):
        """設定測試資料"""
        print("🎯 正在建立測試資料...")
        
        # 建立測試專案
        projects = [
            ("MCP 測試專案", "mcp-test", "用於測試 Redmine MCP 整合的專案"),
            ("軟體開發", "software-dev", "軟體開發相關專案"),
            ("Bug 追蹤", "bug-tracking", "Bug 追蹤和修復專案")
        ]
        
        created_projects = []
        for name, identifier, description in projects:
            project_id = self.create_test_project(name, identifier, description)
            if project_id:
                created_projects.append((project_id, name))
        
        # 為每個專案建立測試議題
        test_issues = [
            ("修復登入問題", "用戶回報無法使用正確帳號密碼登入系統"),
            ("新增搜尋功能", "在主頁面添加全文搜尋功能"),
            ("效能優化", "首頁載入時間過長，需要進行效能優化"),
            ("UI 改善", "更新使用者介面設計，提升使用體驗"),
            ("安全性檢查", "進行系統安全性檢查和漏洞修復")
        ]
        
        for project_id, project_name in created_projects:
            print(f"\n📋 為專案 '{project_name}' 建立議題...")
            for subject, description in test_issues:
                self.create_test_issue(project_id, f"[{project_name}] {subject}", description)
        
        return created_projects
    
    def get_api_key(self) -> str:
        """取得 API 金鑰"""
        return self.api_key


def main():
    print("🔧 Redmine 自動配置工具")
    print("=" * 40)
    
    try:
        # 等待 Redmine 啟動
        print("⏳ 檢查 Redmine 是否啟動...")
        import time
        for i in range(30):
            try:
                response = requests.get("http://localhost:3000", timeout=5)
                if response.status_code == 200:
                    break
            except:
                pass
            print(f"等待中... ({i+1}/30)")
            time.sleep(2)
        else:
            print("❌ Redmine 未啟動，請先執行 ./setup_redmine.sh")
            return False
        
        print("✅ Redmine 已啟動")
        
        # 設定 Redmine
        configurator = RedmineConfigurator()
        created_projects = configurator.setup_test_data()
        api_key = configurator.get_api_key()
        
        print("\n🎉 Redmine 設定完成！")
        print("=" * 40)
        print(f"📍 Redmine URL: http://localhost:3000")
        print(f"🔑 API 金鑰: {api_key}")
        print(f"📁 建立了 {len(created_projects)} 個測試專案")
        
        # 更新 .env 檔案
        env_content = f"""# Redmine MCP 測試環境配置
REDMINE_DOMAIN=http://localhost:3000
REDMINE_API_KEY={api_key}
REDMINE_TIMEOUT=30
DEBUG_MODE=true
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env 檔案已更新")
        print("\n🚀 現在可以測試 MCP 功能了！")
        print("   執行: uv run python test_claude_integration.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 設定失敗: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)