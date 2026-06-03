import json
import re
import asyncio
from typing import Optional, Callable
from config import GROQ_API_KEY, GROQ_MODEL
from mcp.client import MCPClient
from utils.logger import get_logger
from prompts.base.system_prompt import BASE_SYSTEM_PROMPT
from groq import AsyncGroq

logger = get_logger(__name__)


class StreamingJsonFieldExtractor:
    def __init__(self, target_keys: list[str]):
        self.target_keys = target_keys
        self.found_key = None
        self.in_value = False
        self.escape_next = False
        self.scan_idx = 0
        self.is_short_circuit = None

    def feed_and_extract(self, full_text: str) -> str:
        # Check if short_circuit value has been determined yet
        if self.is_short_circuit is None:
            match_sc = re.search(r'"short_circuit"\s*:\s*(true|false)', full_text)
            if match_sc:
                self.is_short_circuit = (match_sc.group(1) == "true")

        # Suppress streaming if it's determined that this is NOT a short-circuit
        if self.is_short_circuit is False:
            return ""

        if not self.in_value:
            for key in self.target_keys:
                pattern = f'"{key}"\\s*:\\s*"'
                match = re.search(pattern, full_text[self.scan_idx:])
                if match:
                    self.in_value = True
                    self.found_key = key
                    self.scan_idx += match.end()
                    break
            if not self.in_value:
                if len(full_text) > 50:
                    self.scan_idx = len(full_text) - 50
                return ""

        extracted = []
        while self.scan_idx < len(full_text):
            char = full_text[self.scan_idx]
            self.scan_idx += 1
            if self.escape_next:
                if char == 'n':
                    extracted.append('\n')
                elif char == 't':
                    extracted.append('\t')
                else:
                    extracted.append(char)
                self.escape_next = False
            elif char == '\\':
                self.escape_next = True
            elif char == '"':
                self.in_value = False
                break
            else:
                extracted.append(char)
        
        return "".join(extracted)


class BaseAgent:
    # Cache MCP tool metadata to reduce repeated MCP calls per workflow.
    _mcp_tools_cache = None
    _mcp_tools_cache_at = 0.0
    _MCP_TOOLS_CACHE_TTL_S = 300.0

    def __init__(self, mcp_client: Optional[object] = None):
        if mcp_client is None:
            from mcp.client import mcp_client as default_mcp
            self.mcp = default_mcp
        else:
            self.mcp = mcp_client

    async def __call__(self, state: dict) -> dict:
        return await self.process(state)

    async def invoke_llm(
        self,
        prompt: str,
        state: dict = None,
        tools_enabled: bool = False,
        allowed_tool_names: list[str] = None,
        json_mode: bool = False,
        max_turns: int = 5,
        stream_callback: Optional[Callable[[str], None]] = None,
    ):
        client = AsyncGroq(api_key=GROQ_API_KEY)

        messages = [
            {
                "role": "system",
                "content": BASE_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        kwargs = {
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.3,
            "max_completion_tokens": 1024,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        cleaned_tools = []

        if tools_enabled:
            kwargs.pop("response_format", None)
            try:
                # Fetch tool list only when cache is stale.
                import time
                now = time.time()
                cache_age = now - self.__class__._mcp_tools_cache_at
                if (
                     self.__class__._mcp_tools_cache is None
                     or cache_age > self.__class__._MCP_TOOLS_CACHE_TTL_S
                ):
                    mcp_tools = await self.mcp.get_tools()
                    self.__class__._mcp_tools_cache = mcp_tools
                    self.__class__._mcp_tools_cache_at = now
                else:
                    mcp_tools = self.__class__._mcp_tools_cache

                mcp_tools = mcp_tools or {}

                if mcp_tools.get("result"):
                    for t in mcp_tools["result"]["tools"]:
                        name = t["name"]
                        if allowed_tool_names is not None and name not in allowed_tool_names:
                            continue

                        cleaned_tools.append(
                            {
                                "type": "function",
                                "function": {
                                    "name": t["name"],
                                    "description": t["description"],
                                    "parameters": t["inputSchema"],
                                },
                            }
                        )

                if cleaned_tools:
                    kwargs["tools"] = cleaned_tools
                    kwargs["tool_choice"] = "auto"
            except Exception as e:
                logger.warning(f"Failed to fetch tools: {e}")

        callback = stream_callback or (state.get("stream_callback") if state else None)
        tool_calls_executed = []

        for _ in range(max_turns):
            if callback:
                kwargs["stream"] = True
                stream = await client.chat.completions.create(**kwargs)
                
                full_text = ""
                tool_calls_raw = {}
                extractor = StreamingJsonFieldExtractor([
                    "ai_response", "answer", "message", "response_to_customer", "response"
                ])
                
                async for chunk in stream:
                    delta = chunk.choices[0].delta
                    content = delta.content or ""
                    
                    if content:
                        full_text += content
                        if not tool_calls_raw:
                            extracted_chunk = extractor.feed_and_extract(full_text)
                            if extracted_chunk:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(extracted_chunk)
                                else:
                                    callback(extracted_chunk)
                                    
                    if getattr(delta, "tool_calls", None):
                        for tc in delta.tool_calls:
                            idx = tc.index
                            if idx not in tool_calls_raw:
                                tool_calls_raw[idx] = {
                                    "id": tc.id or "",
                                    "type": "function",
                                    "function": {
                                        "name": tc.function.name or "",
                                        "arguments": tc.function.arguments or ""
                                    }
                                }
                            else:
                                if tc.id:
                                    tool_calls_raw[idx]["id"] = tc.id
                                if tc.function.name:
                                    tool_calls_raw[idx]["function"]["name"] = tc.function.name
                                if tc.function.arguments:
                                    tool_calls_raw[idx]["function"]["arguments"] += tc.function.arguments

                tool_calls = [tool_calls_raw[i] for i in sorted(tool_calls_raw.keys())]
                
                if not tool_calls:
                    return {
                        "content": full_text,
                        "tool_calls": tool_calls_executed,
                    }
                
                # Append the assistant message that contained tool_calls
                assistant_msg = {"role": "assistant", "content": full_text or None}
                if tool_calls:
                    assistant_msg["tool_calls"] = tool_calls
                messages.append(assistant_msg)

                for tc in tool_calls:
                    t_name = tc["function"]["name"]
                    t_args = json.loads(tc["function"]["arguments"])
                    result = await self.mcp.execute_tool(
                        tool_name=t_name,
                        arguments=t_args,
                    )
                    tool_calls_executed.append(
                        {
                            "tool": t_name,
                            "arguments": t_args,
                            "result": result,
                        }
                    )
                    tool_content = json.dumps(result)
                    if len(tool_content) > 3000:
                        tool_content = tool_content[:3000] + "...[truncated]"

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "name": t_name,
                            "content": tool_content,
                        }
                    )
                kwargs["messages"] = messages
            else:
                kwargs["stream"] = False
                completion = await client.chat.completions.create(**kwargs)
                message = completion.choices[0].message

                if not getattr(message, "tool_calls", None):
                    return {
                        "content": message.content,
                        "tool_calls": tool_calls_executed,
                    }

                for tool_call in message.tool_calls:
                    t_name = tool_call.function.name
                    t_args = json.loads(tool_call.function.arguments)
                    result = await self.mcp.execute_tool(
                        tool_name=t_name,
                        arguments=t_args,
                    )
                    tool_calls_executed.append(
                        {
                            "tool": t_name,
                            "arguments": t_args,
                            "result": result,
                        }
                    )
                    tool_content = json.dumps(result)

                    if len(tool_content) > 3000:
                        tool_content = tool_content[:3000] + "...[truncated]"

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": t_name,
                            "content": tool_content,
                        }
                    )

                    kwargs["messages"] = messages

        return {
            "content": "",
            "tool_calls": tool_calls_executed,
        }
