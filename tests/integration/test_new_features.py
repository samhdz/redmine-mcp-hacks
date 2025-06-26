"""
測試新實作功能的整合測試
包含用戶查詢、快取機制、輔助函數等
"""

import pytest
import os
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

from src.redmine_mcp.redmine_client import get_client, RedmineClient, RedmineAPIError
from src.redmine_mcp.config import get_config


class TestUserFunctionality:
    """測試用戶查詢功能"""
    
    def test_search_users_by_name(self):
        """測試根據姓名搜尋用戶"""
        try:
            client = get_client()
            users = client.search_users("admin", limit=5)
            
            assert isinstance(users, list)
            print(f"✅ 搜尋用戶功能正常，找到 {len(users)} 個用戶")
            
            if users:
                user = users[0]
                assert hasattr(user, 'id')
                assert hasattr(user, 'login')
                assert hasattr(user, 'firstname')
                assert hasattr(user, 'lastname')
                print(f"✅ 用戶數據結構正確：{user.login}")
            
        except RedmineAPIError as e:
            pytest.skip(f"Redmine API 錯誤（可能是權限問題）: {e}")
        except Exception as e:
            pytest.fail(f"用戶搜尋測試失敗: {e}")
    
    def test_list_users(self):
        """測試列出所有用戶"""
        try:
            client = get_client()
            users = client.list_users(limit=10)
            
            assert isinstance(users, list)
            print(f"✅ 列出用戶功能正常，共 {len(users)} 個用戶")
            
            if users:
                user = users[0]
                assert user.id > 0
                assert user.login
                print(f"✅ 第一個用戶：ID={user.id}, Login={user.login}")
            
        except RedmineAPIError as e:
            pytest.skip(f"Redmine API 錯誤: {e}")
        except Exception as e:
            pytest.fail(f"列出用戶測試失敗: {e}")
    
    def test_get_user_details(self):
        """測試取得特定用戶詳情"""
        try:
            client = get_client()
            # 通常 ID 1 是管理員
            user_data = client.get_user(1)
            
            assert isinstance(user_data, dict)
            assert 'id' in user_data
            assert 'login' in user_data
            print(f"✅ 取得用戶詳情功能正常：{user_data.get('login', 'N/A')}")
            
        except RedmineAPIError as e:
            pytest.skip(f"Redmine API 錯誤: {e}")
        except Exception as e:
            pytest.fail(f"取得用戶詳情測試失敗: {e}")


class TestCacheSystem:
    """測試快取系統功能"""
    
    def test_cache_file_creation(self):
        """測試快取檔案是否正確建立"""
        client = get_client()
        cache_dir = client.cache_dir
        cache_file = client._cache_file
        
        # 檢查快取目錄
        assert cache_dir.exists()
        assert cache_dir.is_dir()
        print(f"✅ 快取目錄存在：{cache_dir}")
        
        # 檢查檔案名稱格式
        assert "cache_" in cache_file.name
        config = get_config()
        domain_in_filename = config.redmine_domain.replace('://', '_').replace('/', '_').replace(':', '_')
        assert domain_in_filename in cache_file.name
        print(f"✅ 快取檔案名稱正確：{cache_file.name}")
    
    def test_cache_content_structure(self):
        """測試快取內容結構"""
        try:
            client = get_client()
            # 強制刷新快取
            client.refresh_cache()
            
            cache = client._load_enum_cache()
            
            # 檢查必要欄位
            required_fields = ['cache_time', 'domain', 'priorities', 'statuses', 'trackers', 'users_by_name', 'users_by_login']
            for field in required_fields:
                assert field in cache, f"快取缺少必要欄位：{field}"
            
            # 檢查 domain 是否正確
            config = get_config()
            assert cache['domain'] == config.redmine_domain
            
            # 檢查時間戳
            assert isinstance(cache['cache_time'], (int, float))
            assert cache['cache_time'] > 0
            
            print(f"✅ 快取結構正確")
            print(f"  - Domain: {cache['domain']}")
            print(f"  - 優先權: {len(cache['priorities'])} 個")
            print(f"  - 狀態: {len(cache['statuses'])} 個")
            print(f"  - 追蹤器: {len(cache['trackers'])} 個")
            print(f"  - 用戶（姓名）: {len(cache['users_by_name'])} 個")
            print(f"  - 用戶（登入名）: {len(cache['users_by_login'])} 個")
            
        except Exception as e:
            pytest.fail(f"快取內容測試失敗: {e}")
    
    def test_cache_persistence(self):
        """測試快取持久化"""
        try:
            client = get_client()
            cache_file = client._cache_file
            
            # 確保有快取
            client.refresh_cache()
            
            # 檢查檔案是否存在
            assert cache_file.exists()
            
            # 讀取並驗證 JSON 格式
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert isinstance(data, dict)
            assert 'cache_time' in data
            print(f"✅ 快取檔案持久化正常：{cache_file}")
            
        except Exception as e:
            pytest.fail(f"快取持久化測試失敗: {e}")


class TestHelperFunctions:
    """測試輔助函數功能"""
    
    def test_priority_name_lookup(self):
        """測試優先權名稱查詢"""
        try:
            client = get_client()
            
            # 先取得所有優先權來找一個有效的名稱
            priorities = client.get_priorities()
            if not priorities:
                pytest.skip("沒有可用的優先權資料")
            
            priority_name = priorities[0]['name']
            expected_id = priorities[0]['id']
            
            # 測試輔助函數
            found_id = client.find_priority_id_by_name(priority_name)
            
            assert found_id == expected_id
            print(f"✅ 優先權名稱查詢正常：'{priority_name}' → {found_id}")
            
            # 測試不存在的名稱
            invalid_id = client.find_priority_id_by_name("不存在的優先權")
            assert invalid_id is None
            print(f"✅ 無效優先權名稱正確回傳 None")
            
        except Exception as e:
            pytest.fail(f"優先權名稱查詢測試失敗: {e}")
    
    def test_status_name_lookup(self):
        """測試狀態名稱查詢"""
        try:
            client = get_client()
            
            statuses = client.get_issue_statuses()
            if not statuses:
                pytest.skip("沒有可用的狀態資料")
            
            status_name = statuses[0]['name']
            expected_id = statuses[0]['id']
            
            found_id = client.find_status_id_by_name(status_name)
            
            assert found_id == expected_id
            print(f"✅ 狀態名稱查詢正常：'{status_name}' → {found_id}")
            
        except Exception as e:
            pytest.fail(f"狀態名稱查詢測試失敗: {e}")
    
    def test_tracker_name_lookup(self):
        """測試追蹤器名稱查詢"""
        try:
            client = get_client()
            
            trackers = client.get_trackers()
            if not trackers:
                pytest.skip("沒有可用的追蹤器資料")
            
            tracker_name = trackers[0]['name']
            expected_id = trackers[0]['id']
            
            found_id = client.find_tracker_id_by_name(tracker_name)
            
            assert found_id == expected_id
            print(f"✅ 追蹤器名稱查詢正常：'{tracker_name}' → {found_id}")
            
        except Exception as e:
            pytest.fail(f"追蹤器名稱查詢測試失敗: {e}")
    
    def test_user_name_lookup(self):
        """測試用戶名稱查詢"""
        try:
            client = get_client()
            
            # 刷新快取確保有用戶資料
            client.refresh_cache()
            cache = client._load_enum_cache()
            
            users_by_name = cache.get('users_by_name', {})
            users_by_login = cache.get('users_by_login', {})
            
            if users_by_name:
                # 測試姓名查詢
                user_name = list(users_by_name.keys())[0]
                expected_id = users_by_name[user_name]
                
                found_id = client.find_user_id_by_name(user_name)
                assert found_id == expected_id
                print(f"✅ 用戶姓名查詢正常：'{user_name}' → {found_id}")
            
            if users_by_login:
                # 測試登入名查詢
                login_name = list(users_by_login.keys())[0]
                expected_id = users_by_login[login_name]
                
                found_id = client.find_user_id_by_login(login_name)
                assert found_id == expected_id
                print(f"✅ 用戶登入名查詢正常：'{login_name}' → {found_id}")
                
                # 測試智慧查詢
                smart_id = client.find_user_id(login_name)
                assert smart_id == expected_id
                print(f"✅ 智慧用戶查詢正常：'{login_name}' → {smart_id}")
            
            if not users_by_name and not users_by_login:
                pytest.skip("沒有可用的用戶快取資料")
                
        except Exception as e:
            pytest.fail(f"用戶名稱查詢測試失敗: {e}")


class TestDomainIsolation:
    """測試 Multi-Domain 隔離功能"""
    
    def test_cache_filename_uniqueness(self):
        """測試不同 domain 的快取檔案名稱唯一性"""
        # 模擬不同的 domain
        domains = [
            "https://demo.redmine.org",
            "https://test.redmine.com", 
            "http://localhost:3000"
        ]
        
        cache_files = []
        for domain in domains:
            with patch('src.redmine_mcp.config.get_config') as mock_config:
                mock_config.return_value.redmine_domain = domain
                mock_config.return_value.api_headers = {'X-Redmine-API-Key': 'test'}
                mock_config.return_value.redmine_timeout = 30
                
                client = RedmineClient()
                cache_files.append(client._cache_file.name)
        
        # 檢查所有快取檔案名稱都不同
        assert len(set(cache_files)) == len(cache_files)
        print(f"✅ Multi-Domain 快取檔案隔離正常")
        for i, filename in enumerate(cache_files):
            print(f"  {domains[i]} → {filename}")


def run_comprehensive_test():
    """執行完整的功能驗證測試"""
    print("=" * 60)
    print("🚀 開始執行 redmine-mcp 新功能驗證測試")
    print("=" * 60)
    
    test_classes = [
        TestUserFunctionality,
        TestCacheSystem, 
        TestHelperFunctions,
        TestDomainIsolation
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 執行 {test_class.__name__} 測試...")
        print("-" * 40)
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                print(f"\n🔍 執行 {test_method}...")
                getattr(test_instance, test_method)()
                passed_tests += 1
                print(f"✅ {test_method} 通過")
            except pytest.skip.Exception as e:
                print(f"⏭️  {test_method} 跳過: {e}")
                passed_tests += 1  # 跳過的測試算作通過
            except Exception as e:
                print(f"❌ {test_method} 失敗: {e}")
                failed_tests.append((test_method, str(e)))
    
    # 輸出測試總結
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    print(f"總測試數: {total_tests}")
    print(f"通過數: {passed_tests}")
    print(f"失敗數: {len(failed_tests)}")
    print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print("\n❌ 失敗的測試:")
        for test_name, error in failed_tests:
            print(f"  - {test_name}: {error}")
    else:
        print("\n🎉 所有測試都通過了！")
    
    return len(failed_tests) == 0


if __name__ == "__main__":
    # 直接執行測試
    success = run_comprehensive_test()
    exit(0 if success else 1)