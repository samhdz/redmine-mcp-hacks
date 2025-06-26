# issue_redmine_mcp_fix: 修復 redmine-mcp 無法正確運行的問題

## 問題描述
redmine-mcp 專案在執行時出現 log_level 格式錯誤，無法正確啟動 MCP 服務器。

## 錯誤訊息
```
log_level 值需要為 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'
```

## 問題分析
1. **環境變數錯誤**: `.env` 檔案使用 `DEBUG_MODE=true` 而非 `LOG_LEVEL=DEBUG`
2. **配置檔案不一致**: `claude_mcp_config.json` 也使用了 `DEBUG_MODE` 而非 `LOG_LEVEL`
3. **生成配置錯誤**: 自動生成的配置檔案延續了錯誤的設定

## 解決方案

### 修正的檔案
1. `.env`: `DEBUG_MODE=true` → `LOG_LEVEL=DEBUG`
2. `claude_mcp_config.json`: `"DEBUG_MODE": "false"` → `"LOG_LEVEL": "INFO"`
3. `claude_mcp_config_generated.json`: `"DEBUG_MODE": "true"` → `"LOG_LEVEL": "DEBUG"`

### 修正後的配置格式
```bash
# .env
LOG_LEVEL=DEBUG
```

```json
// claude_mcp_config.json
{
  "mcpServers": {
    "redmine": {
      "command": "redmine-mcp",
      "env": {
        "REDMINE_DOMAIN": "https://your-redmine-domain.com",
        "REDMINE_API_KEY": "your_api_key_here",
        "REDMINE_TIMEOUT": "30",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 測試結果
執行 `uv run python test_claude_integration.py` 後：
- ✅ 所有測試通過 (5/5)
- ✅ MCP 服務器可正常執行
- ✅ 工具函數可用
- ✅ 配置載入成功

## 跨專案協調
- **任務 ID**: redmine_mcp_fix
- **處理會話**: session_2
- **狀態**: completed
- **完成時間**: 2025-06-25T13:50:00Z

## 建立的協調檔案
1. `.claude/session_state.json` - 狀態追蹤檔案
2. `.claude/coordination_guide.md` - 協調指南
3. `.claude/cross_project_update.json` - 跨專案更新記錄

## 下一步
1. 可將修正後的配置添加到 Claude Code
2. 重新啟動 Claude Code 
3. 在 Claude Code 中測試 redmine-mcp 工具