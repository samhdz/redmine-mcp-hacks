#!/usr/bin/env python3
"""
測試 Claude Code MCP 設定
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

def test_mcp_config_generation():
    """測試 MCP 配置檔案生成"""
    print("📋 測試 MCP 配置檔案生成...")
    
    try:
        # 創建測試配置
        config = {
            "mcpServers": {
                "redmine": {
                    "command": "redmine-mcp",
                    "env": {
                        "REDMINE_DOMAIN": "https://demo.redmine.org",
                        "REDMINE_API_KEY": "test_api_key_12345",
                        "REDMINE_TIMEOUT": "30",
                        "DEBUG_MODE": "false"
                    }
                }
            }
        }
        
        # 寫入臨時檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            temp_path = f.name
        
        # 驗證 JSON 格式
        with open(temp_path, 'r') as f:
            loaded_config = json.load(f)
        
        print("✅ MCP 配置檔案格式正確")
        print(f"   配置包含 {len(loaded_config['mcpServers'])} 個 MCP 服務器")
        print(f"   Redmine 服務器配置: {loaded_config['mcpServers']['redmine']['command']}")
        
        # 清理臨時檔案
        os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"❌ MCP 配置檔案生成失敗: {e}")
        return False

def test_command_execution():
    """測試命令執行"""
    print("\n🔧 測試命令執行...")
    
    try:
        # 檢查 redmine-mcp 命令是否存在
        uv_bin_path = Path.home() / ".local" / "bin" / "redmine-mcp"
        
        if not uv_bin_path.exists():
            print("❌ redmine-mcp 命令不存在")
            return False
        
        print(f"✅ 找到命令: {uv_bin_path}")
        
        # 測試命令可執行性（不實際執行，因為會等待 stdio）
        if os.access(uv_bin_path, os.X_OK):
            print("✅ 命令具有執行權限")
            return True
        else:
            print("❌ 命令沒有執行權限")
            return False
            
    except Exception as e:
        print(f"❌ 命令執行測試失敗: {e}")
        return False

def generate_setup_instructions():
    """生成設定說明"""
    print("\n📖 生成 Claude Code 設定說明...")
    
    try:
        # 找到安裝路徑
        uv_bin_path = Path.home() / ".local" / "bin" / "redmine-mcp"
        
        instructions = f"""
Claude Code MCP 設定說明
========================

1. 確認安裝
   命令位置: {uv_bin_path}
   狀態: {'✅ 已安裝' if uv_bin_path.exists() else '❌ 未安裝'}

2. 手動添加到 Claude Code
   執行以下命令將 Redmine MCP 添加到 Claude Code：

   ```bash
   claude mcp add redmine "{uv_bin_path}" \\
     -e REDMINE_DOMAIN="https://your-redmine-domain.com" \\
     -e REDMINE_API_KEY="your_api_key_here"
   ```

3. 或者手動編輯 MCP 配置檔案
   
   配置檔案位置:
   - macOS/Linux: ~/.config/claude-code/mcp_servers.json
   - Windows: %APPDATA%\\claude-code\\mcp_servers.json
   
   配置內容:
   ```json
   {{
     "mcpServers": {{
       "redmine": {{
         "command": "{uv_bin_path}",
         "env": {{
           "REDMINE_DOMAIN": "https://your-redmine-domain.com",
           "REDMINE_API_KEY": "your_api_key_here",
           "REDMINE_TIMEOUT": "30",
           "DEBUG_MODE": "false"
         }}
       }}
     }}
   }}
   ```

4. 重啟 Claude Code
   設定完成後，重新啟動 Claude Code 以載入 MCP 服務器。

5. 驗證設定
   在 Claude Code 中輸入: "請執行健康檢查"
   如果看到 Redmine 連線狀態回應，表示設定成功。
"""
        
        print(instructions)
        
        # 寫入檔案
        setup_file = Path("CLAUDE_SETUP.md")
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"✅ 設定說明已儲存到: {setup_file}")
        return True
        
    except Exception as e:
        print(f"❌ 設定說明生成失敗: {e}")
        return False

def main():
    """主要測試流程"""
    print("🔗 Claude Code MCP 設定測試")
    print("=" * 50)
    
    tests = [
        test_mcp_config_generation,
        test_command_execution,
        generate_setup_instructions,
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
        print("\n🎉 Claude Code 設定測試通過！")
        print("💡 請參考 CLAUDE_SETUP.md 完成 Claude Code 整合設定")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 個測試失敗")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())