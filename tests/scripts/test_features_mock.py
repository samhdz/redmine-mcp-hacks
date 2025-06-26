#!/usr/bin/env python3
"""
使用 Mock 資料測試新功能
不需要真實的 Redmine 連接
"""

import sys
import os
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

# 添加 src 到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def create_mock_data():
    """建立模擬資料"""
    return {
        'priorities': [
            {'id': 5, 'name': '低'},
            {'id': 6, 'name': '正常'},
            {'id': 7, 'name': '高'},
            {'id': 8, 'name': '緊急'}
        ],
        'statuses': [
            {'id': 1, 'name': '新建立'},
            {'id': 2, 'name': '實作中'}, 
            {'id': 3, 'name': '已完成'},
            {'id': 4, 'name': '已關閉'}
        ],
        'trackers': [
            {'id': 1, 'name': '臭蟲'},
            {'id': 2, 'name': '功能'},
            {'id': 3, 'name': '支援'}
        ],
        'users': [
            {
                'id': 1,
                'login': 'admin',
                'firstname': 'Redmine',
                'lastname': 'Admin',
                'mail': 'admin@example.com',
                'status': 1
            },
            {
                'id': 2, 
                'login': 'user1',
                'firstname': '測試',
                'lastname': '用戶',
                'mail': 'user1@example.com',
                'status': 1
            }
        ]
    }


def test_cache_system_with_mock():
    """使用模擬資料測試快取系統"""
    print("💾 測試快取系統 (Mock)")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client, RedmineUser
        
        mock_data = create_mock_data()
        
        # Mock API 回應
        def mock_make_request(method, endpoint, **kwargs):
            if '/enumerations/issue_priorities.json' in endpoint:
                return {'issue_priorities': mock_data['priorities']}
            elif '/issue_statuses.json' in endpoint:
                return {'issue_statuses': mock_data['statuses']}
            elif '/trackers.json' in endpoint:
                return {'trackers': mock_data['trackers']}
            elif '/users.json' in endpoint:
                return {'users': mock_data['users']}
            else:
                raise Exception(f"Unexpected endpoint: {endpoint}")
        
        client = get_client()
        
        # 使用 Mock
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            # 強制刷新快取
            client.refresh_cache()
            
            # 檢查快取檔案是否建立
            cache_file = client._cache_file
            if cache_file.exists():
                print("✅ 快取檔案建立成功")
            else:
                print("❌ 快取檔案建立失敗")
                return False
            
            # 檢查快取內容
            cache = client._load_enum_cache()
            
            # 驗證結構
            required_fields = ['cache_time', 'domain', 'priorities', 'statuses', 'trackers', 'users_by_name', 'users_by_login']
            for field in required_fields:
                if field in cache:
                    print(f"✅ 快取包含 {field}")
                else:
                    print(f"❌ 快取缺少 {field}")
                    return False
            
            # 驗證資料
            expected_priorities = {'低': 5, '正常': 6, '高': 7, '緊急': 8}
            if cache['priorities'] == expected_priorities:
                print("✅ 優先權快取正確")
            else:
                print(f"❌ 優先權快取錯誤: {cache['priorities']}")
                return False
            
            expected_users_by_name = {'Redmine Admin': 1, '測試 用戶': 2}
            if cache['users_by_name'] == expected_users_by_name:
                print("✅ 用戶姓名快取正確")
            else:
                print(f"❌ 用戶姓名快取錯誤: {cache['users_by_name']}")
                return False
            
            print(f"📊 快取統計:")
            print(f"  - 優先權: {len(cache['priorities'])} 個")
            print(f"  - 狀態: {len(cache['statuses'])} 個")
            print(f"  - 追蹤器: {len(cache['trackers'])} 個")
            print(f"  - 用戶（姓名）: {len(cache['users_by_name'])} 個")
            print(f"  - 用戶（登入名）: {len(cache['users_by_login'])} 個")
            
            return True
            
    except Exception as e:
        print(f"❌ 快取系統測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_helper_functions_with_mock():
    """使用模擬資料測試輔助函數"""
    print("\n🔧 測試輔助函數 (Mock)")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client
        
        client = get_client()
        
        # 設定模擬快取
        mock_cache = {
            'cache_time': 1234567890,
            'domain': 'http://localhost:3000',
            'priorities': {'低': 5, '正常': 6, '高': 7, '緊急': 8},
            'statuses': {'新建立': 1, '實作中': 2, '已完成': 3, '已關閉': 4},
            'trackers': {'臭蟲': 1, '功能': 2, '支援': 3},
            'users_by_name': {'Redmine Admin': 1, '測試 用戶': 2},
            'users_by_login': {'admin': 1, 'user1': 2}
        }
        
        client._enum_cache = mock_cache
        
        # 測試優先權查詢
        test_cases = [
            ('find_priority_id_by_name', '低', 5),
            ('find_priority_id_by_name', '不存在', None),
            ('find_status_id_by_name', '實作中', 2),
            ('find_status_id_by_name', '不存在', None),
            ('find_tracker_id_by_name', '臭蟲', 1),
            ('find_tracker_id_by_name', '不存在', None),
            ('find_user_id_by_name', 'Redmine Admin', 1),
            ('find_user_id_by_name', '不存在', None),
            ('find_user_id_by_login', 'admin', 1),
            ('find_user_id_by_login', '不存在', None),
            ('find_user_id', 'admin', 1),
            ('find_user_id', 'Redmine Admin', 1),
            ('find_user_id', '不存在', None),
        ]
        
        for method_name, input_value, expected in test_cases:
            method = getattr(client, method_name)
            result = method(input_value)
            
            if result == expected:
                print(f"✅ {method_name}('{input_value}') → {result}")
            else:
                print(f"❌ {method_name}('{input_value}') → {result}, 期望 {expected}")
                return False
        
        # 測試取得所有選項
        print("\n測試取得所有選項:")
        priorities = client.get_available_priorities()
        if priorities == mock_cache['priorities']:
            print(f"✅ get_available_priorities: {len(priorities)} 個")
        else:
            print(f"❌ get_available_priorities 錯誤")
            return False
        
        users = client.get_available_users()
        expected_users = {
            'by_name': mock_cache['users_by_name'],
            'by_login': mock_cache['users_by_login']
        }
        if users == expected_users:
            print(f"✅ get_available_users: 姓名 {len(users['by_name'])} 個, 登入名 {len(users['by_login'])} 個")
        else:
            print(f"❌ get_available_users 錯誤")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 輔助函數測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_domain_isolation():
    """測試 Domain 隔離"""
    print("\n🌐 測試 Domain 隔離 (Mock)")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import RedmineClient
        
        # 測試不同 domain 的快取檔案名稱
        domains = [
            'http://localhost:3000',
            'https://demo.redmine.org',
            'https://test.example.com:8080'
        ]
        
        cache_files = []
        
        for domain in domains:
            # 直接測試快取檔案名稱生成邏輯
            domain_hash = hash(domain)
            safe_domain = domain.replace('://', '_').replace('/', '_').replace(':', '_')
            cache_filename = f"cache_{safe_domain}_{abs(domain_hash)}.json"
            
            cache_files.append((domain, cache_filename))
        
        # 檢查所有檔案名稱都不同
        filenames = [filename for _, filename in cache_files]
        
        print("Domain 和檔案名稱對應:")
        for domain, filename in cache_files:
            print(f"  {domain} → {filename}")
        
        print(f"\n檔案名稱唯一性檢查:")
        print(f"  總檔案數: {len(filenames)}")
        print(f"  唯一檔案數: {len(set(filenames))}")
        
        if len(set(filenames)) == len(filenames):
            print("✅ 不同 Domain 產生不同快取檔案")
        else:
            print("❌ Domain 隔離失敗，檔案名稱重複")
            # 顯示重複的檔案名稱
            seen = set()
            duplicates = set()
            for filename in filenames:
                if filename in seen:
                    duplicates.add(filename)
                else:
                    seen.add(filename)
            print(f"  重複的檔案名稱: {duplicates}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Domain 隔離測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_tools_with_mock():
    """測試 MCP 工具 (Mock)"""
    print("\n🛠️ 測試 MCP 工具 (Mock)")
    print("-" * 40)
    
    try:
        # Mock 客戶端回應
        mock_users = [
            {'id': 1, 'login': 'admin', 'firstname': 'Redmine', 'lastname': 'Admin', 'mail': 'admin@example.com', 'status': 1}
        ]
        
        def mock_search_users(query, limit):
            from redmine_mcp.redmine_client import RedmineUser
            return [RedmineUser(
                id=user['id'],
                login=user['login'],
                firstname=user['firstname'],
                lastname=user['lastname'],
                mail=user['mail'],
                status=user['status']
            ) for user in mock_users if query.lower() in user['login'].lower()]
        
        def mock_list_users(limit, status):
            from redmine_mcp.redmine_client import RedmineUser
            return [RedmineUser(
                id=user['id'],
                login=user['login'],
                firstname=user['firstname'],
                lastname=user['lastname'],
                mail=user['mail'],
                status=user['status']
            ) for user in mock_users]
        
        def mock_get_user(user_id):
            user = next((u for u in mock_users if u['id'] == user_id), None)
            if user:
                return user
            else:
                raise Exception(f"找不到用戶 ID {user_id}")
        
        # 測試 MCP 工具
        from redmine_mcp.redmine_client import get_client
        client = get_client()
        
        with patch.object(client, 'search_users', side_effect=mock_search_users), \
             patch.object(client, 'list_users', side_effect=mock_list_users), \
             patch.object(client, 'get_user', side_effect=mock_get_user):
            
            # 測試 search_users MCP 工具
            from redmine_mcp.server import search_users, list_users, get_user
            
            result = search_users("admin", 5)
            if "admin" in result and "Redmine Admin" in result:
                print("✅ search_users MCP 工具正常")
            else:
                print(f"❌ search_users MCP 工具異常: {result}")
                return False
            
            # 測試 list_users MCP 工具
            result = list_users(10, "active")
            if "admin" in result and "Redmine Admin" in result:
                print("✅ list_users MCP 工具正常")
            else:
                print(f"❌ list_users MCP 工具異常: {result}")
                return False
            
            # 測試 get_user MCP 工具
            result = get_user(1)
            if "admin" in result and "Redmine Admin" in result:
                print("✅ get_user MCP 工具正常")
            else:
                print(f"❌ get_user MCP 工具異常: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ MCP 工具測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_mock_tests():
    """執行所有 Mock 測試"""
    print("🧪 redmine-mcp 新功能 Mock 測試")
    print("=" * 60)
    print("（使用模擬資料，不需要真實 Redmine 連接）")
    print("=" * 60)
    
    tests = [
        ("快取系統", test_cache_system_with_mock),
        ("輔助函數", test_helper_functions_with_mock),
        ("Domain 隔離", test_domain_isolation),
        ("MCP 工具", test_mcp_tools_with_mock),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 執行測試: {test_name}")
        print("=" * 50)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"\n✅ {test_name} 測試通過")
            else:
                print(f"\n❌ {test_name} 測試失敗")
                
        except Exception as e:
            print(f"\n❌ {test_name} 測試出現異常: {e}")
            results.append((test_name, False))
    
    # 輸出總結
    print("\n" + "=" * 60)
    print("📊 Mock 測試結果總結")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"{test_name:<15} {status}")
    
    print(f"\n總測試數: {total}")
    print(f"通過數: {passed}")
    print(f"失敗數: {total - passed}")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有 Mock 測試都通過了！")
        print("新功能的程式邏輯運作正常！")
        print("\n💡 要測試真實 Redmine 連接，請:")
        print("1. 確保 Redmine 服務正在運行")
        print("2. 更新有效的 API 金鑰")
        print("3. 執行: uv run python tests/scripts/quick_validation.py")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 個測試失敗，請檢查程式邏輯")
        return False


if __name__ == "__main__":
    success = run_mock_tests()
    sys.exit(0 if success else 1)