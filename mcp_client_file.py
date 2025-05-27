import asyncio
import os
from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import Dict, Any

class FileViewerClient:
    """Client for interacting with the File Viewer API MCP server."""

    def __init__(self, server_url: str = "http://10.122.11.111:8080/sse"):
        """Initialize the File Viewer API client.

        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport"""

        print("Connecting to MCP SSE server...")
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()
        print("Streams:", streams)  

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        print("Initializing SSE client...")
        await self.session.initialize()
        print("Initialized SSE client")

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)

    async def list_files(self, path: str) -> str:
        """Send a list files request to the MCP server.

        Args:
            path: The absolute path to the directory to list files from.

        Returns:
            JSON string containing the list of files
        """
        # Initialize the client session
        result = await self.session.call_tool(name="list_files", arguments={"path": path})
        return result

    async def read_file(self, path: str) -> str:
        """Send a read file request to the MCP server.

        Args:
            path: The absolute path to the file to read. Similar to `cat` command in Unix. Only reads plain-text files.

        Returns:
            String containing the content of the file.

        """
        result = await self.session.call_tool(name="read_file", arguments={"path": path})
        return result   

    async def write_file(self, path: str, content: str) -> str:
        """Send a write file request to the MCP server.

        Args:
            path: The absolute path to the file to write.
            content: The content to write to the file.

        Returns:
            Success/error message as a string.
        """
        result = await self.session.call_tool(name="write_file", arguments={"path": path, "content": content})
        return result

    async def delete_file(self, path: str) -> str:
        """Send a delete file request to the MCP server.

        Args:
            path: The absolute path to the file to delete.

        Returns:
            Success/error message as a string.
        """
        result = await self.session.call_tool(name="delete_file", arguments={"path": path})
        return result

async def main():
    # Create client
    client = FileViewerClient()
    await client.connect_to_sse_server(client.server_url)
    result = await client.list_files(path = "/home/ubuntu/aditya/mcp-file-server/smolagents/examples")
    print("List Files Result:", result)

    result = await client.read_file(path = "/home/ubuntu/aditya/mcp-file-server/smolagents/examples/sandboxed_execution.py")
    print("Read File Result:", result)

    result = await client.write_file(path = "/home/ubuntu/aditya/mcp-file-server/smolagents/examples2/test_write.txt", content = "This is a test write operation.")
    print("Write File Result:", result)

    result = await client.delete_file("/home/ubuntu/aditya/mcp-file-server/smolagents/docs/README.md")
    print("Delete File Result:", result)
    await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())