"""
Redmine MCP 服務器主程式
提供與 Redmine 系統整合的 MCP 工具
"""

from typing import Any
from datetime import datetime
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
        include_details: 是否包含詳細資訊（描述、備註、附件等）
    
    Returns:
        議題的詳細資訊，以易讀格式呈現
    """
    try:
        client = get_client()
        include_params = []
        if include_details:
            include_params = ['attachments', 'changesets', 'children', 'journals', 'relations', 'watchers']
        
        # 使用新的 get_issue_raw 方法取得完整資料
        issue_data = client.get_issue_raw(issue_id, include=include_params)
        
        # 格式化基本議題資訊
        # 處理父議題資訊
        parent_info = "無父議題"
        if 'parent' in issue_data and issue_data['parent']:
            parent_info = f"#{issue_data['parent']['id']} - {issue_data['parent'].get('subject', 'N/A')}"
        
        result = f"""議題 #{issue_data['id']}: {issue_data['subject']}

基本資訊:
- 專案: {issue_data['project'].get('name', 'N/A')} (ID: {issue_data['project'].get('id', 'N/A')})
- 追蹤器: {issue_data['tracker'].get('name', 'N/A')}
- 狀態: {issue_data['status'].get('name', 'N/A')}
- 優先級: {issue_data['priority'].get('name', 'N/A')}
- 建立者: {issue_data['author'].get('name', 'N/A')}
- 指派給: {issue_data.get('assigned_to', {}).get('name', '未指派') if issue_data.get('assigned_to') else '未指派'}
- 父議題: {parent_info}
- 完成度: {issue_data.get('done_ratio', 0)}%
- 開始日期: {issue_data.get('start_date', '未設定')}
- 完成日期: {issue_data.get('due_date', '未設定')}
- 預估工時: {issue_data.get('estimated_hours', '未設定')} 小時
- 建立時間: {issue_data.get('created_on', 'N/A')}
- 更新時間: {issue_data.get('updated_on', 'N/A')}

描述:
{issue_data.get('description', '無描述')}"""

        # 加入附件資訊
        if include_details and 'attachments' in issue_data and issue_data['attachments']:
            result += f"\n\n附件 ({len(issue_data['attachments'])} 個):"
            for attachment in issue_data['attachments']:
                file_size = attachment.get('filesize', 0)
                file_size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
                size_text = f"{file_size_mb:.2f} MB" if file_size_mb >= 1 else f"{file_size} bytes"
                
                result += f"""
- 檔名: {attachment.get('filename', 'N/A')}
  大小: {size_text}
  類型: {attachment.get('content_type', 'N/A')}
  上傳者: {attachment.get('author', {}).get('name', 'N/A')}
  上傳時間: {attachment.get('created_on', 'N/A')}
  下載連結: {client.config.redmine_domain}/attachments/download/{attachment.get('id', '')}/{attachment.get('filename', '')}"""

        # 加入備註/歷史記錄
        if include_details and 'journals' in issue_data and issue_data['journals']:
            # 過濾出有備註內容的記錄
            notes_journals = [j for j in issue_data['journals'] if j.get('notes', '').strip()]
            
            if notes_journals:
                result += f"\n\n備註/歷史記錄 ({len(notes_journals)} 筆):"
                for i, journal in enumerate(notes_journals, 1):
                    author_name = journal.get('user', {}).get('name', 'N/A')
                    created_on = journal.get('created_on', 'N/A')
                    notes = journal.get('notes', '').strip()
                    
                    result += f"""

#{i} - {author_name} ({created_on}):
{notes}"""

        return result
        
    except RedmineAPIError as e:
        return f"取得議題失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def update_issue_status(issue_id: int, status_id: int = None, status_name: str = None, notes: str = "") -> str:
    """
    更新議題狀態
    
    Args:
        issue_id: 議題 ID
        status_id: 新的狀態 ID（與 status_name 二選一）
        status_name: 新的狀態名稱（與 status_id 二選一）
        notes: 更新備註（可選）
    
    Returns:
        更新結果訊息
    """
    try:
        client = get_client()
        
        # 處理狀態參數
        final_status_id = status_id
        if status_name:
            final_status_id = client.find_status_id_by_name(status_name)
            if not final_status_id:
                return f"找不到狀態名稱：「{status_name}」\n\n可用狀態：\n" + "\n".join([f"- {name}" for name in client.get_available_statuses().keys()])
        
        if not final_status_id:
            return "錯誤：必須提供 status_id 或 status_name 其中一個參數"
        
        # 準備更新資料
        update_data = {'status_id': final_status_id}
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
def get_trackers() -> str:
    """
    取得所有可用的追蹤器列表
    
    Returns:
        格式化的追蹤器列表
    """
    try:
        client = get_client()
        trackers = client.get_trackers()
        
        if not trackers:
            return "沒有找到追蹤器"
        
        result = "可用的追蹤器:\n\n"
        result += f"{'ID':<5} {'名稱':<20} {'預設狀態':<12}\n"
        result += f"{'-'*5} {'-'*20} {'-'*12}\n"
        
        for tracker in trackers:
            default_status = tracker.get('default_status', {}).get('name', 'N/A')
            result += f"{tracker['id']:<5} {tracker['name']:<20} {default_status:<12}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"取得追蹤器列表失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def get_priorities() -> str:
    """
    取得所有可用的議題優先級列表
    
    Returns:
        格式化的優先級列表
    """
    try:
        client = get_client()
        priorities = client.get_priorities()
        
        if not priorities:
            return "沒有找到議題優先級"
        
        result = "可用的議題優先級:\n\n"
        result += f"{'ID':<5} {'名稱':<15} {'預設':<8}\n"
        result += f"{'-'*5} {'-'*15} {'-'*8}\n"
        
        for priority in priorities:
            is_default = "是" if priority.get('is_default', False) else "否"
            result += f"{priority['id']:<5} {priority['name']:<15} {is_default:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"取得議題優先級失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def get_time_entry_activities() -> str:
    """
    取得所有可用的時間追蹤活動列表
    
    Returns:
        格式化的時間追蹤活動列表
    """
    try:
        client = get_client()
        activities = client.get_time_entry_activities()
        
        if not activities:
            return "沒有找到時間追蹤活動"
        
        result = "可用的時間追蹤活動:\n\n"
        result += f"{'ID':<5} {'名稱':<20} {'預設':<8}\n"
        result += f"{'-'*5} {'-'*20} {'-'*8}\n"
        
        for activity in activities:
            is_default = "是" if activity.get('is_default', False) else "否"
            result += f"{activity['id']:<5} {activity['name']:<20} {is_default:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"取得時間追蹤活動失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def get_document_categories() -> str:
    """
    取得所有可用的文件分類列表
    
    Returns:
        格式化的文件分類列表
    """
    try:
        client = get_client()
        categories = client.get_document_categories()
        
        if not categories:
            return "沒有找到文件分類"
        
        result = "可用的文件分類:\n\n"
        result += f"{'ID':<5} {'名稱':<25} {'預設':<8}\n"
        result += f"{'-'*5} {'-'*25} {'-'*8}\n"
        
        for category in categories:
            is_default = "是" if category.get('is_default', False) else "否"
            result += f"{category['id']:<5} {category['name']:<25} {is_default:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"取得文件分類失敗: {str(e)}"
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
                        priority_id: int = None, priority_name: str = None,
                        done_ratio: int = None, tracker_id: int = None, tracker_name: str = None,
                        parent_issue_id: int = None, remove_parent: bool = False, start_date: str = None, due_date: str = None,
                        estimated_hours: float = None) -> str:
    """
    更新議題內容（標題、描述、優先級、完成度、追蹤器、日期、工時等）
    
    Args:
        issue_id: 議題 ID
        subject: 新的議題標題（可選）
        description: 新的議題描述（可選）
        priority_id: 新的優先級 ID（與 priority_name 二選一）
        priority_name: 新的優先級名稱（與 priority_id 二選一）
        done_ratio: 新的完成百分比 0-100（可選）
        tracker_id: 新的追蹤器 ID（與 tracker_name 二選一）
        tracker_name: 新的追蹤器名稱（與 tracker_id 二選一）
        parent_issue_id: 新的父議題 ID（可選）
        remove_parent: 是否移除父議題關係（可選）
        start_date: 新的開始日期 YYYY-MM-DD 格式（可選）
        due_date: 新的完成日期 YYYY-MM-DD 格式（可選）
        estimated_hours: 新的預估工時（可選）
    
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
        
        # 處理優先級參數
        if priority_name:
            priority_id = client.find_priority_id_by_name(priority_name)
            if not priority_id:
                return f"找不到優先級名稱：「{priority_name}」\n\n可用優先級：\n" + "\n".join([f"- {name}" for name in client.get_available_priorities().keys()])
        
        if priority_id is not None:
            update_data['priority_id'] = priority_id
            changes.append(f"優先級 ID: {priority_id}")
        
        if done_ratio is not None:
            if not (0 <= done_ratio <= 100):
                return "錯誤: 完成百分比必須在 0-100 之間"
            update_data['done_ratio'] = done_ratio
            changes.append(f"完成度: {done_ratio}%")
        
        # 處理追蹤器參數
        if tracker_name:
            tracker_id = client.find_tracker_id_by_name(tracker_name)
            if not tracker_id:
                return f"找不到追蹤器名稱：「{tracker_name}」\n\n可用追蹤器：\n" + "\n".join([f"- {name}" for name in client.get_available_trackers().keys()])
        
        if tracker_id is not None:
            update_data['tracker_id'] = tracker_id
            changes.append(f"追蹤器 ID: {tracker_id}")
        
        if remove_parent:
            update_data['parent_issue_id'] = None
            changes.append("移除父議題關係")
        elif parent_issue_id is not None:
            update_data['parent_issue_id'] = parent_issue_id
            changes.append(f"父議題 ID: {parent_issue_id}")
        
        if start_date is not None:
            # 驗證日期格式
            try:
                from datetime import datetime
                datetime.strptime(start_date, '%Y-%m-%d')
                update_data['start_date'] = start_date
                changes.append(f"開始日期: {start_date}")
            except ValueError:
                return "錯誤: 開始日期格式必須為 YYYY-MM-DD"
        
        if due_date is not None:
            # 驗證日期格式
            try:
                from datetime import datetime
                datetime.strptime(due_date, '%Y-%m-%d')
                update_data['due_date'] = due_date
                changes.append(f"完成日期: {due_date}")
            except ValueError:
                return "錯誤: 完成日期格式必須為 YYYY-MM-DD"
        
        if estimated_hours is not None:
            if estimated_hours < 0:
                return "錯誤: 預估工時不能為負數"
            update_data['estimated_hours'] = estimated_hours
            changes.append(f"預估工時: {estimated_hours} 小時")
        
        if not update_data and not changes:
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
- 追蹤器: {updated_issue.tracker.get('name', 'N/A')}
- 狀態: {updated_issue.status.get('name', 'N/A')}
- 優先級: {updated_issue.priority.get('name', 'N/A')}
- 完成度: {updated_issue.done_ratio}%"""

        return result
        
    except RedmineAPIError as e:
        return f"更新議題內容失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def add_issue_note(issue_id: int, notes: str, private: bool = False, 
                   spent_hours: float = None, activity_name: str = None, 
                   activity_id: int = None, spent_on: str = None) -> str:
    """
    為議題新增備註，可同時記錄時間
    
    Args:
        issue_id: 議題 ID
        notes: 備註內容
        private: 是否為私有備註（預設否）
        spent_hours: 耗用工時（小時）
        activity_name: 活動名稱（與 activity_id 二選一）
        activity_id: 活動 ID（與 activity_name 二選一）
        spent_on: 記錄日期 YYYY-MM-DD 格式（可選，預設今日）
    
    Returns:
        新增結果訊息
    """
    try:
        if not notes.strip():
            return "錯誤: 備註內容不能為空"
        
        client = get_client()
        time_entry_id = None
        
        # 處理時間記錄
        if spent_hours is not None:
            if spent_hours <= 0:
                return "錯誤: 耗用工時必須大於 0"
            
            # 處理活動參數
            final_activity_id = activity_id
            if activity_name:
                final_activity_id = client.find_time_entry_activity_id_by_name(activity_name)
                if not final_activity_id:
                    available_activities = client.get_available_time_entry_activities()
                    return f"找不到時間追蹤活動名稱：「{activity_name}」\n\n可用活動：\n" + "\n".join([f"- {name}" for name in available_activities.keys()])
            
            if not final_activity_id:
                return "錯誤: 必須提供 activity_id 或 activity_name 參數"
            
            # 建立時間記錄
            try:
                time_entry_id = client.create_time_entry(
                    issue_id=issue_id,
                    hours=spent_hours,
                    activity_id=final_activity_id,
                    comments=notes.strip(),
                    spent_on=spent_on
                )
            except Exception as e:
                return f"建立時間記錄失敗: {str(e)}"
        
        # 準備更新資料（新增備註）
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

        # 如果有建立時間記錄，添加相關資訊
        if time_entry_id:
            from datetime import date
            actual_date = spent_on if spent_on else date.today().strftime('%Y-%m-%d')
            activity_name_display = activity_name if activity_name else f"ID {final_activity_id}"
            result += f"""

時間記錄新增成功!
- 時間記錄 ID: {time_entry_id}
- 耗用工時: {spent_hours} 小時
- 活動: {activity_name_display}
- 記錄日期: {actual_date}"""

        return result
        
    except RedmineAPIError as e:
        return f"新增議題備註失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def assign_issue(issue_id: int, user_id: int = None, user_name: str = None, user_login: str = None, notes: str = "") -> str:
    """
    指派議題給用戶
    
    Args:
        issue_id: 議題 ID
        user_id: 指派給的用戶 ID（與 user_name/user_login 三選一）
        user_name: 指派給的用戶姓名（與 user_id/user_login 三選一）
        user_login: 指派給的用戶登入名（與 user_id/user_name 三選一）
        notes: 指派備註（可選）
    
    Returns:
        指派結果訊息
    """
    try:
        client = get_client()
        
        # 處理用戶參數
        final_user_id = user_id
        if user_name:
            final_user_id = client.find_user_id_by_name(user_name)
            if not final_user_id:
                users = client.get_available_users()
                return f"找不到用戶姓名：「{user_name}」\n\n可用用戶（姓名）：\n" + "\n".join([f"- {name}" for name in users['by_name'].keys()])
        elif user_login:
            final_user_id = client.find_user_id_by_login(user_login)
            if not final_user_id:
                users = client.get_available_users()
                return f"找不到用戶登入名：「{user_login}」\n\n可用用戶（登入名）：\n" + "\n".join([f"- {login}" for login in users['by_login'].keys()])
        
        # 準備更新資料
        update_data = {}
        
        if final_user_id is not None:
            update_data['assigned_to_id'] = final_user_id
            action_text = f"指派給用戶 ID {final_user_id}"
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
                    tracker_id: int = None, tracker_name: str = None,
                    priority_id: int = None, priority_name: str = None,
                    assigned_to_id: int = None, assigned_to_name: str = None, assigned_to_login: str = None) -> str:
    """
    建立新的 Redmine 議題
    
    Args:
        project_id: 專案 ID
        subject: 議題標題
        description: 議題描述（可選）
        tracker_id: 追蹤器 ID（與 tracker_name 二選一）
        tracker_name: 追蹤器名稱（與 tracker_id 二選一）
        priority_id: 優先級 ID（與 priority_name 二選一）
        priority_name: 優先級名稱（與 priority_id 二選一）
        assigned_to_id: 指派給的用戶 ID（與 assigned_to_name/assigned_to_login 三選一）
        assigned_to_name: 指派給的用戶姓名（與 assigned_to_id/assigned_to_login 三選一）
        assigned_to_login: 指派給的用戶登入名（與 assigned_to_id/assigned_to_name 三選一）
    
    Returns:
        建立結果訊息
    """
    try:
        if not subject.strip():
            return "錯誤: 議題標題不能為空"
        
        client = get_client()
        
        # 處理追蹤器參數
        final_tracker_id = tracker_id
        if tracker_name:
            final_tracker_id = client.find_tracker_id_by_name(tracker_name)
            if not final_tracker_id:
                return f"找不到追蹤器名稱：「{tracker_name}」\n\n可用追蹤器：\n" + "\n".join([f"- {name}" for name in client.get_available_trackers().keys()])
        
        # 處理優先級參數
        final_priority_id = priority_id
        if priority_name:
            final_priority_id = client.find_priority_id_by_name(priority_name)
            if not final_priority_id:
                return f"找不到優先級名稱：「{priority_name}」\n\n可用優先級：\n" + "\n".join([f"- {name}" for name in client.get_available_priorities().keys()])
        
        # 處理指派用戶參數
        final_assigned_to_id = assigned_to_id
        if assigned_to_name:
            final_assigned_to_id = client.find_user_id_by_name(assigned_to_name)
            if not final_assigned_to_id:
                users = client.get_available_users()
                return f"找不到用戶姓名：「{assigned_to_name}」\n\n可用用戶（姓名）：\n" + "\n".join([f"- {name}" for name in users['by_name'].keys()])
        elif assigned_to_login:
            final_assigned_to_id = client.find_user_id_by_login(assigned_to_login)
            if not final_assigned_to_id:
                users = client.get_available_users()
                return f"找不到用戶登入名：「{assigned_to_login}」\n\n可用用戶（登入名）：\n" + "\n".join([f"- {login}" for login in users['by_login'].keys()])
        
        # 建立議題
        new_issue_id = client.create_issue(
            project_id=project_id,
            subject=subject.strip(),
            description=description,
            tracker_id=final_tracker_id,
            priority_id=final_priority_id,
            assigned_to_id=final_assigned_to_id
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


@mcp.tool()
def search_users(query: str, limit: int = 10) -> str:
    """
    搜尋用戶（依姓名或登入名）
    
    Args:
        query: 搜尋關鍵字（姓名或登入名）
        limit: 最大回傳數量 (預設 10，最大 50)
    
    Returns:
        符合搜尋條件的用戶列表
    """
    try:
        if not query.strip():
            return "請提供搜尋關鍵字"
        
        client = get_client()
        limit = min(max(limit, 1), 50)
        
        users = client.search_users(query, limit)
        
        if not users:
            return f"沒有找到匹配「{query}」的用戶"
        
        result = f"搜尋關鍵字: '{query}'\n找到 {len(users)} 個相關用戶:\n\n"
        result += f"{'ID':<5} {'登入名':<15} {'姓名':<20} {'狀態':<8}\n"
        result += f"{'-'*5} {'-'*15} {'-'*20} {'-'*8}\n"
        
        for user in users:
            full_name = f"{user.firstname} {user.lastname}".strip()
            if not full_name:
                full_name = user.login
            status_text = "啟用" if user.status == 1 else "停用"
            result += f"{user.id:<5} {user.login:<15} {full_name:<20} {status_text:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"搜尋用戶失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def list_users(limit: int = 20, status_filter: str = "active") -> str:
    """
    列出所有用戶
    
    Args:
        limit: 最大回傳數量 (預設 20，最大 100)
        status_filter: 狀態篩選 ("active", "locked", "all")
    
    Returns:
        用戶列表，以表格格式呈現
    """
    try:
        client = get_client()
        limit = min(max(limit, 1), 100)
        
        # 轉換狀態篩選
        status = None
        if status_filter == "active":
            status = 1
        elif status_filter == "locked":
            status = 3
        
        users = client.list_users(limit=limit, status=status)
        
        if not users:
            return "沒有找到用戶"
        
        result = f"找到 {len(users)} 個用戶:\n\n"
        result += f"{'ID':<5} {'登入名':<15} {'姓名':<20} {'Email':<25} {'狀態':<8}\n"
        result += f"{'-'*5} {'-'*15} {'-'*20} {'-'*25} {'-'*8}\n"
        
        for user in users:
            full_name = f"{user.firstname} {user.lastname}".strip()
            if not full_name:
                full_name = user.login
            status_text = "啟用" if user.status == 1 else "停用"
            email = user.mail[:22] + "..." if len(user.mail) > 25 else user.mail
            result += f"{user.id:<5} {user.login:<15} {full_name:<20} {email:<25} {status_text:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"取得用戶列表失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def get_user(user_id: int) -> str:
    """
    取得特定用戶的詳細資訊
    
    Args:
        user_id: 用戶 ID
        
    Returns:
        用戶的詳細資訊，以易讀格式呈現
    """
    try:
        client = get_client()
        user_data = client.get_user(user_id)
        
        # 格式化用戶資訊
        result = f"用戶 #{user_id}: {user_data.get('firstname', '')} {user_data.get('lastname', '')}\n\n"
        result += "基本資訊:\n"
        result += f"- 登入名: {user_data.get('login', 'N/A')}\n"
        result += f"- Email: {user_data.get('mail', 'N/A')}\n"
        result += f"- 狀態: {'啟用' if user_data.get('status', 1) == 1 else '停用'}\n"
        result += f"- 建立時間: {user_data.get('created_on', 'N/A')}\n"
        
        if user_data.get('last_login_on'):
            result += f"- 最後登入: {user_data.get('last_login_on')}\n"
        
        # 群組資訊
        if user_data.get('groups'):
            result += "\n群組:\n"
            for group in user_data['groups']:
                result += f"- {group.get('name', 'N/A')}\n"
        
        # 自訂欄位
        if user_data.get('custom_fields'):
            result += "\n自訂欄位:\n"
            for field in user_data['custom_fields']:
                if field.get('value'):
                    result += f"- {field.get('name', 'N/A')}: {field.get('value', 'N/A')}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"取得用戶資訊失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


@mcp.tool()
def refresh_cache() -> str:
    """
    手動刷新列舉值和用戶快取
    
    Returns:
        刷新結果訊息
    """
    try:
        client = get_client()
        client.refresh_cache()
        
        # 取得快取資訊
        cache = client._load_enum_cache()
        domain = cache.get('domain', 'N/A')
        cache_time = cache.get('cache_time', 0)
        
        if cache_time > 0:
            cache_datetime = datetime.fromtimestamp(cache_time).strftime('%Y-%m-%d %H:%M:%S')
        else:
            cache_datetime = 'N/A'
        
        result = f"""快取刷新成功!

Domain: {domain}
快取時間: {cache_datetime}

快取內容統計:
- 優先權: {len(cache.get('priorities', {}))} 個
- 狀態: {len(cache.get('statuses', {}))} 個  
- 追蹤器: {len(cache.get('trackers', {}))} 個
- 用戶（姓名）: {len(cache.get('users_by_name', {}))} 個
- 用戶（登入名）: {len(cache.get('users_by_login', {}))} 個

快取位置: {client._cache_file}"""
        
        return result
        
    except RedmineAPIError as e:
        return f"刷新快取失敗: {str(e)}"
    except Exception as e:
        return f"系統錯誤: {str(e)}"


def main():
    """MCP 服務器主入口點"""
    # 透過 stdio 運行服務器
    mcp.run('stdio')


if __name__ == "__main__":
    main()