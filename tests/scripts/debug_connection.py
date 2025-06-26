#!/usr/bin/env python3
"""
除錯 Redmine 連接問題
"""

import sys
import os
from pathlib import Path
import requests

# 添加 src 到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def debug_connection():
    """詳細除錯連接問題"""
    print("🔍 除錯 Redmine 連接")
    print("=" * 50)
    
    try:
        from redmine_mcp.config import get_config
        config = get_config()
        
        print(f"Domain: {config.redmine_domain}")
        print(f"API Key: {config.redmine_api_key[:8]}...{config.redmine_api_key[-4:]}")
        print(f"Timeout: {config.redmine_timeout}")
        
        # 測試基本 HTTP 連接
        print("\n1️⃣ 測試基本 HTTP 連接...")
        try:
            response = requests.get(config.redmine_domain, timeout=10)
            print(f"✅ HTTP 連接成功 (狀態碼: {response.status_code})")
        except Exception as e:
            print(f"❌ HTTP 連接失敗: {e}")
            return
        
        # 測試 API 端點
        print("\n2️⃣ 測試 API 端點...")
        api_url = f"{config.redmine_domain}/my/account.json"
        headers = {'X-Redmine-API-Key': config.redmine_api_key}
        
        try:
            response = requests.get(api_url, headers=headers, timeout=config.redmine_timeout)
            print(f"API 回應狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'user' in data:
                    user = data['user']
                    print(f"✅ API 認證成功")
                    print(f"  用戶: {user.get('login', 'N/A')} ({user.get('firstname', '')} {user.get('lastname', '')})")
                else:
                    print(f"❌ API 回應格式異常: {data}")
            elif response.status_code == 401:
                print(f"❌ API 金鑰無效 (401 Unauthorized)")
            elif response.status_code == 403:
                print(f"❌ 權限不足 (403 Forbidden)")
            elif response.status_code == 404:
                print(f"❌ API 端點不存在 (404 Not Found)")
            else:
                print(f"❌ 未知錯誤 ({response.status_code})")
                print(f"回應內容: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"❌ 請求超時 ({config.redmine_timeout}s)")
        except requests.exceptions.ConnectionError:
            print(f"❌ 連接錯誤")
        except Exception as e:
            print(f"❌ API 請求失敗: {e}")
        
        # 測試其他 API 端點
        print("\n3️⃣ 測試其他 API 端點...")
        endpoints = [
            ('/issues.json?limit=1', '議題列表'),
            ('/projects.json?limit=1', '專案列表'),
            ('/enumerations/issue_priorities.json', '優先權列表'),
        ]
        
        for endpoint, desc in endpoints:
            try:
                url = f"{config.redmine_domain}{endpoint}"
                response = requests.get(url, headers=headers, timeout=config.redmine_timeout)
                if response.status_code == 200:
                    print(f"✅ {desc}: {response.status_code}")
                else:
                    print(f"⚠️ {desc}: {response.status_code}")
            except Exception as e:
                print(f"❌ {desc}: {e}")
        
        # 測試我們的客戶端
        print("\n4️⃣ 測試客戶端...")
        try:
            from redmine_mcp.redmine_client import get_client
            client = get_client()
            
            # 直接測試 _make_request 方法
            response = client._make_request('GET', '/my/account.json')
            if 'user' in response:
                print(f"✅ 客戶端請求成功")
            else:
                print(f"❌ 客戶端請求異常: {response}")
                
        except Exception as e:
            print(f"❌ 客戶端測試失敗: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ 除錯過程失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_connection()