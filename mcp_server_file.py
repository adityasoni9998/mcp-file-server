import os
from pathlib import Path
import json
import asyncio
from typing import Dict, Any, List, Optional
import shutil
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "file-server",
    description="MCP server to interact with file system",
    host="0.0.0.0",
    port=8080
)

# check if path is absolute and exists
def validate_path(path: str) -> str:
    """Validate that the given path is absolute and exists."""
    if not os.path.isabs(path):
        return f"Error: Path must be absolute: {path}"
    if not os.path.exists(path):
        return f"Error: Path does not exist: {path}"
    return ""
    

# All paths given to the server must be absolute paths
@mcp.tool()
async def list_files(path: str) -> str:
    """List all files in the specified directory.
    Args:
        path: Absolute path to the directory to list files from.
    """
    path = os.path.normpath(path)
    is_valid = validate_path(path)
    if len(is_valid) > 0:
        return "Error: " + is_valid
    if not os.path.isdir(path):
        return f"Error: Path is not a directory: {path}"
    
    # Security check to prevent directory traversal
    try:
        files = os.listdir(path)
        file_info = []
        
        for file in files:
            full_path = os.path.join(path, file)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else "-"
            file_type = "directory" if is_dir else "file"

            file_info.append({
                "file-path": full_path,
                "type": file_type,
                "size": size
            })        
        return json.dumps(file_info, indent=4)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def read_file(path: str) -> str:
    """Read the contents of a file.

    Args:
        path: Absolute path to the file to read.
    """
    path = os.path.normpath(path)
    is_valid = validate_path(path)
    if len(is_valid) > 0:
        return "Error: " + is_valid
    if not os.path.isfile(path):
        return f"Error: File does not exist or is not a file: {path}"    
    try:
        with open(path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
async def write_file(path: str, content: str) -> str:
    """Write content to a file.

    Args:
        path: Absolute path to the file to write content to.
        content: Content to write to the file
    """
    path = os.path.normpath(path)
    if not os.path.isabs(path):
        return f"Error: Path must be absolute: {path}"
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w') as f:
            f.write(content)
        
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@mcp.tool()
async def delete_file(path: str) -> str:
    """Delete a file or a directory.
    
    Args:
        path: Absolute path of the file/directory to delete.
    """
    path = os.path.normpath(path)
    is_valid = validate_path(path)
    if len(is_valid) > 0:
        return "Error: " + is_valid    
    try:
        if not os.path.exists(path):
            return f"Error: File does not exist: {path}"
        
        if os.path.isdir(path):
            shutil.rmtree(path)
            return f"Successfully deleted directory: {path}"
        else:
            os.remove(path)
            return f"Successfully deleted file: {path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

async def main():
    await mcp.run_sse_async()
    
if __name__ == "__main__":
    asyncio.run(main())
