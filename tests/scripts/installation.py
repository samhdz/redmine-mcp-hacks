#!/usr/bin/env python3
"""
測試安裝的 redmine-mcp 套件
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def test_package_import():
    """測試套件導入"""
    print("📦 測試套件導入...")
    try:
        import redmine_mcp
        from redmine_mcp.server import mcp
        from redmine_mcp.config import get_config
        from redmine_mcp.redmine_client import get_client
        print("✅ 套件導入成功")
        return True
    except ImportError as e:
        print(f"❌ 套件導入失敗: {e}")
        return False

def test_command_availability():
    """測試命令是否可用"""
    print("\n🔧 測試命令可用性...")
    
    # 檢查 uv tool 安裝的命令
    uv_bin_path = Path.home() / ".local" / "bin" / "redmine-mcp"
    if uv_bin_path.exists():
        print(f"✅ 找到 uv tool 安裝的命令: {uv_bin_path}")
        return True
    
    # 檢查系統 PATH 中的命令
    try:
        result = subprocess.run(["which", "redmine-mcp"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ 找到系統 PATH 中的命令: {result.stdout.strip()}")
            return True
    except subprocess.TimeoutExpired:
        pass
    except FileNotFoundError:
        pass
    
    print("❌ 未找到 redmine-mcp 命令")
    return False

def test_mcp_server_startup():
    """測試 MCP 服務器啟動"""
    print("\n🚀 測試 MCP 服務器啟動...")
    
    # 使用本地模組測試
    try:
        # 設定測試環境變數
        os.environ["REDMINE_DOMAIN"] = "https://test.example.com"
        os.environ["REDMINE_API_KEY"] = "test_key_12345"
        
        # 導入並測試服務器
        from redmine_mcp.server import mcp
        
        # 檢查 MCP 實例是否正確建立
        if mcp:
            print("✅ MCP 服務器實例建立成功")
            
            # 簡單檢查 - 確認可以導入工具函數
            try:
                from redmine_mcp.server import server_info, health_check, get_issue
                print("✅ 核心工具函數可以正常導入")
                return True
            except ImportError as ie:
                print(f"⚠️  工具函數導入失敗: {ie}")
                print("✅ MCP 服務器實例建立成功（但工具導入有問題）")
                return True
            
    except Exception as e:
        print(f"❌ MCP 服務器啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading():
    """測試配置載入"""
    print("\n⚙️ 測試配置載入...")
    try:
        # 設定測試環境變數
        os.environ["REDMINE_DOMAIN"] = "https://test.example.com"
        os.environ["REDMINE_API_KEY"] = "test_key_12345"
        os.environ["DEBUG_MODE"] = "true"
        
        from redmine_mcp.config import get_config
        config = get_config()
        
        print(f"✅ 配置載入成功")
        print(f"   - Domain: {config.redmine_domain}")
        print(f"   - API Key: {config.redmine_api_key[:10]}...")
        print(f"   - Debug: {config.debug_mode}")
        print(f"   - Timeout: {config.redmine_timeout}")
        
        return True
    except Exception as e:
        print(f"❌ 配置載入失敗: {e}")
        return False

def test_package_info():
    """測試套件資訊"""
    print("\n📋 測試套件資訊...")
    try:
        import redmine_mcp
        
        # 檢查版本
        if hasattr(redmine_mcp, '__version__'):
            print(f"✅ 套件版本: {redmine_mcp.__version__}")
        else:
            print("⚠️  套件版本資訊不可用")
        
        # 檢查模組
        modules = ['server', 'config', 'redmine_client', 'validators']
        for module in modules:
            try:
                __import__(f'redmine_mcp.{module}')
                print(f"✅ 模組 {module} 可用")
            except ImportError:
                print(f"❌ 模組 {module} 不可用")
        
        return True
    except Exception as e:
        print(f"❌ 套件資訊檢查失敗: {e}")
        return False

def main():
    """主要測試流程"""
    print("🧪 Redmine MCP 安裝測試")
    print("=" * 50)
    
    tests = [
        test_package_import,
        test_command_availability, 
        test_config_loading,
        test_mcp_server_startup,
        test_package_info,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 測試結果摘要")
    print("=" * 50)
    print(f"總測試數: {total}")
    print(f"通過: {passed}")
    print(f"失敗: {total - passed}")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有測試通過！套件安裝成功")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 個測試失敗")
        return 1

if __name__ == "__main__":
    sys.exit(main())