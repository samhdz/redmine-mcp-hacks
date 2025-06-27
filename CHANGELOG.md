# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2025-06-27

### Fixed
- **Documentation Accuracy**: Corrected Claude MCP verification commands
  - Replaced invalid `claude mcp test redmine` with `claude mcp list`
  - Added `/mcp` slash command as alternative verification method in Claude Code
  - Improved installation verification instructions

## [0.3.0] - 2025-06-27

### Added
- 📋 **Environment Variables Reference Table** - Comprehensive documentation of all configuration options
- 🔄 **Reinstallation Guide** - Complete step-by-step instructions for updating MCP server
- 🔧 **Enhanced Log Level Management** - Support for both project-specific and legacy environment variables
- ⚡ **FastMCP Compatibility** - Automatic case conversion and synchronization with FastMCP log levels

### Changed
- **Environment Variable Priority System**: 
  1. `REDMINE_MCP_LOG_LEVEL` (highest priority - project-specific)
  2. `LOG_LEVEL` (backward compatibility)
  3. `INFO` (default)
- **Configuration Loading Order**: Ensure configuration loads before FastMCP initialization
- **Documentation Structure**: Added dedicated updating section and improved environment variable docs

### Fixed
- **FastMCP Startup Errors**: Resolved case sensitivity issues with log level environment variables
- **Configuration Race Condition**: Fixed issue where FastMCP read environment variables before they were properly set
- **Log Level Validation**: Improved error messages for invalid log level values

### Technical Improvements
- Enhanced config.py with robust log level resolution logic
- Improved server.py initialization sequence
- Better error handling and validation
- Backward compatibility maintained for existing installations

## [0.2.0] - 2025-06-27

### Added
- 🎯 **Time Tracking Support** - Record working hours when adding issue notes
- 🏗️ **Parent-Child Issue Relationships** - Full support for issue hierarchies
- 🎯 **Name Parameter Support** - Use names instead of IDs for priorities, statuses, trackers
- 🧠 **Smart Caching System** - Multi-domain cache with automatic refresh
- 👥 **Enhanced User Management** - Search and manage users by name/login
- ⚡ **Cache Refresh Tool** - Manual cache refresh with statistics

### Enhanced Features
- **Name-based Parameters**: All major tools now support name parameters
  - Priority names (e.g., "High", "Normal", "Low")
  - Status names (e.g., "In Progress", "Resolved")
  - Tracker names (e.g., "Bug", "Feature", "Support")
  - User names and login names
- **Time Logging**: `add_issue_note` now supports time tracking
  - Activity names and IDs
  - Flexible date specification
  - Private/public note options
- **Intelligent Error Messages**: Show available options when invalid names provided

### Technical Improvements
- Multi-domain cache file support (`~/.redmine_mcp/cache_{domain}_{hash}.json`)
- 24-hour automatic cache refresh
- Comprehensive helper functions for ID lookups
- Enhanced environment variable configuration

## [0.1.0] - 2025-06-26

### Added
- 🎉 **Initial Release** of Redmine MCP Server
- ✅ **Complete MCP Server Architecture** implementation
- 🔧 **22 Core MCP Tools** for comprehensive Redmine integration
- 📋 **Issue Management Features**
  - `get_issue` - Get detailed issue information
  - `create_new_issue` - Create new issues
  - `update_issue_status` - Update issue status
  - `update_issue_content` - Update issue content
  - `add_issue_note` - Add issue notes
  - `assign_issue` - Assign/unassign issues
  - `close_issue` - Close issues
- 🗂️ **Project Management Features**
  - `get_projects` - Get project lists
  - `list_project_issues` - List project issues
  - `get_issue_statuses` - Get issue statuses
  - `get_trackers` - Get tracker lists
  - `get_priorities` - Get priority lists
  - `get_time_entry_activities` - Get time tracking activities
  - `get_document_categories` - Get document categories
- 👥 **User Management Features**
  - `search_users` - Search users by name/login
  - `list_users` - List all users
  - `get_user` - Get user details
- 🔍 **Search Features**
  - `search_issues` - Search issues by keywords
  - `get_my_issues` - Get issues assigned to current user
- 🔧 **System Tools**
  - `server_info` - Display server information
  - `health_check` - Health check and diagnostics
  - `refresh_cache` - Manual cache refresh
- 🔐 **Complete Authentication and Permission Management**
- 🛡️ **Data Validation and Error Handling**
- 🐳 **Docker Test Environment Support**
- 🧪 **Comprehensive Test Suite** (100% test coverage)
- 📚 **Complete Documentation and Usage Guidelines**
- 🔗 **Claude Code Integration Support**

### Technical Implementation
- Built with FastMCP framework
- Python 3.12+ support
- UV package manager integration
- Complete Redmine REST API client
- Environment variable configuration management
- User-friendly error messages and interface

### Documentation
- 📖 README.md - Project overview and quick start guide
- 🚀 Installation and setup instructions
- 💡 Usage examples and best practices
- 📋 Complete tool reference
- 🧪 Testing guides and examples

### Compatibility
- Redmine 4.0+ (recommended 5.0+)
- Claude Code MCP integration
- Cross-platform support (Windows, macOS, Linux)

---

## Version Format Guidelines

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security-related changes

[Unreleased]: https://github.com/snowild/redmine-mcp/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/snowild/redmine-mcp/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/snowild/redmine-mcp/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/snowild/redmine-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/snowild/redmine-mcp/releases/tag/v0.1.0