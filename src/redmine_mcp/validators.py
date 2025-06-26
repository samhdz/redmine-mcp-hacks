"""
資料驗證和錯誤回饋機制
負責驗證 API 請求參數和提供友好的錯誤訊息
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """驗證結果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class RedmineValidationError(Exception):
    """Redmine 資料驗證錯誤"""
    def __init__(self, message: str, field: str = None, errors: List[str] = None):
        super().__init__(message)
        self.field = field
        self.errors = errors or [message]


class RedmineValidator:
    """Redmine 資料驗證器"""
    
    # 驗證規則常數
    MAX_SUBJECT_LENGTH = 255
    MAX_DESCRIPTION_LENGTH = 65535
    MAX_PROJECT_NAME_LENGTH = 255
    MAX_PROJECT_IDENTIFIER_LENGTH = 100
    MIN_PROJECT_IDENTIFIER_LENGTH = 1
    
    # 專案識別碼格式：只能包含小寫字母、數字、破折號和底線
    PROJECT_IDENTIFIER_PATTERN = re.compile(r'^[a-z0-9\-_]+$')
    
    # 日期格式：YYYY-MM-DD 或 YYYY-MM-DDTHH:MM:SSZ
    DATE_PATTERNS = [
        re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'),  # YYYY-MM-DD (with validation)
        re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])T\d{2}:\d{2}:\d{2}Z?$'),  # ISO format
        re.compile(r'^>=\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'),  # >=YYYY-MM-DD
        re.compile(r'^<=\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'),  # <=YYYY-MM-DD
        re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\|\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$')  # date range
    ]
    
    @classmethod
    def validate_issue_data(cls, data: Dict[str, Any], is_update: bool = False) -> ValidationResult:
        """驗證議題資料"""
        errors = []
        warnings = []
        
        # 必要欄位檢查（建立時）
        if not is_update:
            if 'project_id' not in data:
                errors.append("專案 ID (project_id) 為必填欄位")
            if 'subject' not in data:
                errors.append("議題標題 (subject) 為必填欄位")
            elif not isinstance(data.get('subject'), str) or not data.get('subject', '').strip():
                errors.append("議題標題 (subject) 為必填欄位")
        
        # 議題標題驗證
        if 'subject' in data:
            subject = data['subject']
            if not isinstance(subject, str):
                errors.append("議題標題必須為文字格式")
            elif len(subject.strip()) == 0:
                errors.append("議題標題不能為空")
            elif len(subject) > cls.MAX_SUBJECT_LENGTH:
                errors.append(f"議題標題長度不能超過 {cls.MAX_SUBJECT_LENGTH} 字元")
        
        # 議題描述驗證
        if 'description' in data:
            description = data['description']
            if description is not None and not isinstance(description, str):
                errors.append("議題描述必須為文字格式")
            elif description and len(description) > cls.MAX_DESCRIPTION_LENGTH:
                errors.append(f"議題描述長度不能超過 {cls.MAX_DESCRIPTION_LENGTH} 字元")
        
        # ID 欄位驗證
        id_fields = ['project_id', 'tracker_id', 'status_id', 'priority_id', 'assigned_to_id', 'parent_issue_id']
        for field in id_fields:
            if field in data:
                value = data[field]
                if value is not None and (not isinstance(value, int) or value <= 0):
                    errors.append(f"{field} 必須為正整數")
        
        # 完成百分比驗證
        if 'done_ratio' in data:
            done_ratio = data['done_ratio']
            if not isinstance(done_ratio, int) or done_ratio < 0 or done_ratio > 100:
                errors.append("完成百分比 (done_ratio) 必須為 0-100 之間的整數")
        
        # 自訂欄位驗證
        if 'custom_fields' in data:
            custom_fields = data['custom_fields']
            if custom_fields is not None:  # 只有在不是 None 時才驗證
                if not isinstance(custom_fields, list):
                    errors.append("自訂欄位 (custom_fields) 必須為陣列格式")
                else:
                    for i, field in enumerate(custom_fields):
                        if not isinstance(field, dict):
                            errors.append(f"自訂欄位 [{i}] 必須為物件格式")
                        elif 'id' not in field:
                            errors.append(f"自訂欄位 [{i}] 缺少必要的 id 欄位")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    @classmethod
    def validate_project_data(cls, data: Dict[str, Any], is_update: bool = False) -> ValidationResult:
        """驗證專案資料"""
        errors = []
        warnings = []
        
        # 必要欄位檢查（建立時）
        if not is_update:
            if 'name' not in data or not data.get('name', '').strip():
                errors.append("專案名稱 (name) 為必填欄位")
            if 'identifier' not in data or not data.get('identifier', '').strip():
                errors.append("專案識別碼 (identifier) 為必填欄位")
        
        # 專案名稱驗證
        if 'name' in data:
            name = data['name']
            if not isinstance(name, str):
                errors.append("專案名稱必須為文字格式")
            elif len(name.strip()) == 0:
                errors.append("專案名稱不能為空")
            elif len(name) > cls.MAX_PROJECT_NAME_LENGTH:
                errors.append(f"專案名稱長度不能超過 {cls.MAX_PROJECT_NAME_LENGTH} 字元")
        
        # 專案識別碼驗證
        if 'identifier' in data:
            identifier = data['identifier']
            if not isinstance(identifier, str):
                errors.append("專案識別碼必須為文字格式")
            elif len(identifier.strip()) == 0:
                errors.append("專案識別碼不能為空")
            elif len(identifier) < cls.MIN_PROJECT_IDENTIFIER_LENGTH:
                errors.append(f"專案識別碼長度不能少於 {cls.MIN_PROJECT_IDENTIFIER_LENGTH} 字元")
            elif len(identifier) > cls.MAX_PROJECT_IDENTIFIER_LENGTH:
                errors.append(f"專案識別碼長度不能超過 {cls.MAX_PROJECT_IDENTIFIER_LENGTH} 字元")
            elif not cls.PROJECT_IDENTIFIER_PATTERN.match(identifier):
                errors.append("專案識別碼只能包含小寫字母、數字、破折號和底線")
            elif identifier.lower() != identifier:
                warnings.append("建議專案識別碼使用小寫字母")
        
        # 專案描述驗證
        if 'description' in data:
            description = data['description']
            if description is not None and not isinstance(description, str):
                errors.append("專案描述必須為文字格式")
        
        # 布林欄位驗證
        bool_fields = ['is_public', 'inherit_members']
        for field in bool_fields:
            if field in data:
                value = data[field]
                if not isinstance(value, bool):
                    errors.append(f"{field} 必須為布林值 (true/false)")
        
        # ID 欄位驗證
        if 'parent_id' in data:
            parent_id = data['parent_id']
            if parent_id is not None and (not isinstance(parent_id, int) or parent_id <= 0):
                errors.append("父專案 ID (parent_id) 必須為正整數")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    @classmethod
    def validate_query_params(cls, params: Dict[str, Any]) -> ValidationResult:
        """驗證查詢參數"""
        errors = []
        warnings = []
        
        # 分頁參數驗證
        if 'limit' in params:
            limit = params['limit']
            if not isinstance(limit, int) or limit <= 0:
                errors.append("分頁限制 (limit) 必須為正整數")
            elif limit > 100:
                warnings.append("建議分頁限制不超過 100 以確保效能")
        
        if 'offset' in params:
            offset = params['offset']
            if not isinstance(offset, int) or offset < 0:
                errors.append("分頁偏移 (offset) 必須為非負整數")
        
        # ID 篩選參數驗證
        id_fields = ['project_id', 'tracker_id', 'priority_id', 'assigned_to_id', 'author_id']
        for field in id_fields:
            if field in params:
                value = params[field]
                if value is not None and (not isinstance(value, int) or value <= 0):
                    errors.append(f"{field} 必須為正整數")
        
        # 特殊處理 status_id（支援 Redmine 的特殊值）
        if 'status_id' in params:
            status_id = params['status_id']
            if status_id is not None:
                # 允許正整數或 Redmine 特殊值 ('o' 為開放, 'c' 為關閉)
                if not (isinstance(status_id, int) and status_id > 0) and status_id not in ['o', 'c']:
                    errors.append("status_id 必須為正整數或 'o'(開放)/'c'(關閉)")
        
        # 日期篩選參數驗證
        date_fields = ['created_on', 'updated_on']
        for field in date_fields:
            if field in params:
                date_value = params[field]
                if date_value and not cls._is_valid_date_filter(date_value):
                    errors.append(f"{field} 日期格式不正確，支援格式：YYYY-MM-DD, >=YYYY-MM-DD, <=YYYY-MM-DD")
        
        # 排序參數驗證
        if 'sort' in params:
            sort_value = params['sort']
            if sort_value is not None and not isinstance(sort_value, str):
                errors.append("排序參數 (sort) 必須為文字格式")
            elif sort_value and not cls._is_valid_sort_field(sort_value):
                warnings.append(f"排序欄位 '{sort_value}' 可能不被支援")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    @classmethod
    def _is_valid_date_filter(cls, date_str: str) -> bool:
        """驗證日期篩選格式"""
        if not isinstance(date_str, str):
            return False
        
        return any(pattern.match(date_str) for pattern in cls.DATE_PATTERNS)
    
    @classmethod
    def _is_valid_sort_field(cls, sort_str: str) -> bool:
        """驗證排序欄位"""
        # 移除 :desc 或 :asc 後綴
        field = sort_str.split(':')[0]
        
        # 常見的排序欄位
        valid_fields = [
            'id', 'subject', 'status', 'priority', 'author', 'assigned_to',
            'created_on', 'updated_on', 'due_date', 'done_ratio', 'project'
        ]
        
        return field in valid_fields
    
    @classmethod
    def get_friendly_error_message(cls, error: Exception, context: str = "") -> str:
        """將技術錯誤轉換為友好的錯誤訊息"""
        error_msg = str(error).lower()
        
        # HTTP 錯誤訊息轉換
        if "401" in error_msg or "unauthorized" in error_msg:
            return "認證失敗：請檢查 API 金鑰是否正確"
        elif "403" in error_msg or "forbidden" in error_msg:
            return "權限不足：您沒有執行此操作的權限"
        elif "404" in error_msg or "not found" in error_msg:
            if "issue" in context.lower():
                return "找不到指定的議題，請確認議題 ID 是否正確"
            elif "project" in context.lower():
                return "找不到指定的專案，請確認專案 ID 或識別碼是否正確"
            else:
                return "找不到指定的資源"
        elif "422" in error_msg or "unprocessable" in error_msg:
            return "資料格式錯誤：請檢查輸入的資料是否符合要求"
        elif "500" in error_msg or "internal server error" in error_msg:
            return "伺服器內部錯誤：請稍後再試或聯絡系統管理員"
        elif "timeout" in error_msg:
            return "請求逾時：網路連線可能不穩定，請稍後再試"
        elif "connection" in error_msg or "connectionerror" in error_msg:
            return "連線失敗：請檢查網路連線和 Redmine 伺服器狀態"
        elif "httperror" in error_msg:
            return f"HTTP 錯誤：{str(error)}"
        
        # 其他常見錯誤
        if "json" in error_msg and "decode" in error_msg:
            return "回應格式錯誤：伺服器回應的資料格式不正確"
        
        # 預設錯誤訊息
        return f"操作失敗：{str(error)}"


def validate_and_clean_data(data: Dict[str, Any], validation_type: str) -> Dict[str, Any]:
    """驗證並清理資料"""
    if validation_type == "issue":
        result = RedmineValidator.validate_issue_data(data)
    elif validation_type == "project":
        result = RedmineValidator.validate_project_data(data)
    elif validation_type == "query":
        result = RedmineValidator.validate_query_params(data)
    else:
        raise ValueError(f"不支援的驗證類型：{validation_type}")
    
    if not result.is_valid:
        raise RedmineValidationError(
            f"資料驗證失敗：{'; '.join(result.errors)}",
            errors=result.errors
        )
    
    # 回傳清理後的資料（移除 None 值和空字串）
    cleaned_data = {}
    for key, value in data.items():
        if value is not None and value != "":
            cleaned_data[key] = value
    
    return cleaned_data