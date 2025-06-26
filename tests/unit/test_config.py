"""
配置管理模組測試
"""

import os
import pytest
from unittest.mock import patch
from redmine_mcp.config import RedmineConfig, get_config, reload_config


class TestRedmineConfig:
    """RedmineConfig 類別測試"""
    
    def test_config_with_valid_env(self):
        """測試有效環境變數的配置"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key_123',
            'REDMINE_TIMEOUT': '45',
            'DEBUG_MODE': 'true'
        }):
            config = RedmineConfig()
            
            assert config.redmine_domain == 'https://test.redmine.com'
            assert config.redmine_api_key == 'test_api_key_123'
            assert config.redmine_timeout == 45
            assert config.debug_mode is True
    
    def test_config_missing_required_env(self):
        """測試缺少必要環境變數的情況"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="必要的環境變數 REDMINE_DOMAIN 未設定"):
                RedmineConfig()
    
    def test_config_invalid_domain(self):
        """測試無效的 domain 格式"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'invalid-domain',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            with pytest.raises(ValueError, match="REDMINE_DOMAIN 必須以 http:// 或 https:// 開頭"):
                RedmineConfig()
    
    def test_config_domain_trailing_slash_removal(self):
        """測試移除 domain 末尾斜線"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com/',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            config = RedmineConfig()
            assert config.redmine_domain == 'https://test.redmine.com'
    
    def test_config_default_values(self):
        """測試預設值"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            config = RedmineConfig()
            
            assert config.redmine_timeout == 30  # 預設值
            assert config.debug_mode is False   # 預設值
    
    def test_api_headers(self):
        """測試 API 標頭生成"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key_123'
        }):
            config = RedmineConfig()
            headers = config.api_headers
            
            assert headers['X-Redmine-API-Key'] == 'test_api_key_123'
            assert headers['Content-Type'] == 'application/json'
    
    def test_config_repr(self):
        """測試字串表示不包含敏感資訊"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'secret_api_key'
        }):
            config = RedmineConfig()
            repr_str = repr(config)
            
            assert 'https://test.redmine.com' in repr_str
            assert 'secret_api_key' not in repr_str  # 敏感資訊應該被隱藏


class TestConfigSingleton:
    """測試配置單例模式"""
    
    def test_get_config_singleton(self):
        """測試 get_config 回傳同一個實例"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            config1 = get_config()
            config2 = get_config()
            
            assert config1 is config2
    
    def test_reload_config(self):
        """測試 reload_config 建立新實例"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            config1 = get_config()
            config2 = reload_config()
            
            # 雖然是新實例，但內容應該相同
            assert config1 is not config2
            assert config1.redmine_domain == config2.redmine_domain