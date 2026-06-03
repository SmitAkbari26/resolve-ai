import json
import asyncio


class MCPClient:
    def __init__(self):
        self.process = None
        self.request_id = 0

    async def start(self):
        self.process = await asyncio.create_subprocess_exec(
            "python",
            "C:/Projects/ResolveAI/mcp/main.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    def _next_id(self):
        self.request_id += 1
        return self.request_id

    async def send_request(self, method: str, params: dict = None):
        request_id = self._next_id()

        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        self.process.stdin.write((json.dumps(payload) + "\n").encode())
        await self.process.stdin.drain()
        response_line = await self.process.stdout.readline()
        return json.loads(response_line.decode())

    async def get_tools(self):
        return await self.send_request("tools/list")

    async def execute_tool(self, tool_name, arguments):
        return await self.send_request(
            "tools/call", {"name": tool_name, "arguments": arguments}
        )


mcp_client = MCPClient()

