"""
MCP Tool Tests
"""

import os
import pytest
from unittest.mock import patch, Mock
from redmine_mcp.server import get_issue, update_issue_status, update_issue_content, list_project_issues, health_check, get_trackers, get_priorities, get_time_entry_activities, get_document_categories
from redmine_mcp.redmine_client import RedmineIssue, RedmineProject


class TestMCPTools:
    """MCP Tool Tests"""
    
    def setup_method(self):
        """Setup before each test"""
        # Ensure test environment variables
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            pass
    
    @patch('redmine_mcp.server.get_client')
    def test_health_check_success(self, mock_get_client):
        """Test health check success"""
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_get_client.return_value = mock_client
        
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            result = health_check()
        
        assert "✓ Server is running normally" in result
        assert "https://test.redmine.com" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_health_check_connection_failed(self, mock_get_client):
        """Test health check connection failed"""
        mock_client = Mock()
        mock_client.test_connection.return_value = False
        mock_get_client.return_value = mock_client
        
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            result = health_check()
        
        assert "✗ Unable to connect to Redmine server" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_issue_success(self, mock_get_client):
        """Test get issue success"""
        mock_client = Mock()
        # Mock get_issue_raw method, return dict
        mock_issue_data = {
            'id': 123,
            'subject': 'Test Issue',
            'description': 'Issue description',
            'status': {'name': 'New'},
            'priority': {'name': 'Normal'},
            'project': {'name': 'Test Project', 'id': 1},
            'tracker': {'name': 'Bug'},
            'author': {'name': 'Test User'},
            'assigned_to': {'name': 'Assigned User'},
            'created_on': '2024-01-01T10:00:00Z',
            'updated_on': '2024-01-02T15:30:00Z',
            'done_ratio': 50
        }
        mock_client.get_issue_raw.return_value = mock_issue_data
        mock_client.config.redmine_domain = 'https://test.redmine.com'
        mock_get_client.return_value = mock_client
        
        result = get_issue(123)
        
        assert "Issue #123: Test Issue" in result
        assert "Project: Test Project" in result
        assert "Status: New" in result
        assert "Done Ratio: 50%" in result
        assert "Issue description" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_issue_error(self, mock_get_client):
        """Test get issue error"""
        mock_client = Mock()
        mock_client.get_issue_raw.side_effect = Exception("Issue does not exist")
        mock_get_client.return_value = mock_client
        
        result = get_issue(999)
        
        assert "System Error" in result
        assert "Issue does not exist" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_issue_with_notes_and_attachments(self, mock_get_client):
        """Test get issue with notes and attachments"""
        mock_client = Mock()
        # Simulate issue data with journals and attachments
        mock_issue_data = {
            'id': 123,
            'subject': 'Test Issue',
            'description': 'Issue description',
            'status': {'name': 'New'},
            'priority': {'name': 'Normal'},
            'project': {'name': 'Test Project', 'id': 1},
            'tracker': {'name': 'Bug'},
            'author': {'name': 'Test User'},
            'assigned_to': {'name': 'Assigned User'},
            'created_on': '2024-01-01T10:00:00Z',
            'updated_on': '2024-01-02T15:30:00Z',
            'done_ratio': 50,
            'journals': [
                {
                    'id': 1,
                    'user': {'name': 'John Doe'},
                    'notes': 'This is the first note',
                    'created_on': '2024-01-01T11:00:00Z'
                },
                {
                    'id': 2,
                    'user': {'name': 'Jane Smith'},
                    'notes': 'This is the second note',
                    'created_on': '2024-01-01T12:00:00Z'
                }
            ],
            'attachments': [
                {
                    'id': 1,
                    'filename': 'test.jpg',
                    'filesize': 1048576,  # 1MB
                    'content_type': 'image/jpeg',
                    'author': {'name': 'Alice'},
                    'created_on': '2024-01-01T13:00:00Z'
                },
                {
                    'id': 2,
                    'filename': 'document.pdf',
                    'filesize': 512000,  # 500KB
                    'content_type': 'application/pdf',
                    'author': {'name': 'Bob'},
                    'created_on': '2024-01-01T14:00:00Z'
                }
            ]
        }
        mock_client.get_issue_raw.return_value = mock_issue_data
        mock_client.config.redmine_domain = 'https://test.redmine.com'
        mock_get_client.return_value = mock_client
        
        result = get_issue(123, include_details=True)
        
        # Check basic info
        assert "Issue #123: Test Issue" in result
        
        # Check attachment info
        assert "Attachments (2)" in result
        assert "test.jpg" in result
        assert "1.00 MB" in result
        assert "image/jpeg" in result
        assert "document.pdf" in result
        assert "512000 bytes" in result
        assert "application/pdf" in result
        assert "Download link: https://test.redmine.com/attachments/download" in result
        
        # Check notes info
        assert "Notes/History (2)" in result
        assert "John Doe" in result
        assert "This is the first note" in result
        assert "Jane Smith" in result
        assert "This is the second note" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_trackers_success(self, mock_get_client):
        """Test get tracker list success"""
        mock_client = Mock()
        mock_trackers = [
            {
                'id': 1,
                'name': 'Defect',
                'default_status': {'name': 'New'}
            },
            {
                'id': 2,
                'name': 'Feature',
                'default_status': {'name': 'New'}
            },
            {
                'id': 3,
                'name': 'Support',
                'default_status': {'name': 'New'}
            }
        ]
        mock_client.get_trackers.return_value = mock_trackers
        mock_get_client.return_value = mock_client
        
        result = get_trackers()
        
        assert "Available Trackers" in result
        assert "Defect" in result
        assert "Feature" in result
        assert "Support" in result
        assert "New" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_trackers_empty(self, mock_get_client):
        """Test tracker list empty"""
        mock_client = Mock()
        mock_client.get_trackers.return_value = []
        mock_get_client.return_value = mock_client
        
        result = get_trackers()
        
        assert "No trackers found" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_priorities_success(self, mock_get_client):
        """Test get priority list success"""
        mock_client = Mock()
        mock_priorities = [
            {
                'id': 1,
                'name': 'Low',
                'is_default': False
            },
            {
                'id': 2,
                'name': 'Normal',
                'is_default': True
            },
            {
                'id': 3,
                'name': 'High - handle soon',
                'is_default': False
            },
            {
                'id': 4,
                'name': 'Urgent - handle in two days',
                'is_default': False
            },
            {
                'id': 5,
                'name': 'Critical - handle immediately',
                'is_default': False
            }
        ]
        mock_client.get_priorities.return_value = mock_priorities
        mock_get_client.return_value = mock_client
        
        result = get_priorities()
        
        assert "Available Issue Priorities" in result
        assert "Low" in result
        assert "Normal" in result
        assert "High - handle soon" in result
        assert "Urgent - handle in two days" in result
        assert "Critical - handle immediately" in result
        assert "Yes" in result  # Check default marker
        assert "No" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_priorities_empty(self, mock_get_client):
        """Test priority list empty"""
        mock_client = Mock()
        mock_client.get_priorities.return_value = []
        mock_get_client.return_value = mock_client
        
        result = get_priorities()
        
        assert "No issue priorities found" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_time_entry_activities_success(self, mock_get_client):
        """Test get time entry activity list success"""
        mock_client = Mock()
        mock_activities = [
            {
                'id': 1,
                'name': 'Design',
                'is_default': True
            },
            {
                'id': 2,
                'name': 'Development',
                'is_default': False
            },
            {
                'id': 3,
                'name': 'Debug',
                'is_default': False
            },
            {
                'id': 4,
                'name': 'Investigation',
                'is_default': False
            },
            {
                'id': 5,
                'name': 'Discussion',
                'is_default': False
            },
            {
                'id': 6,
                'name': 'Testing',
                'is_default': False
            },
            {
                'id': 7,
                'name': 'Maintenance',
                'is_default': False
            },
            {
                'id': 8,
                'name': 'Documentation',
                'is_default': False
            },
            {
                'id': 9,
                'name': 'Training',
                'is_default': False
            },
            {
                'id': 10,
                'name': 'Translation',
                'is_default': False
            },
            {
                'id': 11,
                'name': 'Other',
                'is_default': False
            }
        ]
        mock_client.get_time_entry_activities.return_value = mock_activities
        mock_get_client.return_value = mock_client
        
        result = get_time_entry_activities()
        
        assert "Available Time Entry Activities" in result
        assert "Design" in result
        assert "Development" in result
        assert "Debug" in result
        assert "Investigation" in result
        assert "Discussion" in result
        assert "Testing" in result
        assert "Maintenance" in result
        assert "Documentation" in result
        assert "Training" in result
        assert "Translation" in result
        assert "Other" in result
        assert "Yes" in result  # Check default marker
        assert "No" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_time_entry_activities_empty(self, mock_get_client):
        """Test time entry activity list empty"""
        mock_client = Mock()
        mock_client.get_time_entry_activities.return_value = []
        mock_get_client.return_value = mock_client
        
        result = get_time_entry_activities()
        
        assert "No time entry activities found" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_document_categories_success(self, mock_get_client):
        """Test get document category list success"""
        mock_client = Mock()
        mock_categories = [
            {
                'id': 1,
                'name': 'User Manual',
                'is_default': True
            },
            {
                'id': 2,
                'name': 'Technical Document',
                'is_default': False
            },
            {
                'id': 3,
                'name': 'Application Form',
                'is_default': False
            },
            {
                'id': 4,
                'name': 'Requirement Document',
                'is_default': False
            }
        ]
        mock_client.get_document_categories.return_value = mock_categories
        mock_get_client.return_value = mock_client
        
        result = get_document_categories()
        
        assert "Available Document Categories" in result
        assert "User Manual" in result
        assert "Technical Document" in result
        assert "Application Form" in result
        assert "Requirement Document" in result
        assert "Yes" in result  # Check default marker
        assert "No" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_get_document_categories_empty(self, mock_get_client):
        """Test document category list empty"""
        mock_client = Mock()
        mock_client.get_document_categories.return_value = []
        mock_get_client.return_value = mock_client
        
        result = get_document_categories()
        
        assert "No document categories found" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_status_success(self, mock_get_client):
        """Test update issue status success"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        # Simulate updated issue
        updated_issue = RedmineIssue(
            id=123,
            subject='Test Issue',
            description='Description',
            status={'name': 'In Progress'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': 'Test User'}
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_status(123, 2, "Status update note")
        
        assert "Issue status updated successfully" in result
        assert "Issue: #123 - Test Issue" in result
        assert "New Status: In Progress" in result
        assert "Note: Status update note" in result
        
        # Verify call arguments
        mock_client.update_issue.assert_called_once_with(123, status_id=2, notes="Status update note")
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_status_without_notes(self, mock_get_client):
        """Test update issue status without note"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='Test Issue',
            description='Description',
            status={'name': 'Resolved'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': 'Test User'}
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_status(123, 3)
        
        assert "Issue status updated successfully" in result
        assert "New Status: Resolved" in result
        assert "Note:" not in result
        
        # Verify call arguments (no notes)
        mock_client.update_issue.assert_called_once_with(123, status_id=3)
    
    @patch('redmine_mcp.server.get_client')
    def test_list_project_issues_success(self, mock_get_client):
        """Test list project issues success"""
        mock_client = Mock()
        
        # Simulate project info
        mock_project = RedmineProject(
            id=1,
            name='Test Project',
            identifier='test-project',
            description='Project description',
            status=1
        )
        mock_client.get_project.return_value = mock_project
        
        # Simulate issue list
        mock_issues = [
            RedmineIssue(
                id=101,
                subject='First Issue',
                description='Desc1',
                status={'name': 'New'},
                priority={'name': 'Normal'},
                project={'name': 'Test Project', 'id': 1},
                tracker={'name': 'Bug'},
                author={'name': 'User1'},
                assigned_to={'name': 'Assigned User1'},
                updated_on='2024-01-01'
            ),
            RedmineIssue(
                id=102,
                subject='Second Issue',
                description='Desc2',
                status={'name': 'In Progress'},
                priority={'name': 'High'},
                project={'name': 'Test Project', 'id': 1},
                tracker={'name': 'Feature'},
                author={'name': 'User2'},
                assigned_to=None,
                updated_on='2024-01-02'
            )
        ]
        mock_client.list_issues.return_value = mock_issues
        mock_get_client.return_value = mock_client
        
        result = list_project_issues(1, "open", 20)
        
        assert "Project: Test Project" in result
        assert "Status Filter: open" in result
        assert "Found 2 issues" in result
        assert "101" in result
        assert "First Issue" in result
        assert "102" in result
        assert "Second Issue" in result
        assert "Assigned User1" in result
        assert "Unassigned" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_list_project_issues_empty(self, mock_get_client):
        """Test list project issues empty"""
        mock_client = Mock()
        mock_client.list_issues.return_value = []
        mock_get_client.return_value = mock_client
        
        result = list_project_issues(1, "all", 10)
        
        assert "No matching issues found in project 1" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_list_project_issues_with_different_filters(self, mock_get_client):
        """Test project issue list with different status filters"""
        mock_client = Mock()
        mock_client.list_issues.return_value = []
        mock_get_client.return_value = mock_client
        
        # Test closed filter
        result = list_project_issues(1, "closed", 10)
        mock_client.list_issues.assert_called_with(
            project_id=1, limit=10, sort='updated_on:desc', status_id='closed'
        )
        
        # Test all filter
        result = list_project_issues(1, "all", 10)
        mock_client.list_issues.assert_called_with(
            project_id=1, limit=10, sort='updated_on:desc'
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_list_project_issues_limit_bounds(self, mock_get_client):
        """Test project issue list limit bounds"""
        mock_client = Mock()
        mock_client.list_issues.return_value = []
        mock_get_client.return_value = mock_client
        
        # Test over max limit
        list_project_issues(1, "open", 150)
        args = mock_client.list_issues.call_args[1]
        assert args['limit'] == 100  # Should be limited to 100
        
        # Test below min limit
        list_project_issues(1, "open", -5)
        args = mock_client.list_issues.call_args[1]
        assert args['limit'] == 1  # Should be set to 1
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_with_tracker(self, mock_get_client):
        """Test update issue content with tracker"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='Updated Title',
            description='Updated Description',
            status={'name': 'New'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Feature'},
            author={'name': 'Test User'},
            done_ratio=50
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123, subject='Updated Title', tracker_id=2, done_ratio=50)
        
        assert "Issue content updated successfully" in result
        assert "Updated Title" in result
        assert "Tracker ID: 2" in result
        assert "Done Ratio: 50%" in result
        assert "Tracker: Feature" in result
        
        # Verify call arguments
        mock_client.update_issue.assert_called_once_with(123, subject='Updated Title', tracker_id=2, done_ratio=50)
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_tracker_only(self, mock_get_client):
        """Test update tracker only"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='Test Issue',
            description='Description',
            status={'name': 'New'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Feature'},
            author={'name': 'Test User'},
            done_ratio=0
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123, tracker_id=2)
        
        assert "Issue content updated successfully" in result
        assert "Tracker ID: 2" in result
        assert "Tracker: Feature" in result
        
        # Verify call arguments
        mock_client.update_issue.assert_called_once_with(123, tracker_id=2)
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_with_dates_and_hours(self, mock_get_client):
        """Test update issue dates and hours"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='Test Issue',
            description='Description',
            status={'name': 'New'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Feature'},
            author={'name': 'Test User'},
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
        
        assert "Issue content updated successfully" in result
        assert "Start Date: 2025-06-26" in result
        assert "Due Date: 2025-06-30" in result
        assert "Estimated Hours: 8.5 hours" in result
        
        # Verify call arguments
        mock_client.update_issue.assert_called_once_with(
            123, 
            start_date='2025-06-26',
            due_date='2025-06-30',
            estimated_hours=8.5
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_invalid_date_format(self, mock_get_client):
        """Test invalid date format"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Test invalid start date
        result = update_issue_content(123, start_date='2025/06/26')
        assert "Error: Start date format must be YYYY-MM-DD" in result
        
        # Test invalid due date
        result = update_issue_content(123, due_date='26-06-2025')
        assert "Error: Due date format must be YYYY-MM-DD" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_invalid_hours(self, mock_get_client):
        """Test invalid estimated hours"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123, estimated_hours=-5.0)
        assert "Error: Estimated hours cannot be negative" in result
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_with_parent_issue(self, mock_get_client):
        """Test set parent issue"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='Test Sub Issue',
            description='Description',
            status={'name': 'New'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Feature'},
            author={'name': 'Test User'},
            done_ratio=0
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123, parent_issue_id=100)
        
        assert "Issue content updated successfully" in result
        assert "Parent Issue ID: 100" in result
        
        # Verify call arguments
        mock_client.update_issue.assert_called_once_with(123, parent_issue_id=100)
