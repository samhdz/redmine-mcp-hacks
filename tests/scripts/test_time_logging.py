#!/usr/bin/env python3
"""
測試時間記錄功能
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
    
    # 模擬時間追蹤活動資料
    mock_client.get_available_time_entry_activities.return_value = {
        '設計': 10, '開發': 11, '除錯': 12, '調查': 13, '討論': 14,
        '測試': 15, '維護': 16, '文件': 17, '教學': 18, '翻譯': 19, '其他': 20
    }
    
    # 模擬輔助函數
    mock_client.find_time_entry_activity_id_by_name.side_effect = lambda name: {
        '設計': 10, '開發': 11, '除錯': 12, '調查': 13, '討論': 14,
        '測試': 15, '維護': 16, '文件': 17, '教學': 18, '翻譯': 19, '其他': 20
    }.get(name)
    
    # 模擬時間記錄建立
    mock_client.create_time_entry.return_value = 123  # 時間記錄 ID
    
    # 模擬議題更新
    mock_client.update_issue.return_value = None
    
    # 模擬議題資料
    mock_issue = MagicMock()
    mock_issue.subject = "測試議題"
    mock_client.get_issue.return_value = mock_issue
    
    return mock_client


def test_add_note_with_time_logging():
    """測試新增備註並記錄時間"""
    print("⏰ 測試新增備註並記錄時間")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import add_issue_note
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # 測試使用活動名稱記錄時間
            result = add_issue_note(
                issue_id=1,
                notes="完成功能開發",
                spent_hours=2.5,
                activity_name="開發"
            )
            
            if "備註新增成功" in result and "時間記錄新增成功" in result:
                print("✅ 使用活動名稱記錄時間正常")
                print(f"   結果包含時間記錄 ID: {'時間記錄 ID: 123' in result}")
                print(f"   結果包含工時: {'2.5 小時' in result}")
                print(f"   結果包含活動: {'開發' in result}")
            else:
                print(f"❌ 使用活動名稱記錄時間異常: {result}")
                return False
            
            # 驗證是否正確呼叫了相關方法
            mock_client.find_time_entry_activity_id_by_name.assert_called_with("開發")
            mock_client.create_time_entry.assert_called()
            mock_client.update_issue.assert_called()
            
            # 測試使用活動 ID 記錄時間
            result = add_issue_note(
                issue_id=1,
                notes="修復 bug",
                spent_hours=1.0,
                activity_id=12
            )
            
            if "備註新增成功" in result and "時間記錄新增成功" in result:
                print("✅ 使用活動 ID 記錄時間正常")
            else:
                print(f"❌ 使用活動 ID 記錄時間異常: {result}")
                return False
            
            # 測試無效的活動名稱
            result = add_issue_note(
                issue_id=1,
                notes="測試備註",
                spent_hours=1.0,
                activity_name="不存在的活動"
            )
            
            if "找不到時間追蹤活動名稱" in result and "可用活動" in result:
                print("✅ 無效活動名稱錯誤處理正常")
            else:
                print(f"❌ 無效活動名稱錯誤處理異常: {result}")
                return False
            
            # 測試無效的工時
            result = add_issue_note(
                issue_id=1,
                notes="測試備註",
                spent_hours=0,
                activity_name="開發"
            )
            
            if "耗用工時必須大於 0" in result:
                print("✅ 無效工時錯誤處理正常")
            else:
                print(f"❌ 無效工時錯誤處理異常: {result}")
                return False
            
            # 測試缺少活動參數
            result = add_issue_note(
                issue_id=1,
                notes="測試備註",
                spent_hours=1.0
            )
            
            if "必須提供 activity_id 或 activity_name 參數" in result:
                print("✅ 缺少活動參數錯誤處理正常")
            else:
                print(f"❌ 缺少活動參數錯誤處理異常: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_add_note_only():
    """測試僅新增備註（向後相容性）"""
    print("\n📝 測試僅新增備註（向後相容性）")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import add_issue_note
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # 測試僅新增備註
            result = add_issue_note(
                issue_id=1,
                notes="僅新增備註"
            )
            
            if "備註新增成功" in result and "時間記錄新增成功" not in result:
                print("✅ 僅新增備註功能正常")
            else:
                print(f"❌ 僅新增備註功能異常: {result}")
                return False
            
            # 驗證沒有呼叫時間記錄相關方法
            mock_client.create_time_entry.assert_not_called()
            
            # 測試私有備註
            result = add_issue_note(
                issue_id=1,
                notes="私有備註",
                private=True
            )
            
            if "備註新增成功" in result and "私有" in result:
                print("✅ 私有備註功能正常")
            else:
                print(f"❌ 私有備註功能異常: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_time_activities():
    """測試時間追蹤活動快取功能"""
    print("\n💾 測試時間追蹤活動快取功能")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client
        
        mock_time_activities = [
            {'id': 10, 'name': '設計'},
            {'id': 11, 'name': '開發'},
            {'id': 12, 'name': '除錯'},
            {'id': 13, 'name': '調查'},
            {'id': 14, 'name': '討論'},
            {'id': 15, 'name': '測試'},
            {'id': 16, 'name': '維護'},
            {'id': 17, 'name': '文件'},
            {'id': 18, 'name': '教學'},
            {'id': 19, 'name': '翻譯'},
            {'id': 20, 'name': '其他'}
        ]
        
        client = get_client()
        
        # 設定模擬快取
        client._enum_cache = {
            'cache_time': 1234567890,
            'domain': 'http://localhost:3000',
            'priorities': {},
            'statuses': {},
            'trackers': {},
            'time_entry_activities': {item['name']: item['id'] for item in mock_time_activities},
            'users_by_name': {},
            'users_by_login': {}
        }
        
        # 測試查詢功能
        test_cases = [
            ('find_time_entry_activity_id_by_name', '開發', 11),
            ('find_time_entry_activity_id_by_name', '測試', 15),
            ('find_time_entry_activity_id_by_name', '不存在', None),
        ]
        
        for method_name, input_value, expected in test_cases:
            method = getattr(client, method_name)
            result = method(input_value)
            
            if result == expected:
                print(f"✅ {method_name}('{input_value}') → {result}")
            else:
                print(f"❌ {method_name}('{input_value}') → {result}, 期望 {expected}")
                return False
        
        # 測試取得所有活動
        activities = client.get_available_time_entry_activities()
        if len(activities) == 11 and activities.get('開發') == 11:
            print(f"✅ get_available_time_entry_activities: {len(activities)} 個活動")
        else:
            print(f"❌ get_available_time_entry_activities 錯誤: {activities}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_time_entry_creation():
    """測試時間記錄建立功能"""
    print("\n🆕 測試時間記錄建立功能")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client
        from datetime import date
        
        client = get_client()
        
        # 模擬 _make_request 方法
        def mock_make_request(method, endpoint, **kwargs):
            if endpoint == '/time_entries.json' and method == 'POST':
                return {'time_entry': {'id': 456}}
            else:
                raise Exception(f"Unexpected request: {method} {endpoint}")
        
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            # 測試建立時間記錄
            time_entry_id = client.create_time_entry(
                issue_id=1,
                hours=2.5,
                activity_id=11,
                comments="開發新功能"
            )
            
            if time_entry_id == 456:
                print("✅ 建立時間記錄功能正常")
            else:
                print(f"❌ 建立時間記錄功能異常: {time_entry_id}")
                return False
            
            # 測試指定日期的時間記錄
            time_entry_id = client.create_time_entry(
                issue_id=1,
                hours=1.0,
                activity_id=12,
                comments="修復 bug",
                spent_on="2025-06-25"
            )
            
            if time_entry_id == 456:
                print("✅ 指定日期時間記錄功能正常")
            else:
                print(f"❌ 指定日期時間記錄功能異常: {time_entry_id}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_time_logging_tests():
    """執行所有時間記錄測試"""
    print("🧪 redmine-mcp 時間記錄功能測試")
    print("=" * 60)
    
    tests = [
        ("時間記錄活動快取功能", test_cache_time_activities),
        ("時間記錄建立功能", test_time_entry_creation),
        ("新增備註並記錄時間", test_add_note_with_time_logging),
        ("僅新增備註（向後相容）", test_add_note_only),
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
    print("📊 時間記錄功能測試結果總結")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"{test_name:<30} {status}")
    
    print(f"\n總測試數: {total}")
    print(f"通過數: {passed}")
    print(f"失敗數: {total - passed}")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有時間記錄功能測試都通過了！")
        print("現在可以在新增議題備註時同時記錄時間！")
        print("\n💡 使用範例:")
        print("- add_issue_note(issue_id=1, notes='開發完成', spent_hours=2.5, activity_name='開發')")
        print("- add_issue_note(issue_id=1, notes='修復 bug', spent_hours=1.0, activity_id=12)")
        print("- add_issue_note(issue_id=1, notes='僅新增備註')  # 向後相容")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 個測試失敗，請檢查時間記錄功能")
        return False


if __name__ == "__main__":
    success = run_time_logging_tests()
    sys.exit(0 if success else 1)