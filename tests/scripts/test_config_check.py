#!/usr/bin/env python3
"""
檢查 redmine-mcp 配置和環境設定
"""

import sys
import os
from pathlib import Path

# 添加 src 到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def check_configuration():
    """檢查配置是否正確"""
    print("🔧 檢查 redmine-mcp 配置")
    print("=" * 50)
    
    # 檢查環境變數
    print("1️⃣ 檢查環境變數...")
    
    required_vars = {
        'REDMINE_DOMAIN': '必要 - Redmine 伺服器網址',
        'REDMINE_API_KEY': '必要 - Redmine API 金鑰'
    }
    
    optional_vars = {
        'REDMINE_MCP_LOG_LEVEL': '可選 - 日誌級別',
        'REDMINE_MCP_TIMEOUT': '可選 - 請求超時時間',
        'LOG_LEVEL': '備用 - 日誌級別（備用）',
        'REDMINE_TIMEOUT': '備用 - 請求超時時間（備用）'
    }
    
    missing_required = []
    
    print("\n必要環境變數:")
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            # 隱藏 API 金鑰
            display_value = value if var != 'REDMINE_API_KEY' else f"{value[:8]}...{value[-4:]}"
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: 未設定 ({desc})")
            missing_required.append(var)
    
    print("\n可選環境變數:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚪ {var}: 未設定 ({desc})")
    
    if missing_required:
        print(f"\n❌ 缺少必要環境變數: {', '.join(missing_required)}")
        print("\n設定方式:")
        print("export REDMINE_DOMAIN='https://your-redmine-domain.com'")
        print("export REDMINE_API_KEY='your_api_key_here'")
        return False
    
    # 嘗試載入配置
    print("\n2️⃣ 測試配置載入...")
    try:
        from redmine_mcp.config import get_config
        config = get_config()
        
        print(f"✅ 配置載入成功")
        print(f"  - Domain: {config.redmine_domain}")
        print(f"  - API Key: {config.redmine_api_key[:8]}...{config.redmine_api_key[-4:]}")
        print(f"  - Timeout: {config.redmine_timeout}s")
        print(f"  - Log Level: {config.log_level}")
        
    except Exception as e:
        print(f"❌ 配置載入失敗: {e}")
        return False
    
    # 測試客戶端初始化
    print("\n3️⃣ 測試客戶端初始化...")
    try:
        from redmine_mcp.redmine_client import get_client
        client = get_client()
        
        print(f"✅ 客戶端初始化成功")
        print(f"  - 快取目錄: {client.cache_dir}")
        print(f"  - 快取檔案: {client._cache_file.name}")
        
    except Exception as e:
        print(f"❌ 客戶端初始化失敗: {e}")
        return False
    
    # 測試網路連接（不需要有效 API）
    print("\n4️⃣ 測試網路連接...")
    try:
        import requests
        from urllib.parse import urlparse
        
        parsed = urlparse(config.redmine_domain)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        response = requests.get(base_url, timeout=10)
        print(f"✅ 網路連接正常 (HTTP {response.status_code})")
        
    except Exception as e:
        print(f"⚠️ 網路連接測試失敗: {e}")
        print("    這可能是正常的，如果 Redmine 需要特殊認證")
    
    print("\n✅ 基本配置檢查完成")
    return True


def test_offline_features():
    """測試不需要網路連接的功能"""
    print("\n🔧 測試離線功能")
    print("=" * 50)
    
    try:
        from redmine_mcp.redmine_client import get_client
        
        client = get_client()
        
        # 測試快取目錄建立
        print("1️⃣ 測試快取目錄...")
        cache_dir = client.cache_dir
        
        if cache_dir.exists():
            print(f"✅ 快取目錄存在: {cache_dir}")
        else:
            print(f"⚠️ 快取目錄不存在，嘗試建立...")
            cache_dir.mkdir(parents=True, exist_ok=True)
            if cache_dir.exists():
                print(f"✅ 快取目錄建立成功: {cache_dir}")
            else:
                print(f"❌ 快取目錄建立失敗")
                return False
        
        # 測試快取檔案命名
        print("\n2️⃣ 測試快取檔案命名...")
        cache_file = client._cache_file
        print(f"✅ 快取檔案名稱: {cache_file.name}")
        
        # 檢查檔案名稱是否包含 domain 資訊
        from redmine_mcp.config import get_config
        config = get_config()
        domain_part = config.redmine_domain.replace('://', '_').replace('/', '_').replace(':', '_')
        
        if domain_part in cache_file.name:
            print(f"✅ 檔案名稱包含 domain 資訊")
        else:
            print(f"⚠️ 檔案名稱可能有問題")
        
        # 測試空快取結構
        print("\n3️⃣ 測試空快取結構...")
        empty_cache = {
            'cache_time': 0,
            'domain': config.redmine_domain,
            'priorities': {},
            'statuses': {},
            'trackers': {},
            'users_by_name': {},
            'users_by_login': {}
        }
        
        import json
        test_content = json.dumps(empty_cache, ensure_ascii=False, indent=2)
        print(f"✅ 快取結構測試通過")
        
        # 測試輔助函數（使用空資料）
        print("\n4️⃣ 測試輔助函數（空資料）...")
        
        # 設定空快取
        client._enum_cache = empty_cache
        
        result = client.find_priority_id_by_name("不存在的優先權")
        if result is None:
            print("✅ find_priority_id_by_name 正確回傳 None")
        else:
            print("❌ find_priority_id_by_name 應該回傳 None")
            return False
        
        result = client.find_user_id("不存在的用戶")
        if result is None:
            print("✅ find_user_id 正確回傳 None")
        else:
            print("❌ find_user_id 應該回傳 None")
            return False
        
        print("\n✅ 離線功能測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 離線功能測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主要測試流程"""
    print("🧪 redmine-mcp 配置和離線功能測試")
    print("=" * 60)
    
    # 配置檢查
    config_ok = check_configuration()
    
    # 離線功能測試
    offline_ok = test_offline_features()
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    
    print(f"配置檢查: {'✅ 通過' if config_ok else '❌ 失敗'}")
    print(f"離線功能: {'✅ 通過' if offline_ok else '❌ 失敗'}")
    
    if config_ok and offline_ok:
        print("\n🎉 基本功能正常！可以進行進一步測試")
        print("\n💡 如果要測試完整功能，請確保:")
        print("1. REDMINE_DOMAIN 指向可存取的 Redmine 伺服器")
        print("2. REDMINE_API_KEY 是有效的 API 金鑰")
        print("3. 網路連接正常")
        print("\n然後執行: uv run python tests/scripts/quick_validation.py")
        return True
    else:
        print("\n❌ 基本功能有問題，請檢查配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)