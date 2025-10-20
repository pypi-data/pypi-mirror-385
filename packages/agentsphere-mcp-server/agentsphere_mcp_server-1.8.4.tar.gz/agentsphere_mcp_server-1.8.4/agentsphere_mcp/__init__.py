"""AgentSphere STDIO MCP Server

an MCP Server designed for AI to connect and operate agent-sphere sandboxes.

- MCP Tools Description

This MCP Server provides the following 11 tools for AI usage:
1. exec_command: execute Linux system commands in the sandbox
2. get_preview_link: get the access URL for web services in the sandbox
3. upload_files_to_sandbox: upload local files or folders to a specified directory in the sandbox
4. find_file_path: search for files or directories by name and return their absolute paths
5. sandbox_create: create a new sandbox instance without reusing existing ones
6. sandbox_is_running: check if a specific sandbox is running and get its status
7. file_read: read file content from a sandbox by sandbox_id and file path
8. sandbox_file_write: write content to a file in a sandbox by sandbox_id and file path
9. sandbox_mkdir: create a directory in a sandbox (like mkdir -p) by sandbox_id and path
10. sandbox_list_dir: list directory entries in a sandbox (like ls -al) by sandbox_id and path
11. sandbox_dir_exist: check if a file or directory exists in a sandbox by sandbox_id and path

- Usage: MCP Server Configuration

To configure this server in Efflux, Cursor, or other MCP clients, add the following configuration to your MCP configuration file:

```json
{
  "mcpServers": {
    "agentsphere": {
      "command": "uvx",
      "args": ["agentsphere-mcp-server"],
      "env": {
        "AGENTSPHERE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```
"""

__version__ = "1.8.4"
