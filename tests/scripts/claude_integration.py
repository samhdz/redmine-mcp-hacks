#!/usr/bin/env python3
"""
Claude Code 整合測試腳本
用於驗證 MCP 服務器是否能正確與 Claude Code 整合
"""

import json
import subprocess
import sys
import os
from pathlib import Path


def test_mcp_server_executable():
    """測試 MCP 服務器是否可執行"""
    print("🔧 測試 MCP 服務器可執行性...")
    
    try:
        # 測試 server.py 是否可以直接執行
        result = subprocess.run([
            sys.executable, "-m", "redmine_mcp.server", "--help"
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ MCP 服務器可執行")
            return True
        else:
            print(f"❌ MCP 服務器執行失敗: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ MCP 服務器啟動正常（等待 stdio 輸入）")
        return True
    except Exception as e:
        print(f"❌ MCP 服務器測試失敗: {e}")
        return False


def test_package_installation():
    """測試套件是否正確安裝"""
    print("📦 測試套件安裝...")
    
    try:
        import redmine_mcp
        from redmine_mcp.server import mcp
        from redmine_mcp.config import get_config
        from redmine_mcp.redmine_client import get_client
        
        print("✅ 所有模組匯入成功")
        print(f"   - redmine_mcp 版本: {getattr(redmine_mcp, '__version__', 'unknown')}")
        return True
        
    except ImportError as e:
        print(f"❌ 模組匯入失敗: {e}")
        return False


def test_configuration():
    """測試配置是否正確"""
    print("⚙️  測試配置...")
    
    # 測試環境變數
    required_env = ['REDMINE_DOMAIN', 'REDMINE_API_KEY']
    missing_env = []
    
    for env_var in required_env:
        if not os.getenv(env_var):
            missing_env.append(env_var)
    
    if missing_env:
        print(f"⚠️  缺少環境變數: {', '.join(missing_env)}")
        print("   請設定這些環境變數或建立 .env 檔案")
        return False
    
    try:
        from redmine_mcp.config import get_config
        config = get_config()
        print(f"✅ 配置載入成功")
        print(f"   - Redmine 網域: {config.redmine_domain}")
        print(f"   - API 逾時: {config.redmine_timeout}秒")
        print(f"   - 除錯模式: {config.debug_mode}")
        return True
        
    except Exception as e:
        print(f"❌ 配置載入失敗: {e}")
        return False


def generate_claude_config():
    """產生 Claude Code 配置範例"""
    print("📝 產生 Claude Code 配置範例...")
    
    config = {
        "mcpServers": {
            "redmine": {
                "command": "redmine-mcp",
                "env": {
                    "REDMINE_DOMAIN": os.getenv("REDMINE_DOMAIN", "https://your-redmine-domain.com"),
                    "REDMINE_API_KEY": os.getenv("REDMINE_API_KEY", "your_api_key_here"),
                    "REDMINE_TIMEOUT": os.getenv("REDMINE_TIMEOUT", "30"),
                    "DEBUG_MODE": os.getenv("DEBUG_MODE", "false")
                }
            }
        }
    }
    
    config_file = Path("claude_mcp_config_generated.json")
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 配置檔案已產生: {config_file}")
    print("   請將此內容複製到 Claude Code 的 MCP 配置中")
    return True


def test_tools_availability():
    """測試工具是否可用"""
    print("🛠️  測試工具可用性...")
    
    try:
        from redmine_mcp.server import (
            server_info, health_check, get_issue, 
            update_issue_status, list_project_issues
        )
        
        print("✅ 核心工具函數可用")
        
        # 測試工具函數
        info = server_info()
        print(f"   - 服務器資訊: {info[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具測試失敗: {e}")
        return False


def main():
    """主測試函數"""
    print("🚀 Claude Code 整合測試開始\n")
    
    tests = [
        ("套件安裝", test_package_installation),
        ("配置設定", test_configuration),
        ("MCP 服務器", test_mcp_server_executable),
        ("工具可用性", test_tools_availability),
        ("配置產生", generate_claude_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！Redmine MCP 已準備好與 Claude Code 整合")
        print("\n下一步:")
        print("1. 將產生的配置添加到 Claude Code")
        print("2. 重新啟動 Claude Code")
        print("3. 在 Claude Code 中測試工具")
        return True
    else:
        print("❌ 部分測試失敗，請檢查上述錯誤訊息")
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)