"""
資料驗證器測試
"""

import pytest
from redmine_mcp.validators import (
    RedmineValidator, RedmineValidationError, ValidationResult,
    validate_and_clean_data
)


class TestRedmineValidator:
    """RedmineValidator 測試"""
    
    def test_validate_issue_data_success(self):
        """測試議題資料驗證成功"""
        data = {
            'project_id': 1,
            'subject': '測試議題',
            'description': '測試描述',
            'tracker_id': 1,
            'status_id': 1,
            'priority_id': 2,
            'assigned_to_id': 3,
            'done_ratio': 50
        }
        
        result = RedmineValidator.validate_issue_data(data)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_issue_data_missing_required_fields(self):
        """測試議題資料缺少必填欄位"""
        data = {'description': '只有描述'}
        
        result = RedmineValidator.validate_issue_data(data)
        
        assert not result.is_valid
        assert "專案 ID (project_id) 為必填欄位" in result.errors
        assert "議題標題 (subject) 為必填欄位" in result.errors
    
    def test_validate_issue_data_invalid_subject(self):
        """測試無效的議題標題"""
        # 空標題
        data = {'project_id': 1, 'subject': ''}
        result = RedmineValidator.validate_issue_data(data)
        assert not result.is_valid
        assert "議題標題不能為空" in result.errors
        
        # 過長標題
        data = {'project_id': 1, 'subject': 'x' * 300}
        result = RedmineValidator.validate_issue_data(data)
        assert not result.is_valid
        assert "議題標題長度不能超過 255 字元" in result.errors
        
        # 非字串類型
        data = {'project_id': 1, 'subject': 123}
        result = RedmineValidator.validate_issue_data(data)
        assert not result.is_valid
        assert "議題標題必須為文字格式" in result.errors
    
    def test_validate_issue_data_invalid_ids(self):
        """測試無效的 ID 欄位"""
        data = {
            'project_id': -1,
            'subject': '測試',
            'tracker_id': 0,
            'assigned_to_id': 'invalid'
        }
        
        result = RedmineValidator.validate_issue_data(data)
        
        assert not result.is_valid
        assert "project_id 必須為正整數" in result.errors
        assert "tracker_id 必須為正整數" in result.errors
        assert "assigned_to_id 必須為正整數" in result.errors
    
    def test_validate_issue_data_invalid_done_ratio(self):
        """測試無效的完成百分比"""
        data = {'project_id': 1, 'subject': '測試', 'done_ratio': 150}
        
        result = RedmineValidator.validate_issue_data(data)
        
        assert not result.is_valid
        assert "完成百分比 (done_ratio) 必須為 0-100 之間的整數" in result.errors
    
    def test_validate_issue_data_update_mode(self):
        """測試更新模式下的驗證"""
        # 更新模式不需要必填欄位
        data = {'subject': '更新的標題'}
        
        result = RedmineValidator.validate_issue_data(data, is_update=True)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_project_data_success(self):
        """測試專案資料驗證成功"""
        data = {
            'name': '測試專案',
            'identifier': 'test-project',
            'description': '專案描述',
            'is_public': True,
            'inherit_members': False
        }
        
        result = RedmineValidator.validate_project_data(data)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_project_data_missing_required_fields(self):
        """測試專案資料缺少必填欄位"""
        data = {'description': '只有描述'}
        
        result = RedmineValidator.validate_project_data(data)
        
        assert not result.is_valid
        assert "專案名稱 (name) 為必填欄位" in result.errors
        assert "專案識別碼 (identifier) 為必填欄位" in result.errors
    
    def test_validate_project_data_invalid_identifier(self):
        """測試無效的專案識別碼"""
        # 包含大寫字母
        data = {'name': '測試', 'identifier': 'Test-Project'}
        result = RedmineValidator.validate_project_data(data)
        assert not result.is_valid
        assert "專案識別碼只能包含小寫字母、數字、破折號和底線" in result.errors
        
        # 包含空格
        data = {'name': '測試', 'identifier': 'test project'}
        result = RedmineValidator.validate_project_data(data)
        assert not result.is_valid
        assert "專案識別碼只能包含小寫字母、數字、破折號和底線" in result.errors
        
        # 過長
        data = {'name': '測試', 'identifier': 'x' * 150}
        result = RedmineValidator.validate_project_data(data)
        assert not result.is_valid
        assert "專案識別碼長度不能超過 100 字元" in result.errors
    
    def test_validate_query_params_success(self):
        """測試查詢參數驗證成功"""
        params = {
            'project_id': 1,
            'status_id': 2,
            'limit': 50,
            'offset': 0,
            'created_on': '2024-01-01',
            'sort': 'created_on:desc'
        }
        
        result = RedmineValidator.validate_query_params(params)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_query_params_invalid_pagination(self):
        """測試無效的分頁參數"""
        params = {'limit': -1, 'offset': -5}
        
        result = RedmineValidator.validate_query_params(params)
        
        assert not result.is_valid
        assert "分頁限制 (limit) 必須為正整數" in result.errors
        assert "分頁偏移 (offset) 必須為非負整數" in result.errors
    
    def test_validate_query_params_date_formats(self):
        """測試日期格式驗證"""
        # 有效格式
        valid_dates = [
            '2024-01-01',
            '>=2024-01-01',
            '<=2024-12-31',
            '2024-01-01|2024-12-31',
            '2024-01-01T10:30:00Z'
        ]
        
        for date in valid_dates:
            params = {'created_on': date}
            result = RedmineValidator.validate_query_params(params)
            assert result.is_valid, f"日期格式 {date} 應該有效"
        
        # 無效格式
        invalid_dates = ['2024/01/01', 'invalid-date', '2024-13-01']
        
        for date in invalid_dates:
            params = {'created_on': date}
            result = RedmineValidator.validate_query_params(params)
            assert not result.is_valid, f"日期格式 {date} 應該無效"
    
    def test_get_friendly_error_message(self):
        """測試友好錯誤訊息轉換"""
        # 測試 401 錯誤
        error = Exception("HTTP 401 Unauthorized")
        message = RedmineValidator.get_friendly_error_message(error)
        assert "認證失敗" in message
        
        # 測試 404 錯誤與議題相關
        error = Exception("HTTP 404 Not Found")
        message = RedmineValidator.get_friendly_error_message(error, "issue")
        assert "找不到指定的議題" in message
        
        # 測試連線錯誤
        error = Exception("Connection failed")
        message = RedmineValidator.get_friendly_error_message(error)
        assert "連線失敗" in message


class TestValidateAndCleanData:
    """測試資料驗證和清理函數"""
    
    def test_validate_and_clean_issue_data_success(self):
        """測試議題資料驗證和清理成功"""
        data = {
            'project_id': 1,
            'subject': '測試議題',
            'description': '',  # 空字串應被移除
            'tracker_id': None,  # None 值應被移除
            'status_id': 1
        }
        
        cleaned = validate_and_clean_data(data, "issue")
        
        assert 'project_id' in cleaned
        assert 'subject' in cleaned
        assert 'status_id' in cleaned
        assert 'description' not in cleaned  # 空字串被移除
        assert 'tracker_id' not in cleaned   # None 值被移除
    
    def test_validate_and_clean_data_validation_error(self):
        """測試驗證失敗時拋出錯誤"""
        data = {'subject': ''}  # 缺少必填欄位
        
        with pytest.raises(RedmineValidationError) as exc_info:
            validate_and_clean_data(data, "issue")
        
        assert "資料驗證失敗" in str(exc_info.value)
        assert len(exc_info.value.errors) > 0
    
    def test_validate_and_clean_data_invalid_type(self):
        """測試無效的驗證類型"""
        data = {'test': 'data'}
        
        with pytest.raises(ValueError, match="不支援的驗證類型"):
            validate_and_clean_data(data, "invalid_type")