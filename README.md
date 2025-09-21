# CodeMate - System Monitoring and File Management Tool

A comprehensive system monitoring and file management tool with a web interface and API endpoints. Built with Python, Flask, and Streamlit.

## 🌟 Features

### System Monitoring
- Real-time CPU usage tracking
- Memory usage statistics
- Disk space monitoring
- Process management

### File Operations
- Basic file operations (create, read, update, delete)
- Directory navigation and management
- Path safety and workspace isolation
- Secure command execution

### Web Interface
- Streamlit-based user interface
- Interactive command terminal
- Real-time system stats display
- Natural language command processing

## 🚀 Live Deployments

### API Endpoints
Base URL: `https://code-mate-hack-im51txm1m-hiiihimanshus-projects.vercel.app`

Available endpoints:
- `/` - API status and endpoint list
- `/api/system/status` - Overall system status
- `/api/system/memory` - Detailed memory information
- `/api/system/disk` - Disk usage statistics

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **Frontend**: Streamlit
- **Monitoring**: psutil
- **Deployment**: Vercel
- **Version Control**: GitHub

## Safety Model

This application implements a multi-layered safety model:

1. **Workspace Jail**: All file operations are confined to a designated workspace root directory
2. **Command Whitelisting**: Only approved commands can be executed in read-only mode
3. **Dangerous Command Blocking**: Commands like `rm`, `sudo`, `curl`, etc. are blocked entirely
4. **Path Validation**: All paths are validated to ensure they don't escape the workspace
5. **Subprocess Sandboxing**: When enabled, subprocesses are executed with security restrictions

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Environment Variables

- `WORKSPACE_ROOT`: Directory that serves as the root for all file operations (default: `./workspace`)
- `READONLY_MODE`: Enable read-only mode to prevent destructive operations (default: `false`)
- `ALLOW_SUBPROCESS`: Enable subprocess execution (default: `false`)

## Deployment (Streamlit Community Cloud)

To deploy to Streamlit Community Cloud:

1. Push your code to a GitHub repository
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Set the following secrets in your Streamlit app settings (optional):
   - `WORKSPACE_ROOT`: `/app/workspace` (for Streamlit deployment)
   - `READONLY_MODE`: `true` (recommended for security)
   - `ALLOW_SUBPROCESS`: `false` (recommended for security)

### Deployment Hints

- A default `WORKSPACE_ROOT` directory (`./workspace`) will be created automatically at app startup if it doesn't exist
- Streamlit secrets are not required unless you want to customize the default behavior
- The application will boot without any local state - all state is managed through the workspace directory

### Deploy Checklist

- [ ] Ensure `./workspace` directory exists or will be created automatically
- [ ] Verify app starts successfully with `streamlit run app.py`
- [ ] Test basic commands work without local state
- [ ] Confirm workspace isolation is functioning
- [ ] Validate read-only mode can be enabled via environment variable
- [ ] Check that subprocess execution is disabled by default
- [ ] Test that the healthcheck command shows up in startup logs

## Demo Script Checklist for Judges

- [ ] Start the application with `streamlit run app.py`
- [ ] Verify that the workspace root is set correctly
- [ ] Test basic commands like `ls`, `pwd`, `echo`
- [ ] Test help system with `help` and `help ls`
- [ ] Test command history with `history`
- [ ] Test error handling with invalid commands
- [ ] Test argument validation
- [ ] Demonstrate workspace isolation by attempting to access files outside workspace
- [ ] Demonstrate dangerous command blocking
- [ ] Test read-only mode by setting `READONLY_MODE=true`
- [ ] Show execution timing in command responses
