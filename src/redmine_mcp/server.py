"""
Redmine MCP Server Main Program
Provides MCP tools integrated with the Redmine system
"""

import os
from typing import Any
from datetime import datetime

# Ensure configuration is loaded before FastMCP initialization
# This handles all environment variable settings, including FASTMCP_LOG_LEVEL
from .config import get_config
config = get_config()

from mcp.server.fastmcp import FastMCP
from .redmine_client import get_client, RedmineAPIError

# Create FastMCP server instance
mcp = FastMCP("Redmine MCP")


@mcp.tool()
def server_info() -> str:
    """Get server information and status"""
    config = get_config()
    return f"""Redmine MCP server started
- Redmine domain: {config.redmine_domain}
- Debug mode: {config.debug_mode}
- API timeout: {config.redmine_timeout} seconds"""


@mcp.tool()
def health_check() -> str:
    """Health check tool to confirm server is running normally"""
    try:
        config = get_config()
        client = get_client()
        # Test connection
        if client.test_connection():
            return f"✓ Server is running normally, connected to {config.redmine_domain}"
        else:
            return f"✗ Unable to connect to Redmine server: {config.redmine_domain}"
    except Exception as e:
        return f"✗ Server error: {str(e)}"


@mcp.tool()
def get_issue(issue_id: int, include_details: bool = True) -> str:
    """
    Get detailed information for a specified Redmine issue
    
    Args:
        issue_id: Issue ID
        include_details: Whether to include details (description, notes, attachments, etc.)
    
    Returns:
        Detailed issue information in a readable format
    """
    try:
        client = get_client()
        include_params = []
        if include_details:
            include_params = ['attachments', 'changesets', 'children', 'journals', 'relations', 'watchers']
        
        # Use new get_issue_raw method to get full data
        issue_data = client.get_issue_raw(issue_id, include=include_params)
        
        # Format basic issue info
        # Handle parent issue info
        parent_info = "No parent issue"
        if 'parent' in issue_data and issue_data['parent']:
            parent_info = f"#{issue_data['parent']['id']} - {issue_data['parent'].get('subject', 'N/A')}"
        
        result = f"""Issue #{issue_data['id']}: {issue_data['subject']}

Basic Info:
- Project: {issue_data['project'].get('name', 'N/A')} (ID: {issue_data['project'].get('id', 'N/A')})
- Tracker: {issue_data['tracker'].get('name', 'N/A')}
- Status: {issue_data['status'].get('name', 'N/A')}
- Priority: {issue_data['priority'].get('name', 'N/A')}
- Author: {issue_data['author'].get('name', 'N/A')}
- Assigned to: {issue_data.get('assigned_to', {}).get('name', 'Unassigned') if issue_data.get('assigned_to') else 'Unassigned'}
- Parent issue: {parent_info}
- Done ratio: {issue_data.get('done_ratio', 0)}%
- Start date: {issue_data.get('start_date', 'Not set')}
- Due date: {issue_data.get('due_date', 'Not set')}
- Estimated hours: {issue_data.get('estimated_hours', 'Not set')} hours
- Created on: {issue_data.get('created_on', 'N/A')}
- Updated on: {issue_data.get('updated_on', 'N/A')}

Description:
{issue_data.get('description', 'No description')}"""

        # Add attachment info
        if include_details and 'attachments' in issue_data and issue_data['attachments']:
            result += f"\n\nAttachments ({len(issue_data['attachments'])}):"
            for attachment in issue_data['attachments']:
                file_size = attachment.get('filesize', 0)
                file_size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
                size_text = f"{file_size_mb:.2f} MB" if file_size_mb >= 1 else f"{file_size} bytes"
                
                result += f"""
- Filename: {attachment.get('filename', 'N/A')}
  Size: {size_text}
  Type: {attachment.get('content_type', 'N/A')}
  Uploaded by: {attachment.get('author', {}).get('name', 'N/A')}
  Uploaded on: {attachment.get('created_on', 'N/A')}
  Download link: {client.config.redmine_domain}/attachments/download/{attachment.get('id', '')}/{attachment.get('filename', '')}"""

        # Add notes/history
        if include_details and 'journals' in issue_data and issue_data['journals']:
            # Filter records with note content
            notes_journals = [j for j in issue_data['journals'] if j.get('notes', '').strip()]
            
            if notes_journals:
                result += f"\n\nNotes/History ({len(notes_journals)}):"
                for i, journal in enumerate(notes_journals, 1):
                    author_name = journal.get('user', {}).get('name', 'N/A')
                    created_on = journal.get('created_on', 'N/A')
                    notes = journal.get('notes', '').strip()
                    
                    result += f"""

#{i} - {author_name} ({created_on}):
{notes}"""

        return result
        
    except RedmineAPIError as e:
        return f"Failed to get issue: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def update_issue_status(issue_id: int, status_id: int = None, status_name: str = None, notes: str = "") -> str:
    """
    Update issue status
    
    Args:
        issue_id: Issue ID
        status_id: New status ID (choose one with status_name)
        status_name: New status name (choose one with status_id)
        notes: Update notes (optional)
    
    Returns:
        Update result message
    """
    try:
        client = get_client()
        
        # Handle status parameter
        final_status_id = status_id
        if status_name:
            final_status_id = client.find_status_id_by_name(status_name)
            if not final_status_id:
                return f"Status name not found: \"{status_name}\"\n\nAvailable statuses:\n" + "\n".join([f"- {name}" for name in client.get_available_statuses().keys()])
        
        if not final_status_id:
            return "Error: Must provide either status_id or status_name"
        
        # Prepare update data
        update_data = {'status_id': final_status_id}
        if notes.strip():
            update_data['notes'] = notes.strip()
        
        # Perform update
        client.update_issue(issue_id, **update_data)
        
        # Get updated issue info for confirmation
        updated_issue = client.get_issue(issue_id)
        
        result = f"""Issue status updated successfully!

Issue: #{issue_id} - {updated_issue.subject}
New status: {updated_issue.status.get('name', 'N/A')}"""

        if notes.strip():
            result += f"\nNotes: {notes}"
            
        return result
        
    except RedmineAPIError as e:
        return f"Failed to update issue status: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def list_project_issues(project_id: int, status_filter: str = "open", limit: int = 20) -> str:
    """
    List issues for a project
    
    Args:
        project_id: Project ID
        status_filter: Status filter ("open", "closed", "all")
        limit: Maximum number of results (default 20, max 100)
    
    Returns:
        List of project issues in table format
    """
    try:
        client = get_client()
        
        # Restrict limit range
        limit = min(max(limit, 1), 100)
        
        # Set parameters based on status filter
        params = {
            'project_id': project_id,
            'limit': limit,
            'sort': 'updated_on:desc'
        }
        
        # Handle status filter
        if status_filter == "open":
            params['status_id'] = 'o'  # Redmine API uses 'o' for open status
        elif status_filter == "closed":
            params['status_id'] = 'c'  # Redmine API uses 'c' for closed status
        # "all" does not set status_id
        
        # Get issue list
        issues = client.list_issues(**params)
        
        if not issues:
            return f"No issues found in project {project_id} matching the criteria"
        
        # Get project info
        try:
            project = client.get_project(project_id)
            project_name = project.name
        except:
            project_name = f"Project {project_id}"
        
        # Format issue list
        result = f"""Project: {project_name}
Status filter: {status_filter}
Found {len(issues)} issues:

{"ID":<8} {"Title":<40} {"Status":<12} {"Assigned To":<15} {"Updated":<10}
{"-"*8} {"-"*40} {"-"*12} {"-"*15} {"-"*10}"""

        for issue in issues:
            title = issue.subject[:37] + "..." if len(issue.subject) > 40 else issue.subject
            status = issue.status.get('name', 'N/A')[:10]
            assignee = issue.assigned_to.get('name', 'Unassigned')[:13] if issue.assigned_to else 'Unassigned'
            updated = issue.updated_on[:10] if issue.updated_on else 'N/A'
            
            result += f"\n{issue.id:<8} {title:<40} {status:<12} {assignee:<15} {updated:<10}"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to list project issues: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def get_issue_statuses() -> str:
    """
    Get all available issue statuses
    
    Returns:
        Formatted status list
    """
    try:
        client = get_client()
        statuses = client.get_issue_statuses()
        
        if not statuses:
            return "No issue statuses found"
        
        result = "Available issue statuses:\n\n"
        result += f"{'ID':<5} {'Name':<15} {'Closed':<8}\n"
        result += f"{'-'*5} {'-'*15} {'-'*8}\n"
        
        for status in statuses:
            is_closed = "Yes" if status.get('is_closed', False) else "No"
            result += f"{status['id']:<5} {status['name']:<15} {is_closed:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to get issue statuses: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def get_trackers() -> str:
    """
    Get all available trackers
    
    Returns:
        Formatted tracker list
    """
    try:
        client = get_client()
        trackers = client.get_trackers()
        
        if not trackers:
            return "No trackers found"
        
        result = "Available trackers:\n\n"
        result += f"{'ID':<5} {'Name':<20} {'Default Status':<12}\n"
        result += f"{'-'*5} {'-'*20} {'-'*12}\n"
        
        for tracker in trackers:
            default_status = tracker.get('default_status', {}).get('name', 'N/A')
            result += f"{tracker['id']:<5} {tracker['name']:<20} {default_status:<12}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to get tracker list: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def get_priorities() -> str:
    """
    Get all available issue priorities
    
    Returns:
        Formatted priority list
    """
    try:
        client = get_client()
        priorities = client.get_priorities()
        
        if not priorities:
            return "No issue priorities found"
        
        result = "Available issue priorities:\n\n"
        result += f"{'ID':<5} {'Name':<15} {'Default':<8}\n"
        result += f"{'-'*5} {'-'*15} {'-'*8}\n"
        
        for priority in priorities:
            is_default = "Yes" if priority.get('is_default', False) else "No"
            result += f"{priority['id']:<5} {priority['name']:<15} {is_default:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to get issue priorities: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def get_time_entry_activities() -> str:
    """
    Get all available time tracking activities
    
    Returns:
        Formatted time tracking activity list
    """
    try:
        client = get_client()
        activities = client.get_time_entry_activities()
        
        if not activities:
            return "No time tracking activities found"
        
        result = "Available time tracking activities:\n\n"
        result += f"{'ID':<5} {'Name':<20} {'Default':<8}\n"
        result += f"{'-'*5} {'-'*20} {'-'*8}\n"
        
        for activity in activities:
            is_default = "Yes" if activity.get('is_default', False) else "No"
            result += f"{activity['id']:<5} {activity['name']:<20} {is_default:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to get time tracking activities: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def get_document_categories() -> str:
    """
    Get all available document categories
    
    Returns:
        Formatted document category list
    """
    try:
        client = get_client()
        categories = client.get_document_categories()
        
        if not categories:
            return "No document categories found"
        
        result = "Available document categories:\n\n"
        result += f"{'ID':<5} {'Name':<25} {'Default':<8}\n"
        result += f"{'-'*5} {'-'*25} {'-'*8}\n"
        
        for category in categories:
            is_default = "Yes" if category.get('is_default', False) else "No"
            result += f"{category['id']:<5} {category['name']:<25} {is_default:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to get document categories: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def get_projects() -> str:
    """
    Get list of accessible projects
    
    Returns:
        Formatted project list
    """
    try:
        client = get_client()
        projects = client.list_projects(limit=50)
        
        if not projects:
            return "No accessible projects found"
        
        result = f"Found {len(projects)} projects:\n\n"
        result += f"{'ID':<5} {'Identifier':<20} {'Name':<30} {'Status':<8}\n"
        result += f"{'-'*5} {'-'*20} {'-'*30} {'-'*8}\n"
        
        for project in projects:
            status_text = "Active" if project.status == 1 else "Archived"
            name = project.name[:27] + "..." if len(project.name) > 30 else project.name
            result += f"{project.id:<5} {project.identifier:<20} {name:<30} {status_text:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to get project list: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def search_issues(query: str, project_id: int = None, limit: int = 10) -> str:
    """
    Search issues (search keyword in title or description)
    
    Args:
        query: Search keyword
        project_id: Restrict search to specific project (optional)
        limit: Maximum number of results (default 10, max 50)
    
    Returns:
        List of issues matching search criteria
    """
    try:
        if not query.strip():
            return "Please provide a search keyword"
        
        client = get_client()
        limit = min(max(limit, 1), 50)
        
        # Set search parameters
        params = {
            'limit': limit * 3,  # Get more results for filtering
            'sort': 'updated_on:desc'
        }
        
        if project_id:
            params['project_id'] = project_id
        
        # Get issue list
        all_issues = client.list_issues(**params)
        
        # Filter by keyword locally (Redmine API does not have built-in search)
        query_lower = query.lower()
        matching_issues = []
        
        for issue in all_issues:
            if (query_lower in issue.subject.lower() or 
                (issue.description and query_lower in issue.description.lower())):
                matching_issues.append(issue)
                if len(matching_issues) >= limit:
                    break
        
        if not matching_issues:
            search_scope = f"Project {project_id}" if project_id else "all accessible projects"
            return f"No issues containing '{query}' found in {search_scope}"
        
        # Format result
        result = f"Search keyword: '{query}'\n"
        if project_id:
            result += f"Search scope: Project {project_id}\n"
        result += f"Found {len(matching_issues)} related issues:\n\n"
        
        result += f"{'ID':<8} {'Title':<35} {'Status':<12} {'Project':<15}\n"
        result += f"{'-'*8} {'-'*35} {'-'*12} {'-'*15}\n"
        
        for issue in matching_issues:
            title = issue.subject[:32] + "..." if len(issue.subject) > 35 else issue.subject
            status = issue.status.get('name', 'N/A')[:10]
            project_name = issue.project.get('name', 'N/A')[:13]
            
            result += f"{issue.id:<8} {title:<35} {status:<12} {project_name:<15}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to search issues: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def update_issue_content(issue_id: int, subject: str = None, description: str = None, 
                        priority_id: int = None, priority_name: str = None,
                        done_ratio: int = None, tracker_id: int = None, tracker_name: str = None,
                        parent_issue_id: int = None, remove_parent: bool = False, start_date: str = None, due_date: str = None,
                        estimated_hours: float = None) -> str:
    """
    Update issue content (title, description, priority, done ratio, tracker, dates, hours, etc.)
    
    Args:
        issue_id: Issue ID
        subject: New issue title (optional)
        description: New issue description (optional)
        priority_id: New priority ID (choose one with priority_name)
        priority_name: New priority name (choose one with priority_id)
        done_ratio: New completion percentage 0-100 (optional)
        tracker_id: New tracker ID (choose one with tracker_name)
        tracker_name: New tracker name (choose one with tracker_id)
        parent_issue_id: New parent issue ID (optional)
        remove_parent: Whether to remove parent issue relation (optional)
        start_date: New start date YYYY-MM-DD format (optional)
        due_date: New due date YYYY-MM-DD format (optional)
        estimated_hours: New estimated hours (optional)
    
    Returns:
        Update result message
    """
    try:
        client = get_client()
        
        # Prepare update data
        update_data = {}
        changes = []
        
        if subject is not None:
            update_data['subject'] = subject.strip()
            changes.append(f"Title: {subject}")
        
        if description is not None:
            update_data['description'] = description
            changes.append("Description updated")
        
        # Handle priority parameter
        if priority_name:
            priority_id = client.find_priority_id_by_name(priority_name)
            if not priority_id:
                return f"Priority name not found: \"{priority_name}\"\n\nAvailable priorities:\n" + "\n".join([f"- {name}" for name in client.get_available_priorities().keys()])
        
        if priority_id is not None:
            update_data['priority_id'] = priority_id
            changes.append(f"Priority ID: {priority_id}")
        
        if done_ratio is not None:
            if not (0 <= done_ratio <= 100):
                return "Error: Completion percentage must be between 0-100"
            update_data['done_ratio'] = done_ratio
            changes.append(f"Done ratio: {done_ratio}%")
        
        # Handle tracker parameter
        if tracker_name:
            tracker_id = client.find_tracker_id_by_name(tracker_name)
            if not tracker_id:
                return f"Tracker name not found: \"{tracker_name}\"\n\nAvailable trackers:\n" + "\n".join([f"- {name}" for name in client.get_available_trackers().keys()])
        
        if tracker_id is not None:
            update_data['tracker_id'] = tracker_id
            changes.append(f"Tracker ID: {tracker_id}")
        
        if remove_parent:
            update_data['parent_issue_id'] = None
            changes.append("Removed parent issue relation")
        elif parent_issue_id is not None:
            update_data['parent_issue_id'] = parent_issue_id
            changes.append(f"Parent issue ID: {parent_issue_id}")
        
        if start_date is not None:
            # Validate date format
            try:
                from datetime import datetime
                datetime.strptime(start_date, '%Y-%m-%d')
                update_data['start_date'] = start_date
                changes.append(f"Start date: {start_date}")
            except ValueError:
                return "Error: Start date format must be YYYY-MM-DD"
        
        if due_date is not None:
            # Validate date format
            try:
                from datetime import datetime
                datetime.strptime(due_date, '%Y-%m-%d')
                update_data['due_date'] = due_date
                changes.append(f"Due date: {due_date}")
            except ValueError:
                return "Error: Due date format must be YYYY-MM-DD"
        
        if estimated_hours is not None:
            if estimated_hours < 0:
                return "Error: Estimated hours cannot be negative"
            update_data['estimated_hours'] = estimated_hours
            changes.append(f"Estimated hours: {estimated_hours} hours")
        
        if not update_data and not changes:
            return "Error: Please provide at least one field to update"
        
        # Perform update
        client.update_issue(issue_id, **update_data)
        
        # Get updated issue info
        updated_issue = client.get_issue(issue_id)
        
        result = f"""Issue content updated successfully!

Issue: #{issue_id} - {updated_issue.subject}
Updated fields:
{chr(10).join(f"- {change}" for change in changes)}

Current status:
- Tracker: {updated_issue.tracker.get('name', 'N/A')}
- Status: {updated_issue.status.get('name', 'N/A')}
- Priority: {updated_issue.priority.get('name', 'N/A')}
- Done ratio: {updated_issue.done_ratio}%"""

        return result
        
    except RedmineAPIError as e:
        return f"Failed to update issue content: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def add_issue_note(issue_id: int, notes: str, private: bool = False, 
                   spent_hours: float = None, activity_name: str = None, 
                   activity_id: int = None, spent_on: str = None) -> str:
    """
    Add a note to an issue, can also log time
    
    Args:
        issue_id: Issue ID
        notes: Note content
        private: Whether the note is private (default no)
        spent_hours: Spent hours
        activity_name: Activity name (choose one with activity_id)
        activity_id: Activity ID (choose one with activity_name)
        spent_on: Log date YYYY-MM-DD format (optional, default today)
    
    Returns:
        Add result message
    """
    try:
        if not notes.strip():
            return "Error: Note content cannot be empty"
        
        client = get_client()
        time_entry_id = None
        
        # Handle time logging
        if spent_hours is not None:
            if spent_hours <= 0:
                return "Error: Spent hours must be greater than 0"
            
            # Handle activity parameter
            final_activity_id = activity_id
            if activity_name:
                final_activity_id = client.find_time_entry_activity_id_by_name(activity_name)
                if not final_activity_id:
                    available_activities = client.get_available_time_entry_activities()
                    return f"Time tracking activity name not found: \"{activity_name}\"\n\nAvailable activities:\n" + "\n".join([f"- {name}" for name in available_activities.keys()])
            
            if not final_activity_id:
                return "Error: Must provide activity_id or activity_name"
            
            # Create time entry
            try:
                time_entry_id = client.create_time_entry(
                    issue_id=issue_id,
                    hours=spent_hours,
                    activity_id=final_activity_id,
                    comments=notes.strip(),
                    spent_on=spent_on
                )
            except Exception as e:
                return f"Failed to create time entry: {str(e)}"
        
        # Prepare update data (add note)
        update_data = {'notes': notes.strip()}
        if private:
            update_data['private_notes'] = True
        
        # Perform update
        client.update_issue(issue_id, **update_data)
        
        # Get issue info
        issue = client.get_issue(issue_id)
        
        privacy_text = "Private" if private else "Public"
        result = f"""Note added successfully!

Issue: #{issue_id} - {issue.subject}
Note type: {privacy_text}
Note content:
{notes.strip()}"""

        # If time entry created, add info
        if time_entry_id:
            from datetime import date
            actual_date = spent_on if spent_on else date.today().strftime('%Y-%m-%d')
            activity_name_display = activity_name if activity_name else f"ID {final_activity_id}"
            result += f"""

Time entry added successfully!
- Time entry ID: {time_entry_id}
- Spent hours: {spent_hours} hours
- Activity: {activity_name_display}
- Log date: {actual_date}"""

        return result
        
    except RedmineAPIError as e:
        return f"Failed to add issue note: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def assign_issue(issue_id: int, user_id: int = None, user_name: str = None, user_login: str = None, notes: str = "") -> str:
    """
    Assign issue to user
    
    Args:
        issue_id: Issue ID
        user_id: User ID to assign (choose one with user_name/user_login)
        user_name: User name to assign (choose one with user_id/user_login)
        user_login: User login to assign (choose one with user_id/user_name)
        notes: Assignment notes (optional)
    
    Returns:
        Assignment result message
    """
    try:
        client = get_client()
        
        # Handle user parameter
        final_user_id = user_id
        if user_name:
            final_user_id = client.find_user_id_by_name(user_name)
            if not final_user_id:
                users = client.get_available_users()
                return f"User name not found: \"{user_name}\"\n\nAvailable users (name):\n" + "\n".join([f"- {name}" for name in users['by_name'].keys()])
        elif user_login:
            final_user_id = client.find_user_id_by_login(user_login)
            if not final_user_id:
                users = client.get_available_users()
                return f"User login not found: \"{user_login}\"\n\nAvailable users (login):\n" + "\n".join([f"- {login}" for login in users['by_login'].keys()])
        
        # Prepare update data
        update_data = {}
        
        if final_user_id is not None:
            update_data['assigned_to_id'] = final_user_id
            action_text = f"Assigned to user ID {final_user_id}"
        else:
            update_data['assigned_to_id'] = None
            action_text = "Unassigned"
        
        if notes.strip():
            update_data['notes'] = notes.strip()
        
        # Perform update
        client.update_issue(issue_id, **update_data)
        
        # Get updated issue info
        updated_issue = client.get_issue(issue_id)
        
        assignee_name = "Unassigned"
        if updated_issue.assigned_to:
            assignee_name = updated_issue.assigned_to.get('name', f"User ID {user_id}")
        
        result = f"""Issue assignment updated successfully!

Issue: #{issue_id} - {updated_issue.subject}
Action: {action_text}
Currently assigned to: {assignee_name}"""

        if notes.strip():
            result += f"\nNotes: {notes}"

        return result
        
    except RedmineAPIError as e:
        return f"Failed to assign issue: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def create_new_issue(project_id: int, subject: str, description: str = "", 
                    tracker_id: int = None, tracker_name: str = None,
                    priority_id: int = None, priority_name: str = None,
                    assigned_to_id: int = None, assigned_to_name: str = None, assigned_to_login: str = None) -> str:
    """
    Create a new Redmine issue
    
    Args:
        project_id: Project ID
        subject: Issue title
        description: Issue description (optional)
        tracker_id: Tracker ID (choose one with tracker_name)
        tracker_name: Tracker name (choose one with tracker_id)
        priority_id: Priority ID (choose one with priority_name)
        priority_name: Priority name (choose one with priority_id)
        assigned_to_id: User ID to assign (choose one with assigned_to_name/assigned_to_login)
        assigned_to_name: User name to assign (choose one with assigned_to_id/assigned_to_login)
        assigned_to_login: User login to assign (choose one with assigned_to_id/assigned_to_name)
    
    Returns:
        Creation result message
    """
    try:
        if not subject.strip():
            return "Error: Issue title cannot be empty"
        
        client = get_client()
        
        # Handle tracker parameter
        final_tracker_id = tracker_id
        if tracker_name:
            final_tracker_id = client.find_tracker_id_by_name(tracker_name)
            if not final_tracker_id:
                return f"Tracker name not found: \"{tracker_name}\"\n\nAvailable trackers:\n" + "\n".join([f"- {name}" for name in client.get_available_trackers().keys()])
        
        # Handle priority parameter
        final_priority_id = priority_id
        if priority_name:
            final_priority_id = client.find_priority_id_by_name(priority_name)
            if not final_priority_id:
                return f"Priority name not found: \"{priority_name}\"\n\nAvailable priorities:\n" + "\n".join([f"- {name}" for name in client.get_available_priorities().keys()])
        
        # Handle assigned user parameter
        final_assigned_to_id = assigned_to_id
        if assigned_to_name:
            final_assigned_to_id = client.find_user_id_by_name(assigned_to_name)
            if not final_assigned_to_id:
                users = client.get_available_users()
                return f"User name not found: \"{assigned_to_name}\"\n\nAvailable users (name):\n" + "\n".join([f"- {name}" for name in users['by_name'].keys()])
        elif assigned_to_login:
            final_assigned_to_id = client.find_user_id_by_login(assigned_to_login)
            if not final_assigned_to_id:
                users = client.get_available_users()
                return f"User login not found: \"{assigned_to_login}\"\n\nAvailable users (login):\n" + "\n".join([f"- {login}" for login in users['by_login'].keys()])
        
        # Create issue
        new_issue_id = client.create_issue(
            project_id=project_id,
            subject=subject.strip(),
            description=description,
            tracker_id=final_tracker_id,
            priority_id=final_priority_id,
            assigned_to_id=final_assigned_to_id
        )
        
        # Get created issue info
        new_issue = client.get_issue(new_issue_id)
        
        result = f"""New issue created successfully!

Issue ID: #{new_issue_id}
Title: {new_issue.subject}
Project: {new_issue.project.get('name', 'N/A')}
Tracker: {new_issue.tracker.get('name', 'N/A')}
Status: {new_issue.status.get('name', 'N/A')}
Priority: {new_issue.priority.get('name', 'N/A')}
Assigned to: {new_issue.assigned_to.get('name', 'Unassigned') if new_issue.assigned_to else 'Unassigned'}"""

        if description:
            result += f"\n\nDescription:\n{description}"

        return result
        
    except RedmineAPIError as e:
        return f"Failed to create issue: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def get_my_issues(status_filter: str = "open", limit: int = 20) -> str:
    """
    Get list of issues assigned to me
    
    Args:
        status_filter: Status filter ("open", "closed", "all")
        limit: Maximum number of results (default 20, max 100)
    
    Returns:
        My issue list
    """
    try:
        client = get_client()
        
        # Get current user info
        current_user = client.get_current_user()
        user_id = current_user['id']
        user_name = current_user.get('firstname', '') + ' ' + current_user.get('lastname', '')
        
        # Restrict limit range
        limit = min(max(limit, 1), 100)
        
        # Set query parameters
        params = {
            'assigned_to_id': user_id,
            'limit': limit,
            'sort': 'updated_on:desc'
        }
        
        # Handle status filter
        if status_filter == "open":
            params['status_id'] = 'o'  # Redmine API uses 'o' for open status
        elif status_filter == "closed":
            params['status_id'] = 'c'  # Redmine API uses 'c' for closed status
        
        # Get issue list
        issues = client.list_issues(**params)
        
        if not issues:
            return f"No {status_filter} issues assigned to {user_name.strip()} found"
        
        # Format result
        result = f"""Issues assigned to {user_name.strip()}:
Status filter: {status_filter}
Found {len(issues)} issues:

{"ID":<8} {"Title":<35} {"Project":<15} {"Status":<12} {"Updated":<10}
{"-"*8} {"-"*35} {"-"*15} {"-"*12} {"-"*10}"""

        for issue in issues:
            title = issue.subject[:32] + "..." if len(issue.subject) > 35 else issue.subject
            project_name = issue.project.get('name', 'N/A')[:13]
            status = issue.status.get('name', 'N/A')[:10]
            updated = issue.updated_on[:10] if issue.updated_on else 'N/A'
            
            result += f"\n{issue.id:<8} {title:<35} {project_name:<15} {status:<12} {updated:<10}"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to get my issues: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def close_issue(issue_id: int, notes: str = "", done_ratio: int = 100) -> str:
    """
    Close issue (set to completed status)
    
    Args:
        issue_id: Issue ID
        notes: Closing notes (optional)
        done_ratio: Completion percentage (default 100%)
    
    Returns:
        Close result message
    """
    try:
        client = get_client()
        
        # Get available status list, find closed status
        statuses = client.get_issue_statuses()
        closed_status_id = None
        
        for status in statuses:
            if status.get('is_closed', False):
                closed_status_id = status['id']
                break
        
        if closed_status_id is None:
            return "Error: No available closed status found"
        
        # Prepare update data
        update_data = {
            'status_id': closed_status_id,
            'done_ratio': min(max(done_ratio, 0), 100)
        }
        
        if notes.strip():
            update_data['notes'] = notes.strip()
        
        # Perform update
        client.update_issue(issue_id, **update_data)
        
        # Get updated issue info
        updated_issue = client.get_issue(issue_id)
        
        result = f"""Issue closed successfully!

Issue: #{issue_id} - {updated_issue.subject}
Status: {updated_issue.status.get('name', 'N/A')}
Done ratio: {updated_issue.done_ratio}%"""

        if notes.strip():
            result += f"\nClosing notes: {notes}"

        return result
        
    except RedmineAPIError as e:
        return f"Failed to close issue: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def search_users(query: str, limit: int = 10) -> str:
    """
    Search users (by name or login)
    
    Args:
        query: Search keyword (name or login)
        limit: Maximum number of results (default 10, max 50)
    
    Returns:
        List of users matching search criteria
    """
    try:
        if not query.strip():
            return "Please provide a search keyword"
        
        client = get_client()
        limit = min(max(limit, 1), 50)
        
        users = client.search_users(query, limit)
        
        if not users:
            return f"No users matching \"{query}\" found"
        
        result = f"Search keyword: '{query}'\nFound {len(users)} related users:\n\n"
        result += f"{'ID':<5} {'Login':<15} {'Name':<20} {'Status':<8}\n"
        result += f"{'-'*5} {'-'*15} {'-'*20} {'-'*8}\n"
        
        for user in users:
            full_name = f"{user.firstname} {user.lastname}".strip()
            if not full_name:
                full_name = user.login
            status_text = "Enabled" if user.status == 1 else "Disabled"
            result += f"{user.id:<5} {user.login:<15} {full_name:<20} {status_text:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to search users: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def list_users(limit: int = 20, status_filter: str = "active") -> str:
    """
    List all users
    
    Args:
        limit: Maximum number of results (default 20, max 100)
        status_filter: Status filter ("active", "locked", "all")
    
    Returns:
        User list in table format
    """
    try:
        client = get_client()
        limit = min(max(limit, 1), 100)
        
        # Convert status filter
        status = None
        if status_filter == "active":
            status = 1
        elif status_filter == "locked":
            status = 3
        
        users = client.list_users(limit=limit, status=status)
        
        if not users:
            return "No users found"
        
        result = f"Found {len(users)} users:\n\n"
        result += f"{'ID':<5} {'Login':<15} {'Name':<20} {'Email':<25} {'Status':<8}\n"
        result += f"{'-'*5} {'-'*15} {'-'*20} {'-'*25} {'-'*8}\n"
        
        for user in users:
            full_name = f"{user.firstname} {user.lastname}".strip()
            if not full_name:
                full_name = user.login
            status_text = "Enabled" if user.status == 1 else "Disabled"
            email = user.mail[:22] + "..." if len(user.mail) > 25 else user.mail
            result += f"{user.id:<5} {user.login:<15} {full_name:<20} {email:<25} {status_text:<8}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to get user list: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def get_user(user_id: int) -> str:
    """
    Get detailed information for a specific user
    
    Args:
        user_id: User ID
        
    Returns:
        Detailed user information in a readable format
    """
    try:
        client = get_client()
        user_data = client.get_user(user_id)
        
        # Format user info
        result = f"User #{user_id}: {user_data.get('firstname', '')} {user_data.get('lastname', '')}\n\n"
        result += "Basic Info:\n"
        result += f"- Login: {user_data.get('login', 'N/A')}\n"
        result += f"- Email: {user_data.get('mail', 'N/A')}\n"
        result += f"- Status: {'Enabled' if user_data.get('status', 1) == 1 else 'Disabled'}\n"
        result += f"- Created on: {user_data.get('created_on', 'N/A')}\n"
        
        if user_data.get('last_login_on'):
            result += f"- Last login: {user_data.get('last_login_on')}\n"
        
        # Group info
        if user_data.get('groups'):
            result += "\nGroups:\n"
            for group in user_data['groups']:
                result += f"- {group.get('name', 'N/A')}\n"
        
        # Custom fields
        if user_data.get('custom_fields'):
            result += "\nCustom fields:\n"
            for field in user_data['custom_fields']:
                if field.get('value'):
                    result += f"- {field.get('name', 'N/A')}: {field.get('value', 'N/A')}\n"
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to get user info: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


@mcp.tool()
def refresh_cache() -> str:
    """
    Manually refresh enum and user cache
    
    Returns:
        Refresh result message
    """
    try:
        client = get_client()
        client.refresh_cache()
        
        # Get cache info
        cache = client._load_enum_cache()
        domain = cache.get('domain', 'N/A')
        cache_time = cache.get('cache_time', 0)
        
        if cache_time > 0:
            cache_datetime = datetime.fromtimestamp(cache_time).strftime('%Y-%m-%d %H:%M:%S')
        else:
            cache_datetime = 'N/A'
        
        result = f"""Cache refreshed successfully!

Domain: {domain}
Cache time: {cache_datetime}

Cache content statistics:
- Priorities: {len(cache.get('priorities', {}))}
- Statuses: {len(cache.get('statuses', {}))}  
- Trackers: {len(cache.get('trackers', {}))}
- Users (name): {len(cache.get('users_by_name', {}))}
- Users (login): {len(cache.get('users_by_login', {}))}

Cache location: {client._cache_file}"""
        
        return result
        
    except RedmineAPIError as e:
        return f"Failed to refresh cache: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"


def main():
    """MCP server main entry point"""
    # Run server via stdio
    mcp.run('stdio')


if __name__ == "__main__":
    main()
