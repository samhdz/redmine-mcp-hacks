"""
Redmine MCP 服務器主程式
提供與 Redmine 系統整合的 MCP 工具
"""

from typing import Any
from mcp.server.fastmcp import FastMCP

from .config import get_config
from .redmine_client import get_client, RedmineAPIError


# 建立 FastMCP 服務器實例
mcp = FastMCP("Redmine MCP")


@mcp.tool()
def server_info() -> str:
    """取得服務器資訊和狀態"""
    config = get_config()
    return f"""Redmine MCP 服務器已啟動
- Redmine 網域: {config.redmine_domain}
- 除錯模式: {config.debug_mode}
- API 逾時: {config.redmine_timeout}秒"""


@mcp.tool()
def health_check() -> str:
    """健康檢查工具，確認服務器正常運作"""
    try:
        config = get_config()
        client = get_client()
        # 測試連線
        if client.test_connection():
            return f"✓ 服務器正常運作，已連接到 {config.redmine_domain}"
        else:
            return f"✗ 無法連接到 Redmine 服務器: {config.redmine_domain}"
    except Exception as e:
        return f"✗ 服務器異常: {str(e)}"


@mcp.tool()
def get_issue(issue_id: int, include_details: bool = True) -> str:
    """
    取得指定的 Redmine 議題詳細資訊
    
    Args:
        issue_id: 議題 ID
        include_details: 是否包含詳細資訊（描述、自訂欄位等）
    
    Returns:
        議題的詳細資訊，以易讀格式呈現
    """
    try:
        client = get_client()
        include_params = []
        if include_details:
            include_params = ['attachments', 'changesets', 'children', 'journals', 'relations', 'watchers']
        
        issue = client.get_issue(issue_id, include=include_params)
        
        # 格式化議題資訊
        result = f"""議題 #{issue.id}: {issue.subject}

基本資訊:
- 專案: {issue.project.get('name', 'N/A')} (ID: {issue.project.get('id', 'N/A')})
- 追蹤器: {issue.tracker.get('name', 'N/A')}
- 狀態: {issue.status.get('name', 'N/A')}
- 優先級: {issue.priority.get('name', 'N/A')}
- 建立者: {issue.author.get('name', 'N/A')}
- 指派給: {issue.assigned_to.get('name', '未指派') if issue.assigned_to else '未指派'}
- 完成度: {issue.done_ratio}%
- 建立時間: {issue.created_on or 'N/A'}
- 更新時間: {issue.updated_on or 'N/A'}

描述:
{issue.description or '無描述'}"""

        return result
        
    except RedmineAPIError as e:
        return f"取得議題失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def update_issue_status(issue_id: int, status_id: int, notes: str = "") -> str:
    """
    更新議題狀態
    
    Args:
        issue_id: 議題 ID
        status_id: 新的狀態 ID
        notes: 更新備註（可選）
    
    Returns:
        更新結果訊息
    """
    try:
        client = get_client()
        
        # 準備更新資料
        update_data = {'status_id': status_id}
        if notes.strip():
            update_data['notes'] = notes.strip()
        
        # 執行更新
        client.update_issue(issue_id, **update_data)
        
        # 取得更新後的議題資訊確認
        updated_issue = client.get_issue(issue_id)
        
        result = f"""議題狀態更新成功!

議題: #{issue_id} - {updated_issue.subject}
新狀態: {updated_issue.status.get('name', 'N/A')}"""

        if notes.strip():
            result += f"\n備註: {notes}"
            
        return result
        
    except RedmineAPIError as e:
        return f"更新議題狀態失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def list_project_issues(project_id: int, status_filter: str = "open", limit: int = 20) -> str:
    """
    列出專案的議題
    
    Args:
        project_id: 專案 ID
        status_filter: 狀態篩選 ("open", "closed", "all")
        limit: 最大回傳數量 (預設 20，最大 100)
    
    Returns:
        專案議題列表，以表格格式呈現
    """
    try:
        client = get_client()
        
        # 限制 limit 範圍
        limit = min(max(limit, 1), 100)
        
        # 根據狀態篩選設定參數
        params = {
            'project_id': project_id,
            'limit': limit,
            'sort': 'updated_on:desc'
        }
        
        # 處理狀態篩選
        if status_filter == "open":
            params['status_id'] = 'o'  # Redmine API 使用 'o' 表示開放狀態
        elif status_filter == "closed":
            params['status_id'] = 'c'  # Redmine API 使用 'c' 表示關閉狀態
        # "all" 則不設定 status_id
        
        # 取得議題列表
        issues = client.list_issues(**params)
        
        if not issues:
            return f"專案 {project_id} 中沒有找到符合條件的議題"
        
        # 取得專案資訊
        try:
            project = client.get_project(project_id)
            project_name = project.name
        except:
            project_name = f"專案 {project_id}"
        
        # 格式化議題列表
        result = f"""專案: {project_name}
狀態篩選: {status_filter}
找到 {len(issues)} 個議題:

{"ID":<8} {"標題":<40} {"狀態":<12} {"指派給":<15} {"更新時間":<10}
{"-"*8} {"-"*40} {"-"*12} {"-"*15} {"-"*10}"""

        for issue in issues:
            title = issue.subject[:37] + "..." if len(issue.subject) > 40 else issue.subject
            status = issue.status.get('name', 'N/A')[:10]
            assignee = issue.assigned_to.get('name', '未指派')[:13] if issue.assigned_to else '未指派'
            updated = issue.updated_on[:10] if issue.updated_on else 'N/A'
            
            result += f"\n{issue.id:<8} {title:<40} {status:<12} {assignee:<15} {updated:<10}"
        
        return result
        
    except RedmineAPIError as e:
        return f"列出專案議題失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def get_issue_statuses() -> str:
    """
    取得所有可用的議題狀態列表
    
    Returns:
        格式化的狀態列表
    """
    try:
        client = get_client()
        statuses = client.get_issue_statuses()
        
        if not statuses:
            return "沒有找到議題狀態"
        
        result = "可用的議題狀態:\n\n"
        result += f"{'ID':<5} {'名稱':<15} {'已關閉':<8}\n"
        result += f"{'-'*5} {'-'*15} {'-'*8}\n"
        
        for status in statuses:
            is_closed = "是" if status.get('is_closed', False) else "否"
            result += f"{status['id']:<5} {status['name']:<15} {is_closed:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"取得議題狀態失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def get_projects() -> str:
    """
    取得可存取的專案列表
    
    Returns:
        格式化的專案列表
    """
    try:
        client = get_client()
        projects = client.list_projects(limit=50)
        
        if not projects:
            return "沒有找到可存取的專案"
        
        result = f"找到 {len(projects)} 個專案:\n\n"
        result += f"{'ID':<5} {'識別碼':<20} {'名稱':<30} {'狀態':<8}\n"
        result += f"{'-'*5} {'-'*20} {'-'*30} {'-'*8}\n"
        
        for project in projects:
            status_text = "正常" if project.status == 1 else "封存"
            name = project.name[:27] + "..." if len(project.name) > 30 else project.name
            result += f"{project.id:<5} {project.identifier:<20} {name:<30} {status_text:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"取得專案列表失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def search_issues(query: str, project_id: int = None, limit: int = 10) -> str:
    """
    搜尋議題 (在標題或描述中搜尋關鍵字)
    
    Args:
        query: 搜尋關鍵字
        project_id: 限制在特定專案中搜尋 (可選)
        limit: 最大回傳數量 (預設 10，最大 50)
    
    Returns:
        符合搜尋條件的議題列表
    """
    try:
        if not query.strip():
            return "請提供搜尋關鍵字"
        
        client = get_client()
        limit = min(max(limit, 1), 50)
        
        # 設定搜尋參數
        params = {
            'limit': limit * 3,  # 取得更多結果以便篩選
            'sort': 'updated_on:desc'
        }
        
        if project_id:
            params['project_id'] = project_id
        
        # 取得議題列表
        all_issues = client.list_issues(**params)
        
        # 在本地端進行關鍵字篩選 (因為 Redmine API 沒有內建搜尋)
        query_lower = query.lower()
        matching_issues = []
        
        for issue in all_issues:
            if (query_lower in issue.subject.lower() or 
                (issue.description and query_lower in issue.description.lower())):
                matching_issues.append(issue)
                if len(matching_issues) >= limit:
                    break
        
        if not matching_issues:
            search_scope = f"專案 {project_id}" if project_id else "所有可存取的專案"
            return f"在 {search_scope} 中沒有找到包含 '{query}' 的議題"
        
        # 格式化結果
        result = f"搜尋關鍵字: '{query}'\n"
        if project_id:
            result += f"搜尋範圍: 專案 {project_id}\n"
        result += f"找到 {len(matching_issues)} 個相關議題:\n\n"
        
        result += f"{'ID':<8} {'標題':<35} {'狀態':<12} {'專案':<15}\n"
        result += f"{'-'*8} {'-'*35} {'-'*12} {'-'*15}\n"
        
        for issue in matching_issues:
            title = issue.subject[:32] + "..." if len(issue.subject) > 35 else issue.subject
            status = issue.status.get('name', 'N/A')[:10]
            project_name = issue.project.get('name', 'N/A')[:13]
            
            result += f"{issue.id:<8} {title:<35} {status:<12} {project_name:<15}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"搜尋議題失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def update_issue_content(issue_id: int, subject: str = None, description: str = None, 
                        priority_id: int = None, done_ratio: int = None) -> str:
    """
    更新議題內容（標題、描述、優先級、完成度等）
    
    Args:
        issue_id: 議題 ID
        subject: 新的議題標題（可選）
        description: 新的議題描述（可選）
        priority_id: 新的優先級 ID（可選）
        done_ratio: 新的完成百分比 0-100（可選）
    
    Returns:
        更新結果訊息
    """
    try:
        client = get_client()
        
        # 準備更新資料
        update_data = {}
        changes = []
        
        if subject is not None:
            update_data['subject'] = subject.strip()
            changes.append(f"標題: {subject}")
        
        if description is not None:
            update_data['description'] = description
            changes.append("描述已更新")
        
        if priority_id is not None:
            update_data['priority_id'] = priority_id
            changes.append(f"優先級 ID: {priority_id}")
        
        if done_ratio is not None:
            if not (0 <= done_ratio <= 100):
                return "錯誤: 完成百分比必須在 0-100 之間"
            update_data['done_ratio'] = done_ratio
            changes.append(f"完成度: {done_ratio}%")
        
        if not update_data:
            return "錯誤: 請至少提供一個要更新的欄位"
        
        # 執行更新
        client.update_issue(issue_id, **update_data)
        
        # 取得更新後的議題資訊
        updated_issue = client.get_issue(issue_id)
        
        result = f"""議題內容更新成功!

議題: #{issue_id} - {updated_issue.subject}
已更新的欄位:
{chr(10).join(f"- {change}" for change in changes)}

目前狀態:
- 狀態: {updated_issue.status.get('name', 'N/A')}
- 優先級: {updated_issue.priority.get('name', 'N/A')}
- 完成度: {updated_issue.done_ratio}%"""

        return result
        
    except RedmineAPIError as e:
        return f"更新議題內容失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def add_issue_note(issue_id: int, notes: str, private: bool = False) -> str:
    """
    為議題新增備註
    
    Args:
        issue_id: 議題 ID
        notes: 備註內容
        private: 是否為私有備註（預設否）
    
    Returns:
        新增結果訊息
    """
    try:
        if not notes.strip():
            return "錯誤: 備註內容不能為空"
        
        client = get_client()
        
        # 準備更新資料（只新增備註，不改其他欄位）
        update_data = {'notes': notes.strip()}
        if private:
            update_data['private_notes'] = True
        
        # 執行更新
        client.update_issue(issue_id, **update_data)
        
        # 取得議題資訊
        issue = client.get_issue(issue_id)
        
        privacy_text = "私有" if private else "公開"
        result = f"""備註新增成功!

議題: #{issue_id} - {issue.subject}
備註類型: {privacy_text}
備註內容:
{notes.strip()}"""

        return result
        
    except RedmineAPIError as e:
        return f"新增議題備註失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def assign_issue(issue_id: int, user_id: int = None, notes: str = "") -> str:
    """
    指派議題給用戶
    
    Args:
        issue_id: 議題 ID
        user_id: 指派給的用戶 ID（如果為 None 則取消指派）
        notes: 指派備註（可選）
    
    Returns:
        指派結果訊息
    """
    try:
        client = get_client()
        
        # 準備更新資料
        update_data = {}
        
        if user_id is not None:
            update_data['assigned_to_id'] = user_id
            action_text = f"指派給用戶 ID {user_id}"
        else:
            update_data['assigned_to_id'] = None
            action_text = "取消指派"
        
        if notes.strip():
            update_data['notes'] = notes.strip()
        
        # 執行更新
        client.update_issue(issue_id, **update_data)
        
        # 取得更新後的議題資訊
        updated_issue = client.get_issue(issue_id)
        
        assignee_name = "未指派"
        if updated_issue.assigned_to:
            assignee_name = updated_issue.assigned_to.get('name', f"用戶 ID {user_id}")
        
        result = f"""議題指派更新成功!

議題: #{issue_id} - {updated_issue.subject}
動作: {action_text}
目前指派給: {assignee_name}"""

        if notes.strip():
            result += f"\n備註: {notes}"

        return result
        
    except RedmineAPIError as e:
        return f"指派議題失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def create_new_issue(project_id: int, subject: str, description: str = "", 
                    tracker_id: int = None, priority_id: int = None, 
                    assigned_to_id: int = None) -> str:
    """
    建立新的 Redmine 議題
    
    Args:
        project_id: 專案 ID
        subject: 議題標題
        description: 議題描述（可選）
        tracker_id: 追蹤器 ID（可選）
        priority_id: 優先級 ID（可選）
        assigned_to_id: 指派給的用戶 ID（可選）
    
    Returns:
        建立結果訊息
    """
    try:
        if not subject.strip():
            return "錯誤: 議題標題不能為空"
        
        client = get_client()
        
        # 建立議題
        new_issue_id = client.create_issue(
            project_id=project_id,
            subject=subject.strip(),
            description=description,
            tracker_id=tracker_id,
            priority_id=priority_id,
            assigned_to_id=assigned_to_id
        )
        
        # 取得建立的議題資訊
        new_issue = client.get_issue(new_issue_id)
        
        result = f"""新議題建立成功!

議題 ID: #{new_issue_id}
標題: {new_issue.subject}
專案: {new_issue.project.get('name', 'N/A')}
追蹤器: {new_issue.tracker.get('name', 'N/A')}
狀態: {new_issue.status.get('name', 'N/A')}
優先級: {new_issue.priority.get('name', 'N/A')}
指派給: {new_issue.assigned_to.get('name', '未指派') if new_issue.assigned_to else '未指派'}"""

        if description:
            result += f"\n\n描述:\n{description}"

        return result
        
    except RedmineAPIError as e:
        return f"建立議題失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def get_my_issues(status_filter: str = "open", limit: int = 20) -> str:
    """
    取得指派給我的議題列表
    
    Args:
        status_filter: 狀態篩選 ("open", "closed", "all")
        limit: 最大回傳數量 (預設 20，最大 100)
    
    Returns:
        我的議題列表
    """
    try:
        client = get_client()
        
        # 先取得當前用戶資訊
        current_user = client.get_current_user()
        user_id = current_user['id']
        user_name = current_user.get('firstname', '') + ' ' + current_user.get('lastname', '')
        
        # 限制 limit 範圍
        limit = min(max(limit, 1), 100)
        
        # 設定查詢參數
        params = {
            'assigned_to_id': user_id,
            'limit': limit,
            'sort': 'updated_on:desc'
        }
        
        # 處理狀態篩選
        if status_filter == "open":
            params['status_id'] = 'o'  # Redmine API 使用 'o' 表示開放狀態
        elif status_filter == "closed":
            params['status_id'] = 'c'  # Redmine API 使用 'c' 表示關閉狀態
        
        # 取得議題列表
        issues = client.list_issues(**params)
        
        if not issues:
            return f"沒有找到指派給 {user_name.strip()} 的{status_filter}議題"
        
        # 格式化結果
        result = f"""指派給 {user_name.strip()} 的議題:
狀態篩選: {status_filter}
找到 {len(issues)} 個議題:

{"ID":<8} {"標題":<35} {"專案":<15} {"狀態":<12} {"更新時間":<10}
{"-"*8} {"-"*35} {"-"*15} {"-"*12} {"-"*10}"""

        for issue in issues:
            title = issue.subject[:32] + "..." if len(issue.subject) > 35 else issue.subject
            project_name = issue.project.get('name', 'N/A')[:13]
            status = issue.status.get('name', 'N/A')[:10]
            updated = issue.updated_on[:10] if issue.updated_on else 'N/A'
            
            result += f"\n{issue.id:<8} {title:<35} {project_name:<15} {status:<12} {updated:<10}"
        
        return result
        
    except RedmineAPIError as e:
        return f"取得我的議題失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def close_issue(issue_id: int, notes: str = "", done_ratio: int = 100) -> str:
    """
    關閉議題（設定為已完成狀態）
    
    Args:
        issue_id: 議題 ID
        notes: 關閉備註（可選）
        done_ratio: 完成百分比（預設 100%）
    
    Returns:
        關閉結果訊息
    """
    try:
        client = get_client()
        
        # 取得可用狀態列表，尋找關閉狀態
        statuses = client.get_issue_statuses()
        closed_status_id = None
        
        for status in statuses:
            if status.get('is_closed', False):
                closed_status_id = status['id']
                break
        
        if closed_status_id is None:
            return "錯誤: 找不到可用的關閉狀態"
        
        # 準備更新資料
        update_data = {
            'status_id': closed_status_id,
            'done_ratio': min(max(done_ratio, 0), 100)
        }
        
        if notes.strip():
            update_data['notes'] = notes.strip()
        
        # 執行更新
        client.update_issue(issue_id, **update_data)
        
        # 取得更新後的議題資訊
        updated_issue = client.get_issue(issue_id)
        
        result = f"""議題關閉成功!

議題: #{issue_id} - {updated_issue.subject}
狀態: {updated_issue.status.get('name', 'N/A')}
完成度: {updated_issue.done_ratio}%"""

        if notes.strip():
            result += f"\n關閉備註: {notes}"

        return result
        
    except RedmineAPIError as e:
        return f"關閉議題失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


def main():
    """MCP 服務器主入口點"""
    # 透過 stdio 運行服務器
    mcp.run('stdio')


if __name__ == "__main__":
    main()