#!/usr/bin/env python3
"""
測試新實作的 MCP 工具
透過直接呼叫 MCP 工具函數來驗證功能
"""

import sys
import os
from pathlib import Path

# 添加 src 到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from redmine_mcp.server import (
    search_users, list_users, get_user, refresh_cache,
    get_priorities, get_issue_statuses, get_trackers
)


def test_user_mcp_tools():
    """測試用戶相關的 MCP 工具"""
    print("🔍 測試用戶 MCP 工具...")
    print("-" * 40)
    
    try:
        # 測試搜尋用戶
        print("1️⃣ 測試 search_users...")
        result = search_users("admin", 5)
        print(f"搜尋結果：\n{result}\n")
        
        # 測試列出用戶
        print("2️⃣ 測試 list_users...")
        result = list_users(10, "active")
        print(f"用戶列表：\n{result}\n")
        
        # 測試取得用戶詳情（假設用戶 ID 1 存在）
        print("3️⃣ 測試 get_user...")
        result = get_user(1)
        print(f"用戶詳情：\n{result}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ 用戶 MCP 工具測試失敗: {e}")
        return False


def test_cache_mcp_tool():
    """測試快取 MCP 工具"""
    print("💾 測試快取 MCP 工具...")
    print("-" * 40)
    
    try:
        print("🔄 測試 refresh_cache...")
        result = refresh_cache()
        print(f"快取刷新結果：\n{result}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ 快取 MCP 工具測試失敗: {e}")
        return False


def test_enum_mcp_tools():
    """測試列舉值 MCP 工具（驗證是否正常工作）"""
    print("📋 測試列舉值 MCP 工具...")
    print("-" * 40)
    
    try:
        print("1️⃣ 測試 get_priorities...")
        result = get_priorities()
        print(f"優先權列表：\n{result}\n")
        
        print("2️⃣ 測試 get_issue_statuses...")
        result = get_issue_statuses()
        print(f"狀態列表：\n{result}\n")
        
        print("3️⃣ 測試 get_trackers...")
        result = get_trackers()
        print(f"追蹤器列表：\n{result}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ 列舉值 MCP 工具測試失敗: {e}")
        return False


def test_helper_functions_integration():
    """測試輔助函數與實際資料的整合"""
    print("🔧 測試輔助函數整合...")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client
        
        client = get_client()
        
        # 測試優先權查詢
        print("1️⃣ 測試優先權名稱查詢...")
        priorities = client.get_available_priorities()
        if priorities:
            first_priority = list(priorities.keys())[0]
            priority_id = client.find_priority_id_by_name(first_priority)
            print(f"  優先權 '{first_priority}' → ID: {priority_id}")
            assert priority_id == priorities[first_priority]
            print("  ✅ 優先權查詢正確")
        
        # 測試狀態查詢
        print("2️⃣ 測試狀態名稱查詢...")
        statuses = client.get_available_statuses()
        if statuses:
            first_status = list(statuses.keys())[0]
            status_id = client.find_status_id_by_name(first_status)
            print(f"  狀態 '{first_status}' → ID: {status_id}")
            assert status_id == statuses[first_status]
            print("  ✅ 狀態查詢正確")
        
        # 測試追蹤器查詢
        print("3️⃣ 測試追蹤器名稱查詢...")
        trackers = client.get_available_trackers()
        if trackers:
            first_tracker = list(trackers.keys())[0]
            tracker_id = client.find_tracker_id_by_name(first_tracker)
            print(f"  追蹤器 '{first_tracker}' → ID: {tracker_id}")
            assert tracker_id == trackers[first_tracker]
            print("  ✅ 追蹤器查詢正確")
        
        # 測試用戶查詢
        print("4️⃣ 測試用戶名稱查詢...")
        users = client.get_available_users()
        if users['by_name']:
            first_user = list(users['by_name'].keys())[0]
            user_id = client.find_user_id_by_name(first_user)
            print(f"  用戶 '{first_user}' → ID: {user_id}")
            assert user_id == users['by_name'][first_user]
            print("  ✅ 用戶姓名查詢正確")
        
        if users['by_login']:
            first_login = list(users['by_login'].keys())[0]
            user_id = client.find_user_id_by_login(first_login)
            print(f"  登入名 '{first_login}' → ID: {user_id}")
            assert user_id == users['by_login'][first_login]
            print("  ✅ 用戶登入名查詢正確")
            
            # 測試智慧查詢
            smart_id = client.find_user_id(first_login)
            assert smart_id == user_id
            print("  ✅ 智慧用戶查詢正確")
        
        return True
        
    except Exception as e:
        print(f"❌ 輔助函數整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_file_structure():
    """測試快取檔案結構"""
    print("📁 測試快取檔案結構...")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client
        import json
        
        client = get_client()
        
        # 確保快取存在
        client.refresh_cache()
        
        # 檢查快取檔案
        cache_file = client._cache_file
        print(f"快取檔案位置: {cache_file}")
        
        if cache_file.exists():
            print("✅ 快取檔案存在")
            
            # 讀取並檢查結構
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            required_fields = ['cache_time', 'domain', 'priorities', 'statuses', 'trackers', 'users_by_name', 'users_by_login']
            
            for field in required_fields:
                if field in cache_data:
                    print(f"✅ 快取包含 {field}: {len(cache_data[field]) if isinstance(cache_data[field], dict) else 'N/A'} 項目")
                else:
                    print(f"❌ 快取缺少 {field}")
                    return False
            
            # 檢查時間戳
            cache_time = cache_data['cache_time']
            if isinstance(cache_time, (int, float)) and cache_time > 0:
                from datetime import datetime
                cache_datetime = datetime.fromtimestamp(cache_time)
                print(f"✅ 快取時間: {cache_datetime}")
            else:
                print("❌ 快取時間格式錯誤")
                return False
            
            return True
        else:
            print("❌ 快取檔案不存在")
            return False
            
    except Exception as e:
        print(f"❌ 快取檔案結構測試失敗: {e}")
        return False


def run_all_tests():
    """執行所有 MCP 工具測試"""
    print("=" * 60)
    print("🚀 redmine-mcp 新功能 MCP 工具測試")
    print("=" * 60)
    
    tests = [
        ("用戶 MCP 工具", test_user_mcp_tools),
        ("快取 MCP 工具", test_cache_mcp_tool),
        ("列舉值 MCP 工具", test_enum_mcp_tools),
        ("輔助函數整合", test_helper_functions_integration),
        ("快取檔案結構", test_cache_file_structure),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 執行測試: {test_name}")
        print("=" * 50)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} 測試通過")
            else:
                print(f"❌ {test_name} 測試失敗")
                
        except Exception as e:
            print(f"❌ {test_name} 測試出現異常: {e}")
            results.append((test_name, False))
    
    # 輸出總結
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"{test_name:<20} {status}")
    
    print(f"\n總測試數: {total}")
    print(f"通過數: {passed}")
    print(f"失敗數: {total - passed}")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有測試都通過了！新功能運作正常！")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 個測試失敗，請檢查相關功能")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)