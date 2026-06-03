import sys
import json
from Helper.error_helper import create_error_message
from Helper.response_helper import create_response
from register import TOOL_REGISTRY
from models.handler_model import SendError, SendErrorMessage, SendResponse
from config import MCP_PROTOCOL_VERSION, JSON_RPC_VERSION, MCP_SERVER_VERSION


class Handler:
    def __init__(self):
        self.protocol_version = MCP_PROTOCOL_VERSION

    async def handle_initialize(self, request_id):
        """
        Handle an initialize request from a client.

        Args:
            request_id (Any): The identifier of the incoming request to be echoed in the response.

        Returns:
            None: Sends an Initialize response asynchronously via the connection.
        """
        result = {
            "protocolVersion": self.protocol_version,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "ResolveAI MCP", "version": MCP_SERVER_VERSION},
        }
        await self.send_response(create_response(request_id, result))

    async def handle_tools_list(self, request_id):
        """
        Handle a request to list available tools.

        Args:
            request_id (Any): Identifier for the incoming request.

        Returns:
            None: Sends a response containing the list of tools via the connection.
        """
        tools = []

        for name, meta in TOOL_REGISTRY.items():
            tools.append(
                {
                    "name": name,
                    "description": meta["description"],
                    "inputSchema": meta["input_schema"],
                }
            )

        await self.send_response(create_response(request_id, {"tools": tools}))

    async def handle_tool_call(self, request_id, params):
        """
        Handle a tool call request by invoking the registered tool.

        Args:
            request_id (str): Identifier of the incoming request.
            params (dict): Parameters containing the tool name and optional arguments.

        Returns:
            None: Sends a response or error message back to the client.
        """
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name not in TOOL_REGISTRY:
            await self.send_error(
                create_error_message(request_id, -32601, "tool not found")
            )
            return

        tool = TOOL_REGISTRY[name]["function"]

        try:
            result = await tool(**arguments)

            await self.send_response(
                create_response(
                    request_id,
                    {"content": [{"type": "json", "data": result}]},
                )
            )

        except Exception as e:
            await self.send_error(create_error_message(request_id, -32000, str(e)))

    async def send_response(self, send_response: SendResponse):
        """
        Send a JSON-RPC 2.0 response to stdout.

        Args:
            id (int | str | None): The identifier of the request being responded to.
            result (Any): The result payload to include in the response.

        Returns:
            None: The function writes the response to stdout and does not return a value.
        """
        response = {"jsonrpc": JSON_RPC_VERSION, **send_response.model_dump()}
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

    async def send_error(self, send_error_message: SendError):
        """
        Send an error response over stdout using JSON-RPC 2.0 format.

        Args:
            send_error_message (SendError): Model containing error details to be serialized.

        Returns:
            None
        """
        response = {"jsonrpc": JSON_RPC_VERSION, **send_error_message.model_dump()}

        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()
