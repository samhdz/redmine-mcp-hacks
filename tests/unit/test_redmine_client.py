"""
Redmine 客戶端測試
"""

import os
import pytest
from unittest.mock import patch, Mock
import requests
from redmine_mcp.redmine_client import (
    RedmineClient, RedmineAPIError, RedmineIssue, RedmineProject,
    get_client, reload_client
)


class TestRedmineClient:
    """RedmineClient 類別測試"""
    
    def setup_method(self):
        """每個測試前的設置"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            self.client = RedmineClient()
    
    def test_client_initialization(self):
        """測試客戶端初始化"""
        assert self.client.config.redmine_domain == 'https://test.redmine.com'
        assert self.client.session.headers['X-Redmine-API-Key'] == 'test_api_key'
        assert self.client.session.timeout == 30
    
    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """測試成功的 API 請求"""
        mock_response = Mock()
        mock_response.json.return_value = {'test': 'data'}
        mock_response.content = b'{"test": "data"}'
        mock_request.return_value = mock_response
        
        result = self.client._make_request('GET', '/test')
        
        assert result == {'test': 'data'}
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_make_request_timeout(self, mock_request):
        """測試請求逾時"""
        mock_request.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(RedmineAPIError, match="請求逾時"):
            self.client._make_request('GET', '/test')
    
    @patch('requests.Session.request')
    def test_make_request_connection_error(self, mock_request):
        """測試連線錯誤"""
        mock_request.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(RedmineAPIError, match="連線失敗"):
            self.client._make_request('GET', '/test')
    
    @patch('requests.Session.request')
    def test_make_request_http_error(self, mock_request):
        """測試 HTTP 錯誤"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'errors': ['Not found']}
        mock_response.content = b'{"errors": ["Not found"]}'
        
        mock_http_error = requests.exceptions.HTTPError()
        mock_http_error.response = mock_response
        mock_response.raise_for_status.side_effect = mock_http_error
        mock_request.return_value = mock_response
        
        with pytest.raises(RedmineAPIError, match="HTTP 錯誤 404"):
            self.client._make_request('GET', '/test')
    
    @patch('requests.Session.request')
    def test_get_issue_success(self, mock_request):
        """測試成功取得議題"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'issue': {
                'id': 1,
                'subject': '測試議題',
                'description': '測試描述',
                'status': {'id': 1, 'name': '新建'},
                'priority': {'id': 2, 'name': '正常'},
                'project': {'id': 1, 'name': '測試專案'},
                'tracker': {'id': 1, 'name': 'Bug'},
                'author': {'id': 1, 'name': '測試用戶'},
                'done_ratio': 0
            }
        }
        mock_response.content = b'content'
        mock_request.return_value = mock_response
        
        issue = self.client.get_issue(1)
        
        assert isinstance(issue, RedmineIssue)
        assert issue.id == 1
        assert issue.subject == '測試議題'
        assert issue.status['name'] == '新建'
    
    @patch('requests.Session.request')
    def test_get_issue_not_found(self, mock_request):
        """測試議題不存在"""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.content = b'{}'
        mock_request.return_value = mock_response
        
        with pytest.raises(RedmineAPIError, match="議題 1 不存在"):
            self.client.get_issue(1)
    
    @patch('requests.Session.request')
    def test_list_issues_success(self, mock_request):
        """測試列出議題"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'issues': [
                {
                    'id': 1,
                    'subject': '議題1',
                    'description': '描述1',
                    'status': {'id': 1, 'name': '新建'},
                    'priority': {'id': 2, 'name': '正常'},
                    'project': {'id': 1, 'name': '專案1'},
                    'tracker': {'id': 1, 'name': 'Bug'},
                    'author': {'id': 1, 'name': '用戶1'}
                },
                {
                    'id': 2,
                    'subject': '議題2',
                    'description': '描述2',
                    'status': {'id': 2, 'name': '進行中'},
                    'priority': {'id': 3, 'name': '高'},
                    'project': {'id': 1, 'name': '專案1'},
                    'tracker': {'id': 2, 'name': 'Feature'},
                    'author': {'id': 2, 'name': '用戶2'}
                }
            ]
        }
        mock_response.content = b'content'
        mock_request.return_value = mock_response
        
        issues = self.client.list_issues()
        
        assert len(issues) == 2
        assert all(isinstance(issue, RedmineIssue) for issue in issues)
        assert issues[0].subject == '議題1'
        assert issues[1].subject == '議題2'
    
    @patch('requests.Session.request')
    def test_update_issue_success(self, mock_request):
        """測試更新議題"""
        mock_response = Mock()
        mock_response.content = b''
        mock_request.return_value = mock_response
        
        result = self.client.update_issue(1, subject='新標題', status_id=2)
        
        assert result is True
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]['json']['issue']['subject'] == '新標題'
        assert call_args[1]['json']['issue']['status_id'] == 2
    
    def test_update_issue_no_fields(self):
        """測試更新議題但沒有提供欄位"""
        with pytest.raises(RedmineAPIError, match="沒有提供要更新的欄位"):
            self.client.update_issue(1)
    
    @patch('requests.Session.request')
    def test_get_project_success(self, mock_request):
        """測試取得專案"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'project': {
                'id': 1,
                'name': '測試專案',
                'identifier': 'test-project',
                'description': '專案描述',
                'status': 1
            }
        }
        mock_response.content = b'content'
        mock_request.return_value = mock_response
        
        project = self.client.get_project(1)
        
        assert isinstance(project, RedmineProject)
        assert project.id == 1
        assert project.name == '測試專案'
        assert project.identifier == 'test-project'
    
    @patch('requests.Session.request')
    def test_test_connection_success(self, mock_request):
        """測試連線成功"""
        mock_response = Mock()
        mock_response.json.return_value = {'user': {'id': 1, 'login': 'test'}}
        mock_response.content = b'content'
        mock_request.return_value = mock_response
        
        result = self.client.test_connection()
        
        assert result is True
    
    @patch('requests.Session.request')
    def test_test_connection_failure(self, mock_request):
        """測試連線失敗"""
        mock_request.side_effect = RedmineAPIError("連線失敗")
        
        result = self.client.test_connection()
        
        assert result is False


class TestClientSingleton:
    """測試客戶端單例模式"""
    
    def test_get_client_singleton(self):
        """測試 get_client 回傳同一個實例"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            client1 = get_client()
            client2 = get_client()
            
            assert client1 is client2
    
    def test_reload_client(self):
        """測試 reload_client 建立新實例"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            client1 = get_client()
            client2 = reload_client()
            
            assert client1 is not client2
            assert client1.config.redmine_domain == client2.config.redmine_domain