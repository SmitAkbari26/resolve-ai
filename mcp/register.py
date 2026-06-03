TOOL_REGISTRY = {}


def register_tool(name, description, input_schema, output_schema):
    """
    Register a tool in the global TOOL_REGISTRY.

    Args:
        name (str): Identifier for the tool.
        description (str): Human‑readable description of what the tool does.
        input_schema (dict): JSON‑schema describing the expected input parameters.
        output_schema (dict): JSON‑schema describing the structure of the output.

    Returns:
        Callable[[Callable], Callable]: A decorator that, when applied to a function, stores the function and its metadata in TOOL_REGISTRY and returns the original function.
    """

    def decorator(func):
        TOOL_REGISTRY[name] = {
            "function": func,
            "description": description,
            "input_schema": input_schema,
            "output_schema": output_schema,
        }

        return func

    return decorator
