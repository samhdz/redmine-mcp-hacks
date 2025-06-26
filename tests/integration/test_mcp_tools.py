"""
MCP 工具測試
"""

import os
import pytest
from unittest.mock import patch, Mock
from redmine_mcp.server import get_issue, update_issue_status, update_issue_content, list_project_issues, health_check, get_trackers, get_priorities, get_time_entry_activities, get_document_categories
from redmine_mcp.redmine_client import RedmineIssue, RedmineProject


class TestMCPTools:
    """MCP 工具測試"""
    
    def setup_method(self):
        """每個測試前的設置"""
        # 確保有測試環境變數
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            pass
    
    @patch('redmine_mcp.server.get_client')
    def test_health_check_success(self, mock_get_client):
        """測試健康檢查成功"""
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_get_client.return_value = mock_client
        
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            result = health_check()
        
        assert "✓ 服務器正常運作" in result
        assert "https://test.redmine.com" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_health_check_connection_failed(self, mock_get_client):
        """測試健康檢查連線失敗"""
        mock_client = Mock()
        mock_client.test_connection.return_value = False
        mock_get_client.return_value = mock_client
        
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            result = health_check()
        
        assert "✗ 無法連接到 Redmine 服務器" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_issue_success(self, mock_get_client):
        """測試取得議題成功"""
        mock_client = Mock()
        # 改為 mock get_issue_raw 方法，回傳字典格式
        mock_issue_data = {
            'id': 123,
            'subject': '測試議題',
            'description': '議題描述',
            'status': {'name': '新建'},
            'priority': {'name': '正常'},
            'project': {'name': '測試專案', 'id': 1},
            'tracker': {'name': 'Bug'},
            'author': {'name': '測試用戶'},
            'assigned_to': {'name': '指派用戶'},
            'created_on': '2024-01-01T10:00:00Z',
            'updated_on': '2024-01-02T15:30:00Z',
            'done_ratio': 50
        }
        mock_client.get_issue_raw.return_value = mock_issue_data
        mock_client.config.redmine_domain = 'https://test.redmine.com'
        mock_get_client.return_value = mock_client
        
        result = get_issue(123)
        
        assert "議題 #123: 測試議題" in result
        assert "專案: 測試專案" in result
        assert "狀態: 新建" in result
        assert "完成度: 50%" in result
        assert "議題描述" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_issue_error(self, mock_get_client):
        """測試取得議題錯誤"""
        mock_client = Mock()
        mock_client.get_issue_raw.side_effect = Exception("議題不存在")
        mock_get_client.return_value = mock_client
        
        result = get_issue(999)
        
        assert "系統錯誤" in result
        assert "議題不存在" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_issue_with_notes_and_attachments(self, mock_get_client):
        """測試取得議題包含備註和附件"""
        mock_client = Mock()
        # 模擬包含 journals 和 attachments 的議題資料
        mock_issue_data = {
            'id': 123,
            'subject': '測試議題',
            'description': '議題描述',
            'status': {'name': '新建'},
            'priority': {'name': '正常'},
            'project': {'name': '測試專案', 'id': 1},
            'tracker': {'name': 'Bug'},
            'author': {'name': '測試用戶'},
            'assigned_to': {'name': '指派用戶'},
            'created_on': '2024-01-01T10:00:00Z',
            'updated_on': '2024-01-02T15:30:00Z',
            'done_ratio': 50,
            'journals': [
                {
                    'id': 1,
                    'user': {'name': '張三'},
                    'notes': '這是第一個備註',
                    'created_on': '2024-01-01T11:00:00Z'
                },
                {
                    'id': 2,
                    'user': {'name': '李四'},
                    'notes': '這是第二個備註',
                    'created_on': '2024-01-01T12:00:00Z'
                }
            ],
            'attachments': [
                {
                    'id': 1,
                    'filename': 'test.jpg',
                    'filesize': 1048576,  # 1MB
                    'content_type': 'image/jpeg',
                    'author': {'name': '王五'},
                    'created_on': '2024-01-01T13:00:00Z'
                },
                {
                    'id': 2,
                    'filename': 'document.pdf',
                    'filesize': 512000,  # 500KB
                    'content_type': 'application/pdf',
                    'author': {'name': '趙六'},
                    'created_on': '2024-01-01T14:00:00Z'
                }
            ]
        }
        mock_client.get_issue_raw.return_value = mock_issue_data
        mock_client.config.redmine_domain = 'https://test.redmine.com'
        mock_get_client.return_value = mock_client
        
        result = get_issue(123, include_details=True)
        
        # 檢查基本資訊
        assert "議題 #123: 測試議題" in result
        
        # 檢查附件資訊
        assert "附件 (2 個)" in result
        assert "test.jpg" in result
        assert "1.00 MB" in result
        assert "image/jpeg" in result
        assert "document.pdf" in result
        assert "512000 bytes" in result
        assert "application/pdf" in result
        assert "下載連結: https://test.redmine.com/attachments/download" in result
        
        # 檢查備註資訊
        assert "備註/歷史記錄 (2 筆)" in result
        assert "張三" in result
        assert "這是第一個備註" in result
        assert "李四" in result
        assert "這是第二個備註" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_trackers_success(self, mock_get_client):
        """測試取得追蹤器列表成功"""
        mock_client = Mock()
        mock_trackers = [
            {
                'id': 1,
                'name': '缺陷',
                'default_status': {'name': '新建'}
            },
            {
                'id': 2,
                'name': '功能',
                'default_status': {'name': '新建'}
            },
            {
                'id': 3,
                'name': '支援',
                'default_status': {'name': '新建'}
            }
        ]
        mock_client.get_trackers.return_value = mock_trackers
        mock_get_client.return_value = mock_client
        
        result = get_trackers()
        
        assert "可用的追蹤器" in result
        assert "缺陷" in result
        assert "功能" in result
        assert "支援" in result
        assert "新建" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_trackers_empty(self, mock_get_client):
        """測試追蹤器列表為空"""
        mock_client = Mock()
        mock_client.get_trackers.return_value = []
        mock_get_client.return_value = mock_client
        
        result = get_trackers()
        
        assert "沒有找到追蹤器" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_priorities_success(self, mock_get_client):
        """測試取得優先級列表成功"""
        mock_client = Mock()
        mock_priorities = [
            {
                'id': 1,
                'name': '低',
                'is_default': False
            },
            {
                'id': 2,
                'name': '正常',
                'is_default': True
            },
            {
                'id': 3,
                'name': '高-這邊拜處理',
                'is_default': False
            },
            {
                'id': 4,
                'name': '速-這兩天處理',
                'is_default': False
            },
            {
                'id': 5,
                'name': '急-馬上處理',
                'is_default': False
            }
        ]
        mock_client.get_priorities.return_value = mock_priorities
        mock_get_client.return_value = mock_client
        
        result = get_priorities()
        
        assert "可用的議題優先級" in result
        assert "低" in result
        assert "正常" in result
        assert "高-這邊拜處理" in result
        assert "速-這兩天處理" in result
        assert "急-馬上處理" in result
        assert "是" in result  # 檢查預設標記
        assert "否" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_priorities_empty(self, mock_get_client):
        """測試優先級列表為空"""
        mock_client = Mock()
        mock_client.get_priorities.return_value = []
        mock_get_client.return_value = mock_client
        
        result = get_priorities()
        
        assert "沒有找到議題優先級" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_time_entry_activities_success(self, mock_get_client):
        """測試取得時間追蹤活動列表成功"""
        mock_client = Mock()
        mock_activities = [
            {
                'id': 1,
                'name': '設計',
                'is_default': True
            },
            {
                'id': 2,
                'name': '開發',
                'is_default': False
            },
            {
                'id': 3,
                'name': '除錯',
                'is_default': False
            },
            {
                'id': 4,
                'name': '調查',
                'is_default': False
            },
            {
                'id': 5,
                'name': '討論',
                'is_default': False
            },
            {
                'id': 6,
                'name': '測試',
                'is_default': False
            },
            {
                'id': 7,
                'name': '維護',
                'is_default': False
            },
            {
                'id': 8,
                'name': '文件',
                'is_default': False
            },
            {
                'id': 9,
                'name': '教學',
                'is_default': False
            },
            {
                'id': 10,
                'name': '翻譯',
                'is_default': False
            },
            {
                'id': 11,
                'name': '其他',
                'is_default': False
            }
        ]
        mock_client.get_time_entry_activities.return_value = mock_activities
        mock_get_client.return_value = mock_client
        
        result = get_time_entry_activities()
        
        assert "可用的時間追蹤活動" in result
        assert "設計" in result
        assert "開發" in result
        assert "除錯" in result
        assert "調查" in result
        assert "討論" in result
        assert "測試" in result
        assert "維護" in result
        assert "文件" in result
        assert "教學" in result
        assert "翻譯" in result
        assert "其他" in result
        assert "是" in result  # 檢查預設標記
        assert "否" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_time_entry_activities_empty(self, mock_get_client):
        """測試時間追蹤活動列表為空"""
        mock_client = Mock()
        mock_client.get_time_entry_activities.return_value = []
        mock_get_client.return_value = mock_client
        
        result = get_time_entry_activities()
        
        assert "沒有找到時間追蹤活動" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_document_categories_success(self, mock_get_client):
        """測試取得文件分類列表成功"""
        mock_client = Mock()
        mock_categories = [
            {
                'id': 1,
                'name': '使用手冊',
                'is_default': True
            },
            {
                'id': 2,
                'name': '技術文件',
                'is_default': False
            },
            {
                'id': 3,
                'name': '申請表單',
                'is_default': False
            },
            {
                'id': 4,
                'name': '需求文件',
                'is_default': False
            }
        ]
        mock_client.get_document_categories.return_value = mock_categories
        mock_get_client.return_value = mock_client
        
        result = get_document_categories()
        
        assert "可用的文件分類" in result
        assert "使用手冊" in result
        assert "技術文件" in result
        assert "申請表單" in result
        assert "需求文件" in result
        assert "是" in result  # 檢查預設標記
        assert "否" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_document_categories_empty(self, mock_get_client):
        """測試文件分類列表為空"""
        mock_client = Mock()
        mock_client.get_document_categories.return_value = []
        mock_get_client.return_value = mock_client
        
        result = get_document_categories()
        
        assert "沒有找到文件分類" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_status_success(self, mock_get_client):
        """測試更新議題狀態成功"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        # 模擬更新後的議題
        updated_issue = RedmineIssue(
            id=123,
            subject='測試議題',
            description='描述',
            status={'name': '進行中'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': '測試用戶'}
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_status(123, 2, "狀態更新備註")
        
        assert "議題狀態更新成功" in result
        assert "議題: #123 - 測試議題" in result
        assert "新狀態: 進行中" in result
        assert "備註: 狀態更新備註" in result
        
        # 驗證呼叫參數
        mock_client.update_issue.assert_called_once_with(123, status_id=2, notes="狀態更新備註")
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_status_without_notes(self, mock_get_client):
        """測試更新議題狀態不含備註"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='測試議題',
            description='描述',
            status={'name': '已解決'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': '測試用戶'}
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_status(123, 3)
        
        assert "議題狀態更新成功" in result
        assert "新狀態: 已解決" in result
        assert "備註:" not in result
        
        # 驗證呼叫參數（沒有 notes）
        mock_client.update_issue.assert_called_once_with(123, status_id=3)
    
    @patch('redmine_mcp.server.get_client')
    def test_list_project_issues_success(self, mock_get_client):
        """測試列出專案議題成功"""
        mock_client = Mock()
        
        # 模擬專案資訊
        mock_project = RedmineProject(
            id=1,
            name='測試專案',
            identifier='test-project',
            description='專案描述',
            status=1
        )
        mock_client.get_project.return_value = mock_project
        
        # 模擬議題列表
        mock_issues = [
            RedmineIssue(
                id=101,
                subject='第一個議題',
                description='描述1',
                status={'name': '新建'},
                priority={'name': '正常'},
                project={'name': '測試專案', 'id': 1},
                tracker={'name': 'Bug'},
                author={'name': '用戶1'},
                assigned_to={'name': '指派用戶1'},
                updated_on='2024-01-01'
            ),
            RedmineIssue(
                id=102,
                subject='第二個議題',
                description='描述2',
                status={'name': '進行中'},
                priority={'name': '高'},
                project={'name': '測試專案', 'id': 1},
                tracker={'name': 'Feature'},
                author={'name': '用戶2'},
                assigned_to=None,
                updated_on='2024-01-02'
            )
        ]
        mock_client.list_issues.return_value = mock_issues
        mock_get_client.return_value = mock_client
        
        result = list_project_issues(1, "open", 20)
        
        assert "專案: 測試專案" in result
        assert "狀態篩選: open" in result
        assert "找到 2 個議題" in result
        assert "101" in result
        assert "第一個議題" in result
        assert "102" in result
        assert "第二個議題" in result
        assert "指派用戶1" in result
        assert "未指派" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_list_project_issues_empty(self, mock_get_client):
        """測試列出專案議題為空"""
        mock_client = Mock()
        mock_client.list_issues.return_value = []
        mock_get_client.return_value = mock_client
        
        result = list_project_issues(1, "all", 10)
        
        assert "專案 1 中沒有找到符合條件的議題" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_list_project_issues_with_different_filters(self, mock_get_client):
        """測試不同狀態篩選的專案議題列表"""
        mock_client = Mock()
        mock_client.list_issues.return_value = []
        mock_get_client.return_value = mock_client
        
        # 測試 closed 篩選
        result = list_project_issues(1, "closed", 10)
        mock_client.list_issues.assert_called_with(
            project_id=1, limit=10, sort='updated_on:desc', status_id='closed'
        )
        
        # 測試 all 篩選
        result = list_project_issues(1, "all", 10)
        mock_client.list_issues.assert_called_with(
            project_id=1, limit=10, sort='updated_on:desc'
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_list_project_issues_limit_bounds(self, mock_get_client):
        """測試專案議題列表的限制邊界"""
        mock_client = Mock()
        mock_client.list_issues.return_value = []
        mock_get_client.return_value = mock_client
        
        # 測試超過最大限制
        list_project_issues(1, "open", 150)
        args = mock_client.list_issues.call_args[1]
        assert args['limit'] == 100  # 應該被限制到 100
        
        # 測試低於最小限制
        list_project_issues(1, "open", -5)
        args = mock_client.list_issues.call_args[1]
        assert args['limit'] == 1  # 應該被設為 1
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_with_tracker(self, mock_get_client):
        """測試更新議題內容包含追蹤器"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='更新的標題',
            description='更新的描述',
            status={'name': '新建立'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': '功能'},
            author={'name': '測試用戶'},
            done_ratio=50
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123, subject='更新的標題', tracker_id=2, done_ratio=50)
        
        assert "議題內容更新成功" in result
        assert "更新的標題" in result
        assert "追蹤器 ID: 2" in result
        assert "完成度: 50%" in result
        assert "追蹤器: 功能" in result
        
        # 驗證呼叫參數
        mock_client.update_issue.assert_called_once_with(123, subject='更新的標題', tracker_id=2, done_ratio=50)
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_tracker_only(self, mock_get_client):
        """測試只更新追蹤器"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='測試議題',
            description='描述',
            status={'name': '新建立'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': '功能'},
            author={'name': '測試用戶'},
            done_ratio=0
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123, tracker_id=2)
        
        assert "議題內容更新成功" in result
        assert "追蹤器 ID: 2" in result
        assert "追蹤器: 功能" in result
        
        # 驗證呼叫參數
        mock_client.update_issue.assert_called_once_with(123, tracker_id=2)
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_with_dates_and_hours(self, mock_get_client):
        """測試更新議題日期和工時"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='測試議題',
            description='描述',
            status={'name': '新建立'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': '功能'},
            author={'name': '測試用戶'},
            done_ratio=0
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(
            123, 
            start_date='2025-06-26',
            due_date='2025-06-30',
            estimated_hours=8.5
        )
        
        assert "議題內容更新成功" in result
        assert "開始日期: 2025-06-26" in result
        assert "完成日期: 2025-06-30" in result
        assert "預估工時: 8.5 小時" in result
        
        # 驗證呼叫參數
        mock_client.update_issue.assert_called_once_with(
            123, 
            start_date='2025-06-26',
            due_date='2025-06-30',
            estimated_hours=8.5
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_invalid_date_format(self, mock_get_client):
        """測試無效日期格式"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # 測試無效開始日期
        result = update_issue_content(123, start_date='2025/06/26')
        assert "錯誤: 開始日期格式必須為 YYYY-MM-DD" in result
        
        # 測試無效完成日期
        result = update_issue_content(123, due_date='26-06-2025')
        assert "錯誤: 完成日期格式必須為 YYYY-MM-DD" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_invalid_hours(self, mock_get_client):
        """測試無效工時"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123, estimated_hours=-5.0)
        assert "錯誤: 預估工時不能為負數" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_with_parent_issue(self, mock_get_client):
        """測試設定父議題"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='測試子議題',
            description='描述',
            status={'name': '新建立'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': '功能'},
            author={'name': '測試用戶'},
            done_ratio=0
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123, parent_issue_id=100)
        
        assert "議題內容更新成功" in result
        assert "父議題 ID: 100" in result
        
        # 驗證呼叫參數
        mock_client.update_issue.assert_called_once_with(123, parent_issue_id=100)