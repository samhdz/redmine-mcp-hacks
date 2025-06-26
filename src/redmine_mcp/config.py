"""
配置管理模組
負責載入和驗證環境變數配置
"""

import os
from typing import Optional
from dotenv import load_dotenv


class RedmineConfig:
    """Redmine MCP 服務器配置管理"""
    
    def __init__(self):
        # 載入環境變數
        load_dotenv()
        
        # 必要配置
        self.redmine_domain = self._get_required_env("REDMINE_DOMAIN")
        self.redmine_api_key = self._get_required_env("REDMINE_API_KEY")
        
        # 可選配置 - 使用專屬前綴避免與其他專案環境變數衝突
        self.redmine_timeout = int(os.getenv("REDMINE_MCP_TIMEOUT") or os.getenv("REDMINE_TIMEOUT") or "30")
        
        # 優先使用專屬環境變數，如果沒有則使用通用環境變數，最後使用預設值
        mcp_log_level = os.getenv("REDMINE_MCP_LOG_LEVEL")
        fallback_log_level = os.getenv("LOG_LEVEL")
        self.log_level = (mcp_log_level or fallback_log_level or "INFO").upper()
        self.debug_mode = self.log_level == "DEBUG"
        
        self._validate_config()
    
    def _get_required_env(self, key: str) -> str:
        """取得必要的環境變數，如果不存在則拋出錯誤"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"必要的環境變數 {key} 未設定")
        return value
    
    def _validate_config(self) -> None:
        """驗證配置的有效性"""
        # 驗證 domain 格式
        if not self.redmine_domain.startswith(('http://', 'https://')):
            raise ValueError("REDMINE_DOMAIN 必須以 http:// 或 https:// 開頭")
        
        # 移除末尾的斜線
        self.redmine_domain = self.redmine_domain.rstrip('/')
        
        # 驗證 API key 不為空
        if not self.redmine_api_key.strip():
            raise ValueError("REDMINE_API_KEY 不能為空")
        
        # 驗證 timeout 值
        if self.redmine_timeout <= 0:
            raise ValueError("REDMINE_TIMEOUT 必須大於 0")
        
        # 驗證 log_level 值
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_levels:
            raise ValueError(f"LOG_LEVEL 必須是以下值之一: {', '.join(valid_levels)}")
    
    @property
    def api_headers(self) -> dict[str, str]:
        """回傳 API 請求所需的標頭"""
        return {
            'X-Redmine-API-Key': self.redmine_api_key,
            'Content-Type': 'application/json'
        }
    
    def __repr__(self) -> str:
        """除錯用的字串表示，隱藏敏感資訊"""
        return f"RedmineConfig(domain='{self.redmine_domain}', timeout={self.redmine_timeout}, log_level='{self.log_level}', debug={self.debug_mode})"


# 全域配置實例
_config: Optional[RedmineConfig] = None


def get_config() -> RedmineConfig:
    """取得全域配置實例（單例模式）"""
    global _config
    if _config is None:
        _config = RedmineConfig()
    return _config


def reload_config() -> RedmineConfig:
    """重新載入配置（主要用於測試）"""
    global _config
    _config = None
    return get_config()