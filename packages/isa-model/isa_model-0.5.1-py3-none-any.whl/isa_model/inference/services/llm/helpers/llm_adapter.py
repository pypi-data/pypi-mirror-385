#!/usr/bin/env python3
"""
统一适配器架构 - 支持多框架集成
将不同框架的消息、工具、上下文统一适配到 OpenAI 格式
"""

import json
import inspect
from typing import Dict, Any, List, Union, Optional, Callable, Protocol
from abc import ABC, abstractmethod


# ============= 适配器协议定义 =============

class MessageAdapter(Protocol):
    """消息适配器协议"""
    
    def can_handle(self, input_data: Any) -> bool:
        """检查是否能处理该输入格式"""
        ...
    
    def to_openai_format(self, input_data: Any) -> List[Dict[str, str]]:
        """转换为 OpenAI 格式"""
        ...
    
    def from_openai_format(self, response: str, original_input: Any) -> Any:
        """从 OpenAI 格式转换回原始格式"""
        ...


class ToolAdapter(Protocol):
    """工具适配器协议"""
    
    def can_handle(self, tool: Any) -> bool:
        """检查是否能处理该工具"""
        ...
    
    def to_openai_schema(self, tool: Any) -> Dict[str, Any]:
        """转换为 OpenAI 工具 schema"""
        ...
    
    async def execute_tool(self, tool: Any, arguments: Dict[str, Any]) -> Any:
        """执行工具"""
        ...


class ContextAdapter(Protocol):
    """上下文适配器协议"""
    
    adapter_name: str
    
    def can_provide_context(self, query: str, context_type: str) -> bool:
        """检查是否能为查询提供上下文"""
        ...
    
    async def get_relevant_context(self, query: str, limit: int = 5) -> str:
        """获取相关上下文"""
        ...


# ============= LangChain 适配器实现 =============

class LangChainMessageAdapter:
    """LangChain 消息适配器"""
    
    def __init__(self):
        self.adapter_name = "langchain"
        self.priority = 8
    
    def can_handle(self, input_data: Any) -> bool:
        """检查是否是 LangChain 消息"""
        if isinstance(input_data, list) and input_data:
            return hasattr(input_data[0], 'type') and hasattr(input_data[0], 'content')
        return hasattr(input_data, 'type') and hasattr(input_data, 'content')
    
    def to_openai_format(self, input_data: Any) -> List[Dict[str, str]]:
        """转换 LangChain 消息为 OpenAI 格式"""
        if not isinstance(input_data, list):
            input_data = [input_data]
        
        converted_messages = []
        for msg in input_data:
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                msg_dict = {"content": str(msg.content)}
                
                if msg.type == "system":
                    msg_dict["role"] = "system"
                elif msg.type == "human":
                    msg_dict["role"] = "user"
                elif msg.type == "ai":
                    msg_dict["role"] = "assistant"
                    # Handle tool calls if present in LangChain AI messages
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        tool_calls = []
                        for tc in msg.tool_calls:
                            if isinstance(tc, dict):
                                # LangChain format: {"name": "func", "args": {...}, "id": "..."}
                                tool_call = {
                                    "id": tc.get("id", f"call_{len(tool_calls)}"),
                                    "type": "function",
                                    "function": {
                                        "name": tc.get("name", "unknown"),
                                        "arguments": json.dumps(tc.get("args", {}))
                                    }
                                }
                            else:
                                # Handle other tool call formats
                                tool_call = {
                                    "id": getattr(tc, 'id', f"call_{len(tool_calls)}"),
                                    "type": "function",
                                    "function": {
                                        "name": getattr(tc, 'name', 'unknown'),
                                        "arguments": json.dumps(getattr(tc, 'args', {}))
                                    }
                                }
                            tool_calls.append(tool_call)
                        
                        msg_dict["tool_calls"] = tool_calls  # type: ignore
                elif msg.type == "tool":
                    msg_dict["role"] = "tool"
                    if hasattr(msg, 'tool_call_id'):
                        msg_dict["tool_call_id"] = msg.tool_call_id
                elif msg.type == "function":  # Legacy function message
                    msg_dict["role"] = "function"
                    if hasattr(msg, 'name'):
                        msg_dict["name"] = msg.name
                else:
                    # Unknown message type, default to user
                    msg_dict["role"] = "user"
                
                converted_messages.append(msg_dict)
        
        return converted_messages
    
    def from_openai_format(self, response: Union[str, Any], original_input: Any) -> Any:
        """从 OpenAI 格式转换回 LangChain 格式"""
        try:
            from langchain_core.messages import AIMessage
            
            # Handle response objects with tool_calls (OpenAI message objects)
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Convert OpenAI tool_calls to LangChain format
                tool_calls = []
                for tc in response.tool_calls:
                    tool_call = {
                        "name": tc.function.name,
                        "args": json.loads(tc.function.arguments),
                        "id": tc.id
                    }
                    tool_calls.append(tool_call)
                
                return AIMessage(
                    content=response.content if response.content is not None else "",
                    tool_calls=tool_calls
                )
            else:
                # Handle simple string response
                content = response if isinstance(response, str) else getattr(response, 'content', str(response))
                return AIMessage(content=content)
                
        except ImportError:
            # 回退实现
            class SimpleAIMessage:
                def __init__(self, content, tool_calls=None):
                    self.content = content
                    self.type = "ai"
                    self.tool_calls = tool_calls or []
            
            # Handle response objects with tool_calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_calls = []
                for tc in response.tool_calls:
                    tool_call = {
                        "name": tc.function.name,
                        "args": json.loads(tc.function.arguments),
                        "id": tc.id
                    }
                    tool_calls.append(tool_call)
                
                return SimpleAIMessage(response.content if response.content is not None else "", tool_calls)
            else:
                content = response if isinstance(response, str) else getattr(response, 'content', str(response))
                return SimpleAIMessage(content)


class LangChainToolAdapter:
    """LangChain 工具适配器"""
    
    def __init__(self):
        self.adapter_name = "langchain_tool"
        self.priority = 8
    
    def can_handle(self, tool: Any) -> bool:
        """检查是否是 LangChain 工具"""
        return (hasattr(tool, 'name') and hasattr(tool, 'description') 
                and hasattr(tool, 'args_schema'))
    
    def to_openai_schema(self, tool: Any) -> Dict[str, Any]:
        """转换 LangChain 工具为 OpenAI schema"""
        properties = {}
        required = []
        
        if tool.args_schema and hasattr(tool.args_schema, 'model_fields'):
            for field_name, field_info in tool.args_schema.model_fields.items():
                field_type = getattr(field_info, 'annotation', str)
                
                if field_type == str:
                    prop_type = "string"
                elif field_type == int:
                    prop_type = "integer"
                elif field_type == float:
                    prop_type = "number"
                elif field_type == bool:
                    prop_type = "boolean"
                else:
                    prop_type = "string"
                
                properties[field_name] = {"type": prop_type}
                
                if hasattr(field_info, 'default') and field_info.default == ...:
                    required.append(field_name)
        
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    async def execute_tool(self, tool: Any, arguments: Dict[str, Any]) -> Any:
        """执行 LangChain 工具"""
        try:
            if len(arguments) == 1:
                input_value = list(arguments.values())[0]
                result = tool.invoke(input_value)
            else:
                result = tool.invoke(arguments)
            
            if hasattr(result, '__await__'):
                result = await result
            
            return result
        except Exception as e:
            return f"Error executing LangChain tool {tool.name}: {str(e)}"


# ============= OpenAI 格式工具适配器 =============

class DictToolAdapter:
    """OpenAI 格式工具字典适配器"""
    
    def __init__(self):
        self.adapter_name = "dict_tool"
        self.priority = 9  # Higher priority than Python functions
    
    def can_handle(self, tool: Any) -> bool:
        """检查是否是 OpenAI 格式的工具字典"""
        return (isinstance(tool, dict) and 
                tool.get("type") == "function" and
                "function" in tool and
                isinstance(tool["function"], dict) and
                "name" in tool["function"])
    
    def to_openai_schema(self, tool: Any) -> Dict[str, Any]:
        """工具已经是 OpenAI 格式，直接返回"""
        return tool
    
    async def execute_tool(self, tool: Any, arguments: Dict[str, Any]) -> Any:
        """执行 OpenAI 格式工具（通常需要外部执行器）"""
        # 对于 OpenAI 格式的工具字典，我们无法直接执行
        # 这种情况下返回一个指示，让调用方处理
        tool_name = tool["function"]["name"]
        return f"Error: Cannot execute dict tool {tool_name} directly. Requires external executor."


# ============= MCP 工具适配器 =============

class MCPToolAdapter:
    """MCP 工具适配器 - 处理 MCP 协议的工具格式"""
    
    def __init__(self):
        self.adapter_name = "mcp_tool"
        self.priority = 7  # 高优先级，在 LangChain 和 Dict 之间
    
    def can_handle(self, tool: Any) -> bool:
        """检查是否是 MCP 工具格式"""
        return (isinstance(tool, dict) and 
                "name" in tool and 
                "description" in tool and
                "inputSchema" in tool and
                isinstance(tool["inputSchema"], dict))
    
    def to_openai_schema(self, tool: Any) -> Dict[str, Any]:
        """转换 MCP 工具为 OpenAI schema"""
        return {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool.get("inputSchema", {"type": "object", "properties": {}})
            }
        }
    
    async def execute_tool(self, tool: Any, arguments: Dict[str, Any]) -> Any:
        """MCP 工具执行由外部处理，这里返回指示信息"""
        tool_name = tool["name"]
        return f"MCP tool {tool_name} execution should be handled externally by MCP client"


# ============= Python 函数适配器 =============

class PythonFunctionAdapter:
    """Python 函数适配器"""
    
    def __init__(self):
        self.adapter_name = "python_function"
        self.priority = 5
    
    def can_handle(self, tool: Any) -> bool:
        """检查是否是 Python 函数"""
        return callable(tool) and hasattr(tool, '__name__')
    
    def to_openai_schema(self, tool: Any) -> Dict[str, Any]:
        """转换 Python 函数为 OpenAI schema"""
        func = tool  # tool 就是函数
        sig = inspect.signature(func)
        properties = {}
        required = []
        
        # 尝试获取类型提示，优雅处理错误
        try:
            from typing import get_type_hints
            type_hints = get_type_hints(func)
        except (NameError, AttributeError, TypeError):
            type_hints = {}
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    type_hints[param_name] = param.annotation
        
        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name, str)
            
            # 转换 Python 类型到 JSON schema 类型
            if param_type == str or param_type == "str":
                prop_type = "string"
            elif param_type == int or param_type == "int":
                prop_type = "integer"
            elif param_type == float or param_type == "float":
                prop_type = "number"
            elif param_type == bool or param_type == "bool":
                prop_type = "boolean"
            elif param_type == list or param_type == "list":
                prop_type = "array"
            elif param_type == dict or param_type == "dict":
                prop_type = "object"
            else:
                prop_type = "string"
            
            properties[param_name] = {"type": prop_type}
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__ or f"Function {func.__name__}",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    async def execute_tool(self, tool: Any, arguments: Dict[str, Any]) -> Any:
        """执行 Python 函数"""
        func = tool  # tool 就是函数
        try:
            result = func(**arguments)
            if hasattr(result, '__await__'):
                result = await result
            return result
        except Exception as e:
            return f"Error executing function {func.__name__}: {str(e)}"


# ============= 标准格式适配器 =============

class StandardMessageAdapter:
    """标准消息适配器（处理字典和字符串）"""
    
    def __init__(self):
        self.adapter_name = "standard"
        self.priority = 1  # 最低优先级，作为回退
    
    def can_handle(self, input_data: Any) -> bool:
        """处理所有标准格式"""
        return True  # 作为回退适配器
    
    def to_openai_format(self, input_data: Any) -> List[Dict[str, str]]:
        """转换标准格式为 OpenAI 格式"""
        if isinstance(input_data, str):
            return [{"role": "user", "content": input_data}]
        elif isinstance(input_data, list):
            if not input_data:
                return [{"role": "user", "content": ""}]
            
            if isinstance(input_data[0], dict):
                return input_data  # 假设已经是 OpenAI 格式
            else:
                # 转换字符串列表
                messages = []
                for i, msg in enumerate(input_data):
                    role = "user" if i % 2 == 0 else "assistant"
                    messages.append({"role": role, "content": str(msg)})
                return messages
        else:
            return [{"role": "user", "content": str(input_data)}]
    
    def from_openai_format(self, response: Union[str, Any], original_input: Any) -> Any:
        """从 OpenAI 格式转换回原始格式

        Return format matches the input format:
        - String input → Plain string output
        - List of dicts (OpenAI chat format) → OpenAI completion dict
        """
        # Extract content from response
        if isinstance(response, str):
            content = response
        elif hasattr(response, 'content'):
            content = response.content if response.content is not None else ""
        else:
            content = str(response)

        # Determine output format based on original input
        if isinstance(original_input, str):
            # String input → return plain string
            return content

        elif isinstance(original_input, list) and original_input and isinstance(original_input[0], dict):
            # OpenAI chat format input → return OpenAI completion format
            completion = {
                "id": f"chatcmpl-{hash(content) % 1000000}",
                "object": "chat.completion",
                "created": int(__import__('time').time()),
                "model": "unknown",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }
                ]
            }

            # Handle tool_calls if present
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_calls = []
                for tc in response.tool_calls:
                    if hasattr(tc, 'function'):
                        tool_call = {
                            "id": getattr(tc, 'id', f"call_{len(tool_calls)}"),
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        tool_calls.append(tool_call)

                completion["choices"][0]["message"]["tool_calls"] = tool_calls
                completion["choices"][0]["finish_reason"] = "tool_calls"

            return completion

        else:
            # For other inputs (list of strings, etc.), return plain string
            return content


# ============= 适配器管理器 =============

class AdapterManager:
    """适配器管理器 - 统一管理所有类型的适配器"""
    
    def __init__(self):
        self.message_adapters: List[MessageAdapter] = []
        self.tool_adapters: List[ToolAdapter] = []
        self.context_adapters: List[ContextAdapter] = []
        
        # 注册默认适配器
        self._register_default_adapters()
    
    def _register_default_adapters(self):
        """注册默认适配器"""
        # 消息适配器（按优先级排序）
        self.message_adapters = [
            LangChainMessageAdapter(),
            StandardMessageAdapter()  # 回退适配器
        ]
        
        # 工具适配器（按优先级排序）
        self.tool_adapters = [
            DictToolAdapter(),        # 最高优先级 - OpenAI格式工具
            LangChainToolAdapter(),   # 中等优先级 - LangChain工具
            MCPToolAdapter(),         # 高优先级 - MCP工具
            PythonFunctionAdapter()   # 最低优先级 - Python函数
        ]
    
    def register_custom_adapter(self, adapter, adapter_type: str):
        """注册自定义适配器"""
        if adapter_type == "message":
            # 按优先级插入
            priority = getattr(adapter, 'priority', 5)
            inserted = False
            for i, existing in enumerate(self.message_adapters):
                if getattr(existing, 'priority', 5) < priority:
                    self.message_adapters.insert(i, adapter)
                    inserted = True
                    break
            if not inserted:
                self.message_adapters.append(adapter)
        
        elif adapter_type == "tool":
            priority = getattr(adapter, 'priority', 5)
            inserted = False
            for i, existing in enumerate(self.tool_adapters):
                if getattr(existing, 'priority', 5) < priority:
                    self.tool_adapters.insert(i, adapter)
                    inserted = True
                    break
            if not inserted:
                self.tool_adapters.append(adapter)
        
        elif adapter_type == "context":
            self.context_adapters.append(adapter)
    
    def convert_messages(self, input_data: Any) -> List[Dict[str, str]]:
        """转换消息格式"""
        for adapter in self.message_adapters:
            if adapter.can_handle(input_data):
                return adapter.to_openai_format(input_data)
        
        # 不应该到这里，因为有回退适配器
        return [{"role": "user", "content": str(input_data)}]
    
    def format_response(self, response: Union[str, Any], original_input: Any) -> Any:
        """格式化响应"""
        for adapter in self.message_adapters:
            if adapter.can_handle(original_input):
                return adapter.from_openai_format(response, original_input)
        
        return response
    
    async def convert_tools_to_schemas(self, tools: List[Any]) -> tuple[List[Dict[str, Any]], Dict[str, tuple]]:
        """转换工具为 OpenAI schemas"""
        schemas = []
        tool_mappings = {}  # 存储工具名到适配器的映射
        
        for tool in tools:
            for adapter in self.tool_adapters:
                if adapter.can_handle(tool):
                    schema = adapter.to_openai_schema(tool)
                    schemas.append(schema)
                    
                    # 存储映射关系
                    tool_name = schema["function"]["name"]
                    tool_mappings[tool_name] = (tool, adapter)
                    break
        
        return schemas, tool_mappings
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], 
                          tool_mappings: Dict[str, tuple]) -> Any:
        """执行工具"""
        if tool_name in tool_mappings:
            tool, adapter = tool_mappings[tool_name]
            return await adapter.execute_tool(tool, arguments)
        else:
            return f"Error: Tool {tool_name} not found"
    
    async def get_context(self, query: str, context_type: str = "all", 
                         limit: int = 5) -> str:
        """获取上下文"""
        context_parts = []
        
        for adapter in self.context_adapters:
            if adapter.can_provide_context(query, context_type):
                try:
                    context = await adapter.get_relevant_context(query, limit)
                    if context:
                        context_parts.append(context)
                except Exception as e:
                    print(f"Warning: Context adapter {adapter.adapter_name} failed: {e}")
        
        return "\n\n".join(context_parts) 