# Redmine MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Redmine integration, enabling Claude Code to directly interact with Redmine project management systems.

## 🚀 Features

### ✅ Issue Management
- **Query Issues**: Get detailed issue information and lists
- **Create Issues**: Create new issues and set related attributes
- **Update Issues**: Modify issue content, status, priority, etc.
- **Assign Issues**: Assign or unassign issues to specific users
- **Add Notes**: Add public or private notes to issues
- **Close Issues**: Automatically set issues to completed status

### ✅ Project Management
- **Project Lists**: Get accessible project lists
- **Project Issues**: Filter by status and list all issues in projects

### ✅ Search Features
- **Keyword Search**: Search for keywords in issue titles and descriptions
- **My Issues**: Quick view of issues assigned to current user

### ✅ System Tools
- **Health Check**: Verify MCP server and Redmine connection status
- **Status Query**: Get available issue status lists

## 📋 System Requirements

- **Python**: 3.12 or higher
- **Redmine**: Version with REST API support (recommended 4.0+)
- **Package Manager**: [uv](https://docs.astral.sh/uv/) or pip

## 🔧 Installation & Setup

### 1. Clone the Project

```bash
git clone https://github.com/snowild/redmine-mcp.git
cd redmine-mcp
```

### 2. Install Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

### 3. Environment Configuration

Create a `.env` file:
```bash
cp .env.example .env
```

Edit the `.env` file and set the following environment variables:
```env
REDMINE_DOMAIN=https://your-redmine-domain.com
REDMINE_API_KEY=your_api_key_here

# Project-specific variables (avoid conflicts with other projects)
REDMINE_MCP_LOG_LEVEL=INFO
REDMINE_MCP_TIMEOUT=30

# Backward compatibility variables (fallback)
REDMINE_TIMEOUT=30
LOG_LEVEL=info
```

#### Environment Variables Reference

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REDMINE_DOMAIN` | Redmine server URL | *Required* | `https://redmine.example.com` |
| `REDMINE_API_KEY` | Your Redmine API key | *Required* | `abc123...` |
| `REDMINE_MCP_LOG_LEVEL` | Log level for this MCP server | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `REDMINE_MCP_TIMEOUT` | Request timeout (seconds) | `30` | `60` |
| `LOG_LEVEL` | Legacy log level (backward compatibility) | - | `debug`, `info` |
| `REDMINE_TIMEOUT` | Legacy timeout (backward compatibility) | - | `30` |

**Log Level Priority:**
1. `REDMINE_MCP_LOG_LEVEL` (highest priority - project-specific)
2. `LOG_LEVEL` (backward compatibility)
3. `INFO` (default if neither is set)

> **Note**: The system automatically handles case conversion and ensures FastMCP compatibility.

### 4. Redmine API Setup

#### 4.1 Enable REST API
1. Log in to Redmine as administrator
2. Go to **Administration** → **Settings** → **API**
3. Check **"Enable REST web service"**
4. Click **Save**

#### 4.2 Configure Redmine Basic Data (Administrator)
Before using MCP tools, you need to configure Redmine's basic data:

**Configure Roles and Permissions**
1. Go to **Administration** → **Roles and permissions**
2. Create or edit roles (e.g.: Developer, Tester, Project Manager)
3. Assign appropriate permissions to roles (recommend at least: View issues, Add issues, Edit issues)

**Configure Trackers**
1. Go to **Administration** → **Trackers**
2. Create tracker types (e.g.: Bug, Feature, Support)
3. Set default status and workflow for each tracker

**Configure Issue Statuses**
1. Go to **Administration** → **Issue statuses**
2. Create statuses (e.g.: New, In Progress, Resolved, Closed, Rejected)
3. Set status attributes (whether it's a closed status, etc.)

**Configure Workflow**
1. Go to **Administration** → **Workflow**
2. Set allowed status transitions for each role and tracker combination
3. Ensure basic status transition paths (New → In Progress → Resolved → Closed)

**Create Projects**
1. Go to **Projects** → **New project**
2. Set project name, identifier, description
3. Select enabled modules (at least enable "Issue tracking")
4. Assign members and set roles

#### 4.3 Get API Key
1. Log in to your Redmine system (can be administrator or regular user)
2. Go to **My account** → **API access key**
3. Click **Show** or **Reset** to get the API key
4. Copy the key to `REDMINE_API_KEY` in the `.env` file

> **⚠️ Important Notes**: 
> - If you can't find the API key option, please ensure step 4.1 (Enable REST API) is completed
> - Complete basic setup before you can properly create and manage issues
> 
> **📚 Detailed Setup Guide**: For complete Redmine setup steps, please refer to [Redmine Complete Setup Guide](docs/manuals/redmine_setup_guide.md)

## 🔗 Claude Code Integration

### Install to Claude Code

```bash
# Install from local
uv tool install .

# Or using pip
pip install .

# Add to Claude Code MCP configuration
claude mcp add redmine "redmine-mcp" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here"
```

### Verify Installation

```bash
# Test MCP server
uv run python -m redmine_mcp.server

# Test Claude Code integration
uv run python tests/scripts/claude_integration.py
```

## 🔄 Updating/Reinstalling MCP

If you need to update to the latest version of the MCP server or reinstall it:

### 1. Remove Previous Installation

```bash
# Remove from Claude Code
claude mcp remove redmine

# Uninstall the package (if installed with uv tool)
uv tool uninstall redmine-mcp

# Or if installed with pip
pip uninstall redmine-mcp
```

### 2. Install Latest Version

```bash
# Navigate to project directory
cd /path/to/redmine-mcp

# Pull latest changes (if from git)
git pull origin main

# Install latest version
uv tool install .

# Or using pip
pip install .
```

### 3. Re-register with Claude Code

```bash
claude mcp add redmine "redmine-mcp" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here" \
  -e REDMINE_MCP_LOG_LEVEL="INFO" \
  -e REDMINE_MCP_TIMEOUT="30"
```

### 4. Verify Updated Installation

```bash
# Verify MCP registration
claude mcp list

# Or test directly
uv run python -m redmine_mcp.server --help
```

> **Important Notes:**
> - Environment variable names have been updated for better project isolation
> - Now supports both `REDMINE_MCP_LOG_LEVEL` (preferred) and `LOG_LEVEL` (backward compatibility)
> - Log level handling is now more robust with automatic case conversion and FastMCP compatibility

## 🛠️ Available MCP Tools

### Basic Tools
| Tool Name | Description |
|-----------|-------------|
| `server_info` | Display server information and configuration status |
| `health_check` | Check server and Redmine connection health status |

### Issue Operations
| Tool Name | Description |
|-----------|-------------|
| `get_issue` | Get detailed information of specified issue |
| `create_new_issue` | Create a new issue |
| `update_issue_status` | Update issue status |
| `update_issue_content` | Update issue content (title, description, etc.) |
| `add_issue_note` | Add notes to issues |
| `assign_issue` | Assign or unassign issues |
| `close_issue` | Close issue and set completion rate |

### Query Tools
| Tool Name | Description |
|-----------|-------------|
| `list_project_issues` | List issues in projects |
| `get_my_issues` | Get list of issues assigned to me |
| `search_issues` | Search for issues containing keywords |
| `get_projects` | Get list of accessible projects |
| `get_issue_statuses` | Get all available issue statuses |
| `get_trackers` | Get all available tracker lists |
| `get_priorities` | Get all available issue priorities |
| `get_time_entry_activities` | Get all available time tracking activities |
| `get_document_categories` | Get all available document categories |

## 💡 Usage Examples

### Using in Claude Code

```
# Check server status
Please run health check

# Get project list
Show all accessible projects

# View system settings
Get all available issue statuses
Get all available tracker lists
Get all available issue priorities
Get all available time tracking activities
Get all available document categories

# View specific issue
Get detailed information for issue #123

# Create new issue
Create an issue in project ID 1:
- Title: Fix login error
- Description: Users cannot log in to the system properly
- Priority: High

# Search issues
Search for issues containing "login" keyword

# Update issue status
Update issue #123 status to "In Progress" with note "Starting to handle this issue"
```

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
uv run python -m pytest

# Run MCP integration tests
uv run python tests/scripts/mcp_integration.py

# Run Claude Code integration tests  
uv run python tests/scripts/claude_integration.py
```

### Docker Environment Testing

If you want to test in a local Docker environment:

```bash
# Start Redmine test environment
docker-compose up -d

# Quick start complete test environment
./quick_start.sh
```

## 🔍 Troubleshooting

### Common Issues

**1. API Authentication Failed (401/403 errors)**
- Verify API key is correct
- **Check if Redmine has REST API enabled**: Go to `Administration` → `Settings` → `API`, check "Enable REST web service"
- Verify user permissions are sufficient
- Check if URL is correct (including http/https and port)

**2. Connection Timeout**
- Check network connection
- Adjust `REDMINE_TIMEOUT` environment variable
- Verify Redmine server status

**3. Issue Creation Failed**
- Verify project exists and has permissions
- Check if required fields are filled
- Verify tracker and status settings
- **Check basic data configuration**: Ensure roles, trackers, statuses, and workflow setup is complete
- Verify user has appropriate role and permissions in the project

**4. Status Update Failed**
- Check if workflow allows the status transition
- Verify user role has permission to change status
- Verify target status ID is correct

**5. Project or Issue Not Found**
- Verify ID is correct
- Check if user has permission to view the project/issue
- Verify project status is active

### Debug Mode

Enable debug mode for more detailed error information:

```env
DEBUG_MODE=true
```

## 📁 Project Structure

```
redmine-mcp/
├── src/redmine_mcp/          # Main source code
│   ├── __init__.py           # Package initialization
│   ├── server.py             # MCP server main program
│   ├── redmine_client.py     # Redmine API client
│   ├── config.py             # Configuration management
│   └── validators.py         # Data validation
├── tests/                    # Test files
├── docs/                     # Documentation directory
├── docker-compose.yml        # Docker test environment
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

## 🤝 Contributing

1. Fork this project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Code](https://claude.ai/code)
- [Redmine](https://www.redmine.org/)
- [FastMCP](https://github.com/jlowin/fastmcp)

---

If you have any questions or suggestions, feel free to open an Issue or contact the project maintainers.