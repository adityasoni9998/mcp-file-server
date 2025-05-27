import asyncio
from typing import Dict, Any, List, Optional
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "unix-shell",
    description="MCP server to interact with a Unix shell",
    host="0.0.0.0",
    port=8081
)

@mcp.tool()
def execute_command(command: str) -> str:
    """Execute a shell command and return the result"""
    print(f"Executing command: {command} in shell.")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30 # Timeout after 30 seconds
        )
        return f"Command output: {result.stdout + result.stderr}"
    except Exception as e:
        return f"Command execution failed: {str(e)}"
        
async def main():
    await mcp.run_sse_async()
    
if __name__ == "__main__":
    asyncio.run(main())
