"""
進階 MCP 工具測試
"""

import os
import pytest
from unittest.mock import patch, Mock
from redmine_mcp.server import (
    update_issue_content, add_issue_note, assign_issue,
    create_new_issue, get_my_issues, close_issue
)
from redmine_mcp.redmine_client import RedmineIssue, RedmineProject


class TestAdvancedMCPTools:
    """進階 MCP 工具測試"""
    
    def setup_method(self):
        """每個測試前的設置"""
        # 確保有測試環境變數
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            pass
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_success(self, mock_get_client):
        """測試更新議題內容成功"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        # 模擬更新後的議題
        updated_issue = RedmineIssue(
            id=123,
            subject='更新後的標題',
            description='更新後的描述',
            status={'name': '進行中'},
            priority={'name': '高'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': '測試用戶'},
            done_ratio=75
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(
            123, 
            subject="更新後的標題", 
            description="更新後的描述",
            done_ratio=75
        )
        
        assert "議題內容更新成功" in result
        assert "更新後的標題" in result
        assert "標題: 更新後的標題" in result
        assert "描述已更新" in result
        assert "完成度: 75%" in result
        
        # 驗證呼叫參數
        mock_client.update_issue.assert_called_once_with(
            123, 
            subject="更新後的標題",
            description="更新後的描述",
            done_ratio=75
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_no_params(self, mock_get_client):
        """測試更新議題內容沒有參數"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123)
        
        assert "錯誤: 請至少提供一個要更新的欄位" in result
        mock_client.update_issue.assert_not_called()
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_invalid_done_ratio(self, mock_get_client):
        """測試更新議題內容無效的完成百分比"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123, done_ratio=150)
        
        assert "錯誤: 完成百分比必須在 0-100 之間" in result
        mock_client.update_issue.assert_not_called()
    
    @patch('redmine_mcp.server.get_client')
    def test_add_issue_note_success(self, mock_get_client):
        """測試新增議題備註成功"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        mock_issue = RedmineIssue(
            id=123,
            subject='測試議題',
            description='描述',
            status={'name': '新建'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': '測試用戶'}
        )
        mock_client.get_issue.return_value = mock_issue
        mock_get_client.return_value = mock_client
        
        result = add_issue_note(123, "這是一個測試備註", private=True)
        
        assert "備註新增成功" in result
        assert "這是一個測試備註" in result
        assert "私有" in result
        
        # 驗證呼叫參數
        mock_client.update_issue.assert_called_once_with(
            123, 
            notes="這是一個測試備註",
            private_notes=True
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_add_issue_note_empty_notes(self, mock_get_client):
        """測試新增議題備註空內容"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = add_issue_note(123, "  ")
        
        assert "錯誤: 備註內容不能為空" in result
        mock_client.update_issue.assert_not_called()
    
    @patch('redmine_mcp.server.get_client')
    def test_assign_issue_success(self, mock_get_client):
        """測試指派議題成功"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='測試議題',
            description='描述',
            status={'name': '新建'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': '測試用戶'},
            assigned_to={'name': '指派用戶', 'id': 456}
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = assign_issue(123, 456, "指派給測試用戶")
        
        assert "議題指派更新成功" in result
        assert "指派給用戶 ID 456" in result
        assert "指派用戶" in result
        assert "指派給測試用戶" in result
        
        # 驗證呼叫參數
        mock_client.update_issue.assert_called_once_with(
            123, 
            assigned_to_id=456,
            notes="指派給測試用戶"
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_assign_issue_unassign(self, mock_get_client):
        """測試取消指派議題"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='測試議題',
            description='描述',
            status={'name': '新建'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': '測試用戶'},
            assigned_to=None
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = assign_issue(123, None)
        
        assert "議題指派更新成功" in result
        assert "取消指派" in result
        assert "未指派" in result
        
        # 驗證呼叫參數
        mock_client.update_issue.assert_called_once_with(123, assigned_to_id=None)
    
    @patch('redmine_mcp.server.get_client')
    def test_create_new_issue_success(self, mock_get_client):
        """測試建立新議題成功"""
        mock_client = Mock()
        mock_client.create_issue.return_value = 789
        
        new_issue = RedmineIssue(
            id=789,
            subject='新議題標題',
            description='新議題描述',
            status={'name': '新建'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': 'Feature'},
            author={'name': '建立用戶'},
            assigned_to={'name': '指派用戶'}
        )
        mock_client.get_issue.return_value = new_issue
        mock_get_client.return_value = mock_client
        
        result = create_new_issue(
            1, 
            "新議題標題", 
            "新議題描述",
            tracker_id=2,
            assigned_to_id=456
        )
        
        assert "新議題建立成功" in result
        assert "議題 ID: #789" in result
        assert "標題: 新議題標題" in result
        assert "專案: 測試專案" in result
        assert "新議題描述" in result
        
        # 驗證呼叫參數
        mock_client.create_issue.assert_called_once_with(
            project_id=1,
            subject="新議題標題",
            description="新議題描述",
            tracker_id=2,
            priority_id=None,
            assigned_to_id=456
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_create_new_issue_empty_subject(self, mock_get_client):
        """測試建立新議題空標題"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = create_new_issue(1, "  ")
        
        assert "錯誤: 議題標題不能為空" in result
        mock_client.create_issue.assert_not_called()
    
    @patch('redmine_mcp.server.get_client')
    def test_get_my_issues_success(self, mock_get_client):
        """測試取得我的議題成功"""
        mock_client = Mock()
        
        # 模擬當前用戶
        mock_client.get_current_user.return_value = {
            'id': 123,
            'firstname': '測試',
            'lastname': '用戶'
        }
        
        # 模擬議題列表
        mock_issues = [
            RedmineIssue(
                id=101,
                subject='我的議題1',
                description='描述1',
                status={'name': '進行中'},
                priority={'name': '正常'},
                project={'name': '專案A', 'id': 1},
                tracker={'name': 'Bug'},
                author={'name': '其他用戶'},
                updated_on='2024-01-01'
            )
        ]
        mock_client.list_issues.return_value = mock_issues
        mock_get_client.return_value = mock_client
        
        result = get_my_issues("open", 10)
        
        assert "指派給 測試 用戶 的議題" in result
        assert "狀態篩選: open" in result
        assert "找到 1 個議題" in result
        assert "我的議題1" in result
        
        # 驗證呼叫參數
        mock_client.list_issues.assert_called_once_with(
            assigned_to_id=123,
            limit=10,
            sort='updated_on:desc',
            status_id='open'
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_close_issue_success(self, mock_get_client):
        """測試關閉議題成功"""
        mock_client = Mock()
        
        # 模擬狀態列表
        mock_client.get_issue_statuses.return_value = [
            {'id': 1, 'name': '新建', 'is_closed': False},
            {'id': 5, 'name': '已關閉', 'is_closed': True}
        ]
        
        mock_client.update_issue.return_value = True
        
        closed_issue = RedmineIssue(
            id=123,
            subject='已關閉議題',
            description='描述',
            status={'name': '已關閉'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': '測試用戶'},
            done_ratio=100
        )
        mock_client.get_issue.return_value = closed_issue
        mock_get_client.return_value = mock_client
        
        result = close_issue(123, "議題已完成", 100)
        
        assert "議題關閉成功" in result
        assert "已關閉議題" in result
        assert "狀態: 已關閉" in result
        assert "完成度: 100%" in result
        assert "關閉備註: 議題已完成" in result
        
        # 驗證呼叫參數
        mock_client.update_issue.assert_called_once_with(
            123,
            status_id=5,
            done_ratio=100,
            notes="議題已完成"
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_close_issue_no_closed_status(self, mock_get_client):
        """測試關閉議題找不到關閉狀態"""
        mock_client = Mock()
        
        # 模擬沒有關閉狀態
        mock_client.get_issue_statuses.return_value = [
            {'id': 1, 'name': '新建', 'is_closed': False},
            {'id': 2, 'name': '進行中', 'is_closed': False}
        ]
        
        mock_get_client.return_value = mock_client
        
        result = close_issue(123)
        
        assert "錯誤: 找不到可用的關閉狀態" in result
        mock_client.update_issue.assert_not_called()