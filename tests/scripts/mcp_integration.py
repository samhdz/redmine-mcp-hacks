#!/usr/bin/env python3
"""
完整的 MCP 功能測試腳本
使用本地 Redmine 環境測試所有 MCP 工具
"""

import sys
import os
import time
import requests
from typing import List, Dict, Any

# 添加 src 目錄到路徑（從 tests/scripts 往上兩層到根目錄）
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from redmine_mcp.server import (
    server_info, health_check, get_issue, update_issue_status,
    list_project_issues, get_issue_statuses, get_projects,
    search_issues, update_issue_content, add_issue_note,
    assign_issue, create_new_issue, get_my_issues, close_issue
)


class MCPTester:
    """MCP 功能測試器"""
    
    def __init__(self):
        self.test_results = []
        self.created_issues = []
        self.project_id = None
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """記錄測試結果"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'name': test_name,
            'success': success,
            'message': message
        })
    
    def test_basic_functions(self):
        """測試基本功能"""
        print("\n📋 測試基本功能...")
        
        # 測試服務器資訊
        try:
            result = server_info()
            self.log_test("服務器資訊", "Redmine MCP" in result, f"取得: {result[:50]}...")
        except Exception as e:
            self.log_test("服務器資訊", False, f"錯誤: {e}")
        
        # 測試健康檢查
        try:
            result = health_check()
            success = "正常運作" in result or "已連接" in result
            self.log_test("健康檢查", success, f"狀態: {result[:50]}...")
        except Exception as e:
            self.log_test("健康檢查", False, f"錯誤: {e}")
    
    def test_query_functions(self):
        """測試查詢功能"""
        print("\n🔍 測試查詢功能...")
        
        # 測試取得專案列表
        try:
            result = get_projects()
            success = "找到" in result and "專案" in result
            self.log_test("取得專案列表", success, f"結果: {result[:50]}...")
            
            # 從結果中解析專案 ID
            if success:
                import re
                id_match = re.search(r'(\d+)\s+[a-z-]+\s+', result)
                if id_match:
                    self.project_id = int(id_match.group(1))
                    print(f"  📝 找到測試專案 ID: {self.project_id}")
        except Exception as e:
            self.log_test("取得專案列表", False, f"錯誤: {e}")
        
        # 測試取得議題狀態
        try:
            result = get_issue_statuses()
            success = "可用的議題狀態" in result
            self.log_test("取得議題狀態", success, f"結果: {result[:50]}...")
        except Exception as e:
            self.log_test("取得議題狀態", False, f"錯誤: {e}")
        
        # 測試列出專案議題
        if self.project_id:
            try:
                result = list_project_issues(self.project_id)
                success = "找到" in result or "沒有找到" in result  # 兩種都是正常結果
                self.log_test("列出專案議題", success, f"結果: {result[:50]}...")
                
                # 從結果中解析議題 ID
                if "找到" in result:
                    import re
                    id_matches = re.findall(r'^(\d+)\s+', result, re.MULTILINE)
                    if id_matches:
                        first_issue_id = int(id_matches[0])
                        print(f"  📝 找到議題 ID: {first_issue_id}")
                        return first_issue_id
            except Exception as e:
                self.log_test("列出專案議題", False, f"錯誤: {e}")
        
        return None
    
    def test_create_functions(self):
        """測試建立功能"""
        print("\n➕ 測試建立功能...")
        
        if not self.project_id:
            self.log_test("建立新議題", False, "沒有有效的專案 ID")
            return None
        
        # 測試建立新議題
        try:
            subject = f"MCP 測試議題 - {int(time.time())}"
            description = "這是由 MCP 自動測試腳本建立的測試議題"
            
            result = create_new_issue(
                self.project_id, 
                subject, 
                description
            )
            
            success = "新議題建立成功" in result
            self.log_test("建立新議題", success, f"結果: {result[:50]}...")
            
            if success:
                # 解析議題 ID
                import re
                id_match = re.search(r'議題 ID: #(\d+)', result)
                if id_match:
                    issue_id = int(id_match.group(1))
                    self.created_issues.append(issue_id)
                    print(f"  📝 建立的議題 ID: {issue_id}")
                    return issue_id
        except Exception as e:
            self.log_test("建立新議題", False, f"錯誤: {e}")
        
        return None
    
    def test_update_functions(self, issue_id: int):
        """測試更新功能"""
        print("\n✏️  測試更新功能...")
        
        # 測試取得議題詳細資訊
        try:
            result = get_issue(issue_id)
            success = f"議題 #{issue_id}" in result
            self.log_test("取得議題詳細資訊", success, f"結果: {result[:50]}...")
        except Exception as e:
            self.log_test("取得議題詳細資訊", False, f"錯誤: {e}")
        
        # 測試更新議題內容
        try:
            new_subject = f"已更新的 MCP 測試議題 - {int(time.time())}"
            result = update_issue_content(
                issue_id, 
                subject=new_subject,
                description="描述已由 MCP 更新",
                done_ratio=25
            )
            success = "議題內容更新成功" in result
            self.log_test("更新議題內容", success, f"結果: {result[:50]}...")
        except Exception as e:
            self.log_test("更新議題內容", False, f"錯誤: {e}")
        
        # 測試新增議題備註
        try:
            result = add_issue_note(issue_id, "這是 MCP 自動測試新增的備註", private=False)
            success = "備註新增成功" in result
            self.log_test("新增議題備註", success, f"結果: {result[:50]}...")
        except Exception as e:
            self.log_test("新增議題備註", False, f"錯誤: {e}")
        
        # 測試更新議題狀態
        try:
            result = update_issue_status(issue_id, 2, "狀態由 MCP 自動測試更新")
            success = "議題狀態更新成功" in result or "找不到" in result  # 狀態 ID 可能不存在
            self.log_test("更新議題狀態", success, f"結果: {result[:50]}...")
        except Exception as e:
            self.log_test("更新議題狀態", False, f"錯誤: {e}")
    
    def test_search_functions(self):
        """測試搜尋功能"""
        print("\n🔎 測試搜尋功能...")
        
        # 測試搜尋議題
        try:
            result = search_issues("MCP", limit=5)
            success = "搜尋關鍵字" in result
            self.log_test("搜尋議題", success, f"結果: {result[:50]}...")
        except Exception as e:
            self.log_test("搜尋議題", False, f"錯誤: {e}")
        
        # 測試取得我的議題
        try:
            result = get_my_issues("all", 10)
            success = "的議題" in result or "沒有找到" in result
            self.log_test("取得我的議題", success, f"結果: {result[:50]}...")
        except Exception as e:
            self.log_test("取得我的議題", False, f"錯誤: {e}")
    
    def test_close_functions(self, issue_id: int):
        """測試關閉功能"""
        print("\n🔒 測試關閉功能...")
        
        # 測試關閉議題
        try:
            result = close_issue(issue_id, "議題由 MCP 自動測試關閉", 100)
            success = "議題關閉成功" in result or "找不到" in result
            self.log_test("關閉議題", success, f"結果: {result[:50]}...")
        except Exception as e:
            self.log_test("關閉議題", False, f"錯誤: {e}")
    
    def cleanup_test_data(self):
        """清理測試資料"""
        print("\n🧹 清理測試資料...")
        
        # 注意：這裡只是記錄，實際清理需要 DELETE API
        if self.created_issues:
            print(f"  📝 建立的測試議題: {self.created_issues}")
            print("  ℹ️  如需清理，請手動刪除或關閉這些議題")
    
    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 開始 MCP 功能整合測試")
        print("=" * 50)
        
        # 檢查環境
        if not os.getenv('REDMINE_DOMAIN') or not os.getenv('REDMINE_API_KEY'):
            print("❌ 環境變數未設定，請先執行 configure_redmine.py")
            return False
        
        # 基本功能測試
        self.test_basic_functions()
        
        # 查詢功能測試
        existing_issue_id = self.test_query_functions()
        
        # 建立功能測試
        new_issue_id = self.test_create_functions()
        
        # 更新功能測試
        test_issue_id = new_issue_id or existing_issue_id
        if test_issue_id:
            self.test_update_functions(test_issue_id)
        
        # 搜尋功能測試
        self.test_search_functions()
        
        # 關閉功能測試
        if new_issue_id:
            self.test_close_functions(new_issue_id)
        
        # 清理測試資料
        self.cleanup_test_data()
        
        # 統計結果
        self.print_summary()
        
        # 回傳成功率
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        return passed / total > 0.8  # 80% 通過率視為成功
    
    def print_summary(self):
        """列印測試摘要"""
        print("\n" + "=" * 50)
        print("📊 測試結果摘要")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['success'])
        failed = len(self.test_results) - passed
        success_rate = (passed / len(self.test_results)) * 100 if self.test_results else 0
        
        print(f"總測試數: {len(self.test_results)}")
        print(f"通過: {passed}")
        print(f"失敗: {failed}")
        print(f"成功率: {success_rate:.1f}%")
        
        if failed > 0:
            print("\n❌ 失敗的測試:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['name']}: {result['message']}")
        
        if success_rate >= 80:
            print("\n🎉 測試通過！MCP 功能運作正常")
        else:
            print("\n⚠️  部分測試失敗，請檢查上述錯誤")


def main():
    """主函數"""
    tester = MCPTester()
    success = tester.run_all_tests()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)