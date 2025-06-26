"""
MCP 工具測試
"""

import os
import pytest
from unittest.mock import patch, Mock
from redmine_mcp.server import get_issue, update_issue_status, list_project_issues, health_check
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
        mock_issue = RedmineIssue(
            id=123,
            subject='測試議題',
            description='議題描述',
            status={'name': '新建'},
            priority={'name': '正常'},
            project={'name': '測試專案', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': '測試用戶'},
            assigned_to={'name': '指派用戶'},
            created_on='2024-01-01T10:00:00Z',
            updated_on='2024-01-02T15:30:00Z',
            done_ratio=50
        )
        mock_client.get_issue.return_value = mock_issue
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
        mock_client.get_issue.side_effect = Exception("議題不存在")
        mock_get_client.return_value = mock_client
        
        result = get_issue(999)
        
        assert "系統錯誤" in result
        assert "議題不存在" in result
    
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