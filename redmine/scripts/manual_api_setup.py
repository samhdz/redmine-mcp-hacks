#!/usr/bin/env python3
"""
手動 API 金鑰設置和測試腳本
當自動配置失敗時使用此腳本
"""

import requests
import json
import sys
import os

def test_api_connection(api_key: str, domain: str = "http://localhost:3000") -> bool:
    """測試 API 連接"""
    print(f"🔍 測試 API 金鑰: {api_key[:8]}...")
    
    headers = {
        'X-Redmine-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # 測試取得專案列表
        response = requests.get(f"{domain}/projects.json", headers=headers, timeout=10)
        print(f"📡 API 回應狀態: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            project_count = len(data.get('projects', []))
            print(f"✅ API 連接成功，找到 {project_count} 個專案")
            return True
        elif response.status_code == 401:
            print("❌ API 金鑰無效 (401 Unauthorized)")
        elif response.status_code == 403:
            print("❌ API 存取被禁止 (403 Forbidden)")
        elif response.status_code == 422:
            print("❌ API 格式錯誤 (422 Unprocessable Entity)")
        else:
            print(f"❌ API 請求失敗: {response.status_code}")
            print(f"回應內容: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 網路錯誤: {e}")
    
    return False

def create_test_project(api_key: str, domain: str = "http://localhost:3000") -> bool:
    """建立測試專案"""
    print("📁 嘗試建立測試專案...")
    
    headers = {
        'X-Redmine-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    project_data = {
        'project': {
            'name': '手動測試專案',
            'identifier': 'manual-test',
            'description': '手動建立的測試專案',
            'is_public': True
        }
    }
    
    try:
        response = requests.post(f"{domain}/projects.json", headers=headers, json=project_data, timeout=10)
        print(f"📡 建立專案回應: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            project_id = data['project']['id']
            print(f"✅ 測試專案建立成功 (ID: {project_id})")
            return True
        else:
            print(f"❌ 專案建立失敗: {response.status_code}")
            print(f"回應內容: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 網路錯誤: {e}")
    
    return False

def update_env_file(api_key: str):
    """更新 .env 檔案"""
    env_content = f"""# Redmine MCP 測試環境配置
REDMINE_DOMAIN=http://localhost:3000
REDMINE_API_KEY={api_key}
REDMINE_TIMEOUT=30
DEBUG_MODE=true
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env 檔案已更新")

def main():
    print("🔧 手動 API 金鑰設置工具")
    print("=" * 40)
    
    # 檢查是否提供 API 金鑰
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python manual_api_setup.py <API_KEY>")
        print("")
        print("請手動取得 API 金鑰:")
        print("1. 開啟瀏覽器前往: http://localhost:3000")
        print("2. 使用 admin/admin 登入")
        print("3. 前往「我的帳戶」")
        print("4. 找到「API 存取金鑰」區塊")
        print("5. 如果沒有金鑰，點選「重設」按鈕")
        print("6. 複製金鑰並執行:")
        print("   python manual_api_setup.py <你的API金鑰>")
        return False
    
    api_key = sys.argv[1].strip()
    
    # 驗證 API 金鑰格式
    if len(api_key) != 40 or not all(c in '0123456789abcdef' for c in api_key.lower()):
        print("⚠️  API 金鑰格式不正確，應該是 40 位 16 進位字串")
        return False
    
    print(f"🔑 使用 API 金鑰: {api_key[:8]}...")
    
    # 測試 API 連接
    if not test_api_connection(api_key):
        print("❌ API 連接測試失敗")
        return False
    
    # 嘗試建立測試專案
    create_test_project(api_key)
    
    # 更新環境檔案
    update_env_file(api_key)
    
    print("\n🎉 設定完成！")
    print("接下來可以執行:")
    print("  uv run python test_mcp_integration.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)