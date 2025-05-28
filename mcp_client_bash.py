import asyncio
import os
from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import Dict, Any

class BashClient:
    """Client for interacting with a Unix shell using an MCP server."""

    def __init__(self, server_url: str = "http://10.122.11.111:8081/sse"):
        """Initialize the Bash client.

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

    async def execute_command(self, command: str) -> str:
        """Send a command execution request to the MCP server.

        Args:
            command: The command to execute (e.g., "ls -l /path/to/dir").

        Returns:
            The output of command execution as a string.
        """
        # Initialize the client session
        result = await self.session.call_tool(name="execute_command", arguments={"command": command})
        return result.content[0].text

async def main():
    # Create client to interact with MCP bash server
    client = BashClient()
    await client.connect_to_sse_server(client.server_url)

    # list all files in current working directory of MCP server process
    result = await client.execute_command("ls -l ./")
    print("Execute Command Result:", result)

    # check file space left on disk
    result = await client.execute_command("df -h")
    print("Disk Space Result:", result)

    # print the output a text file given its absolute path
    result = await client.execute_command("cat /etc/hostname")
    print("File Content Result:", result)

    # print the content of a C++ file with line numbers
    result = await client.execute_command("cat -n find_primes.cpp")
    print("File Content Result:", result)

    # execute an invalid command to see if error handling works and server still responds without crashing
    result = await client.execute_command("cat -n find_primes2.cpp")
    print("File Content Result:", result)

    # run a simple C++ program that finds all prime numbers upto 1e6 using Sieve of Eratosthenes
    result = await client.execute_command("g++ -Wall find_primes.cpp && ./a.out")
    print("C++ Program Result:", result)

    # Cleanup
    await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())