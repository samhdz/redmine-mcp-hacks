#!/usr/bin/env python3
"""
快速驗證新功能的簡化測試腳本
主要測試核心功能是否正常運作
"""

import sys
import os
from pathlib import Path

# 添加 src 到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def quick_test():
    """快速測試核心功能"""
    print("🚀 快速驗證 redmine-mcp 新功能")
    print("=" * 50)
    
    try:
        # 測試基本連接
        print("1️⃣ 測試基本連接...")
        from redmine_mcp.redmine_client import get_client
        client = get_client()
        
        if client.test_connection():
            print("✅ Redmine 連接正常")
        else:
            print("❌ Redmine 連接失敗")
            return False
        
        # 測試快取系統
        print("\n2️⃣ 測試快取系統...")
        cache_dir = client.cache_dir
        cache_file = client._cache_file
        
        print(f"  快取目錄: {cache_dir}")
        print(f"  快取檔案: {cache_file.name}")
        
        if cache_dir.exists():
            print("✅ 快取目錄存在")
        else:
            print("❌ 快取目錄不存在")
            return False
        
        # 刷新快取
        print("\n3️⃣ 測試快取刷新...")
        client.refresh_cache()
        
        if cache_file.exists():
            print("✅ 快取檔案建立成功")
        else:
            print("❌ 快取檔案建立失敗")
            return False
        
        # 測試輔助函數
        print("\n4️⃣ 測試輔助函數...")
        
        # 測試優先權查詢
        priorities = client.get_available_priorities()
        if priorities:
            priority_name = list(priorities.keys())[0]
            priority_id = client.find_priority_id_by_name(priority_name)
            if priority_id:
                print(f"✅ 優先權查詢正常: '{priority_name}' → {priority_id}")
            else:
                print("❌ 優先權查詢失敗")
                return False
        else:
            print("⚠️ 沒有優先權資料可測試")
        
        # 測試狀態查詢
        statuses = client.get_available_statuses()
        if statuses:
            status_name = list(statuses.keys())[0]
            status_id = client.find_status_id_by_name(status_name)
            if status_id:
                print(f"✅ 狀態查詢正常: '{status_name}' → {status_id}")
            else:
                print("❌ 狀態查詢失敗")
                return False
        else:
            print("⚠️ 沒有狀態資料可測試")
        
        # 測試用戶查詢
        print("\n5️⃣ 測試用戶查詢...")
        try:
            users = client.list_users(limit=5)
            if users:
                print(f"✅ 用戶查詢正常: 找到 {len(users)} 個用戶")
                
                # 測試用戶快取
                cache = client._load_enum_cache()
                users_by_name = cache.get('users_by_name', {})
                users_by_login = cache.get('users_by_login', {})
                
                if users_by_name or users_by_login:
                    print(f"✅ 用戶快取正常: 姓名 {len(users_by_name)} 個, 登入名 {len(users_by_login)} 個")
                else:
                    print("⚠️ 用戶快取為空")
            else:
                print("⚠️ 沒有用戶資料可測試")
        except Exception as e:
            print(f"⚠️ 用戶查詢跳過（可能權限不足）: {e}")
        
        # 測試 MCP 工具
        print("\n6️⃣ 測試 MCP 工具...")
        try:
            from redmine_mcp.server import get_priorities, refresh_cache
            
            # 測試 get_priorities
            result = get_priorities()
            if "優先級" in result or "priorities" in result.lower():
                print("✅ get_priorities MCP 工具正常")
            else:
                print("❌ get_priorities MCP 工具異常")
                return False
            
            # 測試 refresh_cache
            result = refresh_cache()
            if "成功" in result or "success" in result.lower():
                print("✅ refresh_cache MCP 工具正常")
            else:
                print("❌ refresh_cache MCP 工具異常")
                return False
                
        except Exception as e:
            print(f"❌ MCP 工具測試失敗: {e}")
            return False
        
        # 輸出快取統計
        print("\n📊 快取統計資訊:")
        cache = client._load_enum_cache()
        print(f"  - Domain: {cache.get('domain', 'N/A')}")
        print(f"  - 優先權: {len(cache.get('priorities', {}))} 個")
        print(f"  - 狀態: {len(cache.get('statuses', {}))} 個")
        print(f"  - 追蹤器: {len(cache.get('trackers', {}))} 個")
        print(f"  - 用戶（姓名）: {len(cache.get('users_by_name', {}))} 個")
        print(f"  - 用戶（登入名）: {len(cache.get('users_by_login', {}))} 個")
        
        print("\n🎉 所有核心功能驗證通過！")
        return True
        
    except Exception as e:
        print(f"\n❌ 驗證過程出現錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


def display_usage_examples():
    """顯示使用範例"""
    print("\n" + "=" * 50)
    print("💡 使用範例")
    print("=" * 50)
    
    examples = [
        "# 根據名稱查詢 ID",
        "from redmine_mcp.redmine_client import get_client",
        "client = get_client()",
        "",
        "# 查詢優先權 ID",
        'priority_id = client.find_priority_id_by_name("低")',
        "",
        "# 查詢狀態 ID", 
        'status_id = client.find_status_id_by_name("實作中")',
        "",
        "# 查詢用戶 ID",
        'user_id = client.find_user_id("Redmine Admin")',
        "",
        "# 取得所有可用選項",
        "priorities = client.get_available_priorities()",
        "users = client.get_available_users()",
        "",
        "# 手動刷新快取",
        "client.refresh_cache()",
    ]
    
    for example in examples:
        print(example)


if __name__ == "__main__":
    success = quick_test()
    
    if success:
        display_usage_examples()
    
    print(f"\n{'='*50}")
    print(f"驗證結果: {'✅ 成功' if success else '❌ 失敗'}")
    print(f"{'='*50}")
    
    sys.exit(0 if success else 1)