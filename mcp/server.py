import sys
import json
from handler import Handler
from Helper.error_helper import create_error_message


class MCPServer:
    def __init__(self):
        self.handler = Handler()

    async def run(self):
        """
        Continuously reads JSON-RPC requests from standard input and dispatches them to the appropriate handler methods.

        The loop runs until an empty line is read (EOF). Each line is parsed as JSON and expected to contain:
        - method (str): The RPC method name.
        - id (any): The request identifier.
        - params (dict, optional): Parameters for the method.

        Supported methods:
        - initialize: Calls self.handler.handle_initialize.
        - tools/list: Calls self.handler.handle_tools_list.
        - tools/call: Calls self.handler.handle_tool_call with provided params.

        If the method is unknown, a SendError with code -32601 is sent.
        If JSON parsing or any other exception occurs, a SendError with code -32700 is sent.

        Args:
            self: Instance of the class containing the handler attribute used to process requests.

        Returns:
            None
        """
        while True:
            line = sys.stdin.readline()

            if not line:
                break

            try:
                request = json.loads(line)

                method = request.get("method")
                request_id = request.get("id")
                params = request.get("params", {})

                if method == "initialize":
                    await self.handler.handle_initialize(request_id)

                elif method == "tools/list":
                    await self.handler.handle_tools_list(request_id)

                elif method == "tools/call":
                    await self.handler.handle_tool_call(request_id, params)

                else:
                    self.handler.send_error(
                        create_error_message(request_id, -32601),
                        f"Unknown method: {method}",
                    )

            except Exception as e:
                await self.handler.send_error(
                    create_error_message(1, -32700, str(e))
                )


async def main():
    server = MCPServer()
    await server.run()
