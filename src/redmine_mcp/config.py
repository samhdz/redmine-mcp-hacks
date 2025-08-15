"""
Configuration management module
Responsible for loading and validating environment variable configuration
"""

import os
from typing import Optional
from dotenv import load_dotenv


class RedmineConfig:
    """Redmine MCP server configuration management"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Required configuration
        self.redmine_domain = self._get_required_env("REDMINE_DOMAIN")
        self.redmine_api_key = self._get_required_env("REDMINE_API_KEY")
        
        # Optional configuration - use project-specific prefix to avoid conflicts with other projects
        self.redmine_timeout = int(os.getenv("REDMINE_MCP_TIMEOUT") or os.getenv("REDMINE_TIMEOUT") or "30")
        
        # Log level management strategy:
        # 1. Prefer REDMINE_MCP_LOG_LEVEL (project-specific variable)
        # 2. Then use LOG_LEVEL (backward compatibility)
        # 3. If neither is set, default to INFO
        # 4. FASTMCP_LOG_LEVEL always follows the final log level value
        redmine_log_level = os.getenv("REDMINE_MCP_LOG_LEVEL")
        if redmine_log_level:
            self.log_level = redmine_log_level.upper()
        else:
            # Backward compatibility: if no project-specific variable, check legacy LOG_LEVEL
            legacy_log_level = os.getenv("LOG_LEVEL")
            if legacy_log_level:
                self.log_level = legacy_log_level.upper()
            else:
                self.log_level = "INFO"
        
        # FastMCP log level control - always set to the final log level value
        # Regardless of whether FASTMCP_LOG_LEVEL is set, it will be overwritten
        os.environ["FASTMCP_LOG_LEVEL"] = self.log_level
        self.fastmcp_log_level = self.log_level
        
        self.effective_log_level = self.log_level
        self.debug_mode = self.effective_log_level == "DEBUG"
        
        self._validate_config()
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable, raise error if not set"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _validate_config(self) -> None:
        """Validate configuration values"""
        # Validate domain format
        if not self.redmine_domain.startswith(('http://', 'https://')):
            raise ValueError("REDMINE_DOMAIN must start with http:// or https://")
        
        # Remove trailing slash
        self.redmine_domain = self.redmine_domain.rstrip('/')
        
        # Validate API key is not empty
        if not self.redmine_api_key.strip():
            raise ValueError("REDMINE_API_KEY cannot be empty")
        
        # Validate timeout value
        if self.redmine_timeout <= 0:
            raise ValueError("REDMINE_TIMEOUT must be greater than 0")
        
        # Validate log_level value
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)} (current: {self.log_level})")
    
    @property
    def api_headers(self) -> dict[str, str]:
        """Return headers required for API requests"""
        return {
            'X-Redmine-API-Key': self.redmine_api_key,
            'Content-Type': 'application/json'
        }
    
    def __repr__(self) -> str:
        """Debug string representation, hides sensitive info"""
        return f"RedmineConfig(domain='{self.redmine_domain}', timeout={self.redmine_timeout}, log_level='{self.log_level}', fastmcp_log_level='{self.fastmcp_log_level}', debug={self.debug_mode})"


# Global config instance
_config: Optional[RedmineConfig] = None


def get_config() -> RedmineConfig:
    """Get global config instance (singleton pattern)"""
    global _config
    if _config is None:
        _config = RedmineConfig()
    return _config


def reload_config() -> RedmineConfig:
    """Reload configuration (mainly for testing)"""
    global _config
    _config = None
    return get_config()
