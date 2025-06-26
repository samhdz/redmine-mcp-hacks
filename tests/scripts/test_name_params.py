#!/usr/bin/env python3
"""
測試 MCP 工具名稱參數支援功能
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加 src 到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def create_mock_client():
    """建立模擬客戶端"""
    mock_client = MagicMock()
    
    # 模擬快取資料
    mock_client.get_available_priorities.return_value = {
        '低': 5, '正常': 6, '高': 7, '緊急': 8
    }
    mock_client.get_available_statuses.return_value = {
        '新建立': 1, '實作中': 2, '已完成': 3, '已關閉': 4
    }
    mock_client.get_available_trackers.return_value = {
        '臭蟲': 1, '功能': 2, '支援': 3
    }
    mock_client.get_available_users.return_value = {
        'by_name': {'Redmine Admin': 1, '測試 用戶': 2},
        'by_login': {'admin': 1, 'user1': 2}
    }
    
    # 模擬輔助函數
    mock_client.find_priority_id_by_name.side_effect = lambda name: {
        '低': 5, '正常': 6, '高': 7, '緊急': 8
    }.get(name)
    
    mock_client.find_status_id_by_name.side_effect = lambda name: {
        '新建立': 1, '實作中': 2, '已完成': 3, '已關閉': 4
    }.get(name)
    
    mock_client.find_tracker_id_by_name.side_effect = lambda name: {
        '臭蟲': 1, '功能': 2, '支援': 3
    }.get(name)
    
    mock_client.find_user_id_by_name.side_effect = lambda name: {
        'Redmine Admin': 1, '測試 用戶': 2
    }.get(name)
    
    mock_client.find_user_id_by_login.side_effect = lambda name: {
        'admin': 1, 'user1': 2
    }.get(name)
    
    # 模擬更新操作
    mock_client.update_issue.return_value = None
    mock_client.create_issue.return_value = 999  # 新議題 ID
    
    # 模擬議題資料
    mock_issue = MagicMock()
    mock_issue.subject = "測試議題"
    mock_issue.status = {'name': '實作中'}
    mock_issue.priority = {'name': '高'}
    mock_issue.tracker = {'name': '臭蟲'}
    mock_issue.assigned_to = {'name': 'Redmine Admin'}
    mock_client.get_issue.return_value = mock_issue
    
    return mock_client


def test_update_issue_status_with_name():
    """測試使用名稱更新議題狀態"""
    print("🔄 測試 update_issue_status 名稱參數")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import update_issue_status
        from redmine_mcp.redmine_client import get_client
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # 測試有效的狀態名稱
            result = update_issue_status(issue_id=1, status_name="實作中", notes="使用名稱更新狀態")
            
            if "成功" in result:
                print("✅ 有效狀態名稱處理正常")
            else:
                print(f"❌ 有效狀態名稱處理異常: {result}")
                return False
            
            # 驗證是否正確呼叫了輔助函數
            mock_client.find_status_id_by_name.assert_called_with("實作中")
            mock_client.update_issue.assert_called()
            
            # 測試無效的狀態名稱
            result = update_issue_status(issue_id=1, status_name="不存在的狀態")
            
            if "找不到狀態名稱" in result and "可用狀態" in result:
                print("✅ 無效狀態名稱錯誤處理正常")
            else:
                print(f"❌ 無效狀態名稱錯誤處理異常: {result}")
                return False
            
            # 測試沒有提供任何參數
            result = update_issue_status(issue_id=1)
            
            if "必須提供" in result:
                print("✅ 參數驗證正常")
            else:
                print(f"❌ 參數驗證異常: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_update_issue_content_with_names():
    """測試使用名稱更新議題內容"""
    print("\n📝 測試 update_issue_content 名稱參數")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import update_issue_content
        from redmine_mcp.redmine_client import get_client
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # 測試有效的名稱參數
            result = update_issue_content(
                issue_id=1,
                priority_name="高",
                tracker_name="臭蟲",
                subject="更新後的標題"
            )
            
            if "成功" in result:
                print("✅ 有效名稱參數處理正常")
                
                # 驗證輔助函數被正確呼叫
                mock_client.find_priority_id_by_name.assert_called_with("高")
                mock_client.find_tracker_id_by_name.assert_called_with("臭蟲")
                
            else:
                print(f"❌ 有效名稱參數處理異常: {result}")
                return False
            
            # 測試無效的優先級名稱
            result = update_issue_content(issue_id=1, priority_name="超高")
            
            if "找不到優先級名稱" in result and "可用優先級" in result:
                print("✅ 無效優先級名稱錯誤處理正常")
            else:
                print(f"❌ 無效優先級名稱錯誤處理異常: {result}")
                return False
            
            # 測試無效的追蹤器名稱
            result = update_issue_content(issue_id=1, tracker_name="不存在的追蹤器")
            
            if "找不到追蹤器名稱" in result and "可用追蹤器" in result:
                print("✅ 無效追蹤器名稱錯誤處理正常")
            else:
                print(f"❌ 無效追蹤器名稱錯誤處理異常: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_assign_issue_with_names():
    """測試使用名稱指派議題"""
    print("\n👤 測試 assign_issue 名稱參數")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import assign_issue
        from redmine_mcp.redmine_client import get_client
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # 測試有效的用戶姓名
            result = assign_issue(issue_id=1, user_name="Redmine Admin", notes="使用姓名指派")
            
            if "成功" in result:
                print("✅ 有效用戶姓名處理正常")
                mock_client.find_user_id_by_name.assert_called_with("Redmine Admin")
            else:
                print(f"❌ 有效用戶姓名處理異常: {result}")
                return False
            
            # 測試有效的用戶登入名
            result = assign_issue(issue_id=1, user_login="admin", notes="使用登入名指派")
            
            if "成功" in result:
                print("✅ 有效用戶登入名處理正常")
                mock_client.find_user_id_by_login.assert_called_with("admin")
            else:
                print(f"❌ 有效用戶登入名處理異常: {result}")
                return False
            
            # 測試無效的用戶姓名
            result = assign_issue(issue_id=1, user_name="不存在的用戶")
            
            if "找不到用戶姓名" in result and "可用用戶" in result:
                print("✅ 無效用戶姓名錯誤處理正常")
            else:
                print(f"❌ 無效用戶姓名錯誤處理異常: {result}")
                return False
            
            # 測試無效的用戶登入名
            result = assign_issue(issue_id=1, user_login="不存在")
            
            if "找不到用戶登入名" in result and "可用用戶" in result:
                print("✅ 無效用戶登入名錯誤處理正常")
            else:
                print(f"❌ 無效用戶登入名錯誤處理異常: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_new_issue_with_names():
    """測試使用名稱建立新議題"""
    print("\n➕ 測試 create_new_issue 名稱參數")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import create_new_issue
        from redmine_mcp.redmine_client import get_client
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # 測試有效的名稱參數
            result = create_new_issue(
                project_id=1,
                subject="新測試議題",
                description="使用名稱參數建立",
                priority_name="高",
                tracker_name="功能",
                assigned_to_name="Redmine Admin"
            )
            
            if "成功" in result:
                print("✅ 有效名稱參數建立議題正常")
                
                # 驗證輔助函數被正確呼叫
                mock_client.find_priority_id_by_name.assert_called_with("高")
                mock_client.find_tracker_id_by_name.assert_called_with("功能")
                mock_client.find_user_id_by_name.assert_called_with("Redmine Admin")
                
                # 驗證建立議題時使用了正確的 ID
                mock_client.create_issue.assert_called_with(
                    project_id=1,
                    subject="新測試議題",
                    description="使用名稱參數建立",
                    tracker_id=2,    # 功能的 ID
                    priority_id=7,   # 高的 ID  
                    assigned_to_id=1 # Redmine Admin 的 ID
                )
                
            else:
                print(f"❌ 有效名稱參數建立議題異常: {result}")
                return False
            
            # 測試使用登入名指派
            result = create_new_issue(
                project_id=1,
                subject="另一個測試議題",
                assigned_to_login="admin"
            )
            
            if "成功" in result:
                print("✅ 使用登入名指派正常")
                mock_client.find_user_id_by_login.assert_called_with("admin")
            else:
                print(f"❌ 使用登入名指派異常: {result}")
                return False
            
            # 測試無效參數
            test_cases = [
                ("無效優先級", {"priority_name": "超高"}, "找不到優先級名稱"),
                ("無效追蹤器", {"tracker_name": "不存在"}, "找不到追蹤器名稱"),
                ("無效用戶姓名", {"assigned_to_name": "不存在用戶"}, "找不到用戶姓名"),
                ("無效用戶登入名", {"assigned_to_login": "不存在"}, "找不到用戶登入名"),
            ]
            
            for test_name, kwargs, expected_error in test_cases:
                result = create_new_issue(project_id=1, subject="測試議題", **kwargs)
                if expected_error in result:
                    print(f"✅ {test_name}錯誤處理正常")
                else:
                    print(f"❌ {test_name}錯誤處理異常: {result}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backwards_compatibility():
    """測試向後相容性"""
    print("\n🔄 測試向後相容性")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import update_issue_status, update_issue_content, assign_issue, create_new_issue
        from redmine_mcp.redmine_client import get_client
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # 測試使用原有的 ID 參數仍然正常工作
            
            # 更新狀態
            result = update_issue_status(issue_id=1, status_id=2, notes="使用 ID 更新")
            if "成功" in result:
                print("✅ update_issue_status ID 參數向後相容")
            else:
                print(f"❌ update_issue_status ID 參數不相容: {result}")
                return False
            
            # 更新內容
            result = update_issue_content(issue_id=1, priority_id=7, tracker_id=1)
            if "成功" in result:
                print("✅ update_issue_content ID 參數向後相容")
            else:
                print(f"❌ update_issue_content ID 參數不相容: {result}")
                return False
            
            # 指派議題
            result = assign_issue(issue_id=1, user_id=1, notes="使用 ID 指派")
            if "成功" in result:
                print("✅ assign_issue ID 參數向後相容")
            else:
                print(f"❌ assign_issue ID 參數不相容: {result}")
                return False
            
            # 建立議題
            result = create_new_issue(
                project_id=1,
                subject="ID 參數測試",
                tracker_id=2,
                priority_id=6,
                assigned_to_id=1
            )
            if "成功" in result:
                print("✅ create_new_issue ID 參數向後相容")
            else:
                print(f"❌ create_new_issue ID 參數不相容: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_name_params_tests():
    """執行所有名稱參數測試"""
    print("🧪 redmine-mcp 名稱參數支援測試")
    print("=" * 60)
    
    tests = [
        ("update_issue_status 名稱參數", test_update_issue_status_with_name),
        ("update_issue_content 名稱參數", test_update_issue_content_with_names),
        ("assign_issue 名稱參數", test_assign_issue_with_names),
        ("create_new_issue 名稱參數", test_create_new_issue_with_names),
        ("向後相容性", test_backwards_compatibility),
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
    print("📊 名稱參數支援測試結果總結")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"{test_name:<35} {status}")
    
    print(f"\n總測試數: {total}")
    print(f"通過數: {passed}")
    print(f"失敗數: {total - passed}")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有名稱參數支援測試都通過了！")
        print("MCP 工具現在完全支援名稱參數，同時保持向後相容性！")
        print("\n💡 使用範例:")
        print("- update_issue_status(issue_id=1, status_name='實作中')")
        print("- assign_issue(issue_id=1, user_name='Redmine Admin')")
        print("- create_new_issue(project_id=1, subject='test', priority_name='高')")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 個測試失敗，請檢查名稱參數功能")
        return False


if __name__ == "__main__":
    success = run_name_params_tests()
    sys.exit(0 if success else 1)