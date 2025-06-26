#!/usr/bin/env python3
"""
啟用 Redmine REST API 的腳本
"""

import requests
import re
import time

def enable_rest_api():
    """透過 Web 介面啟用 REST API"""
    session = requests.Session()
    url = "http://localhost:3000"
    
    try:
        print("🔐 正在登入管理員帳戶...")
        
        # 取得登入頁面和 CSRF token
        response = session.get(f"{url}/login")
        csrf_match = re.search(r'name="authenticity_token" value="([^"]+)"', response.text)
        if not csrf_match:
            print("❌ 找不到 CSRF token")
            return False
        
        csrf_token = csrf_match.group(1)
        
        # 登入
        login_data = {
            'username': 'admin',
            'password': 'admin',
            'authenticity_token': csrf_token
        }
        
        response = session.post(f"{url}/login", data=login_data, allow_redirects=False)
        if response.status_code not in [302, 200]:
            print(f"❌ 登入失敗: {response.status_code}")
            return False
        
        print("✅ 登入成功")
        
        # 前往設定頁面
        print("⚙️  正在存取系統設定...")
        response = session.get(f"{url}/settings")
        if response.status_code != 200:
            print(f"❌ 無法存取設定頁面: {response.status_code}")
            return False
        
        # 檢查當前 REST API 狀態
        if 'rest_api_enabled' in response.text:
            print("📡 找到 REST API 設定")
        else:
            print("⚠️  找不到 REST API 設定選項")
            
        # 取得設定頁面的 CSRF token
        csrf_match = re.search(r'name="authenticity_token" value="([^"]+)"', response.text)
        if not csrf_match:
            print("❌ 找不到設定頁面的 CSRF token")
            return False
        
        csrf_token = csrf_match.group(1)
        
        # 準備啟用 REST API 的資料
        print("🔧 正在啟用 REST API...")
        settings_data = {
            'authenticity_token': csrf_token,
            'settings[rest_api_enabled]': '1',  # 啟用 REST API
            'settings[jsonp_enabled]': '0',     # 保持 JSONP 停用
            'commit': 'Save'
        }
        
        response = session.post(f"{url}/settings", data=settings_data)
        
        if response.status_code == 200:
            print("✅ REST API 設定已更新")
            
            # 驗證設定是否生效
            time.sleep(1)
            test_response = session.get(f"{url}/issues.json")
            print(f"🧪 API 測試回應: {test_response.status_code}")
            
            if test_response.status_code == 200:
                print("🎉 REST API 已成功啟用！")
                return True
            else:
                print("⚠️  REST API 可能仍未正常運作")
        else:
            print(f"❌ 設定更新失敗: {response.status_code}")
            print(f"回應內容: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        
    return False

def main():
    print("🚀 Redmine REST API 啟用工具")
    print("=" * 40)
    
    if enable_rest_api():
        print("\n🎯 接下來的步驟:")
        print("1. 執行: uv run python configure_redmine.py")
        print("2. 或者手動取得 API 金鑰後執行:")
        print("   python manual_api_setup.py <API_KEY>")
        return True
    else:
        print("\n❌ REST API 啟用失敗")
        print("請手動啟用:")
        print("1. 開啟 http://localhost:3000")
        print("2. 使用 admin/admin 登入")
        print("3. 前往 Administration > Settings > API")
        print("4. 勾選 'Enable REST web service'")
        print("5. 點選 Save")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)