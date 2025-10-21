from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, AsyncGenerator, Callable
import logging
import json

from isa_model.inference.services.base_service import BaseService
from isa_model.inference.services.llm.helpers.llm_adapter import AdapterManager
from isa_model.inference.services.llm.helpers.llm_utils import TokenCounter, TextProcessor, ResponseParser, LLMMetrics
from isa_model.inference.services.llm.helpers.llm_prompts import LLMPrompts, LLMPromptTemplates

logger = logging.getLogger(__name__)

class BaseLLMService(BaseService):
    """Base class for Large Language Model services with unified task dispatch"""
    
    def __init__(self, provider_name: str, model_name: str, **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        self._bound_tools: List[Any] = []
        self._tool_mappings: Dict[str, tuple] = {}
        
        # 初始化适配器管理器
        self.adapter_manager = AdapterManager()
        
        # Initialize helper utilities (optional, can be overridden by specific services)
        self.token_counter = TokenCounter(model_name)
        self.text_processor = TextProcessor()
        self.response_parser = ResponseParser()
        self.llm_prompts = LLMPrompts()
        
        # Get config from provider
        provider_config = self.get_provider_config()
        self.streaming = provider_config.get("streaming", False)
        self.max_tokens = provider_config.get("max_tokens", 4096)
        self.temperature = provider_config.get("temperature", 0.7)
    
    async def invoke(
        self, 
        input_data: Union[str, List[Dict[str, str]], Any],
        task: Optional[str] = None,
        show_reasoning: bool = False,
        output_format: Optional[str] = None,
        json_schema: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一的任务分发方法 - Base类提供通用实现
        
        Args:
            input_data: 输入数据，可以是:
                - str: 简单文本提示
                - list: 消息历史 [{"role": "user", "content": "hello"}]
                - Any: LangChain 消息对象或其他格式
            task: 任务类型，支持多种LLM任务
            output_format: Output format ("json", "markdown", "code", etc.)
            json_schema: JSON schema for structured output validation
            **kwargs: 任务特定的附加参数
            
        Returns:
            Dict containing task results (optionally formatted as JSON)
        """
        task = task or "chat"
        
        # Store formatting options for use by specific task methods
        format_options = {
            "output_format": output_format,
            "json_schema": json_schema,
            "repair_attempts": kwargs.get("repair_attempts", 3)
        }
        
        # Execute task and apply formatting
        result = None
        
        # ==================== 对话类任务 ====================
        if task == "chat":
            # Pass all kwargs to ainvoke for better parameter support (like response_format)
            result_raw = await self.ainvoke(input_data, show_reasoning=show_reasoning, **kwargs)
            # Wrap in chat response format, preserving AIMessage objects with tool_calls
            if hasattr(result_raw, 'tool_calls'):
                # This is an AIMessage with tool_calls - preserve the entire object
                result = {"message": result_raw}
            elif hasattr(result_raw, 'content'):
                # Regular AIMessage without tool_calls - extract content
                content = result_raw.content
                result = {"message": content}
            else:
                # Plain string response
                content = str(result_raw)
                result = {"message": content}
        elif task == "complete":
            result = await self.complete_text(input_data, kwargs.get("max_tokens", self.max_tokens))
        elif task == "instruct":
            result = await self.instruct(input_data, kwargs.get("instruction"), kwargs.get("max_tokens", self.max_tokens))
        
        # ==================== 文本生成类任务 ====================
        elif task == "generate":
            result = await self.generate_text(input_data, kwargs.get("max_tokens", self.max_tokens))
        elif task == "rewrite":
            result = await self.rewrite_text(input_data, kwargs.get("style"), kwargs.get("tone"))
        elif task == "summarize":
            result = await self.summarize_text(input_data, kwargs.get("max_length"), kwargs.get("style"))
        elif task == "translate":
            target_language = kwargs.get("target_language")
            if not target_language:
                raise ValueError("target_language is required for translate task")
            result = await self.translate_text(input_data, target_language, kwargs.get("source_language"))
        
        # ==================== 分析类任务 ====================
        elif task == "analyze":
            result = await self.analyze_text(input_data, kwargs.get("analysis_type"))
        elif task == "classify":
            result = await self.classify_text(input_data, kwargs.get("categories"))
        elif task == "extract":
            result = await self.extract_information(input_data, kwargs.get("extract_type"))
        elif task == "sentiment":
            # Always use chat with appropriate prompt for sentiment analysis
            if output_format == "json":
                # Create JSON-formatted prompt
                json_prompt = self.create_json_prompt(
                    f"Please analyze the sentiment of the following text: {input_data}",
                    json_schema or {
                        "type": "object",
                        "properties": {
                            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "explanation": {"type": "string"}
                        },
                        "required": ["sentiment"]
                    }
                )
                result = await self.chat(json_prompt, show_reasoning=show_reasoning)
            else:
                # Use simple chat prompt for sentiment analysis
                sentiment_prompt = f"Please analyze the sentiment of the following text and classify it as positive, negative, or neutral:\n\n{input_data}\n\nSentiment:"
                result = await self.chat(sentiment_prompt, show_reasoning=show_reasoning)
        
        # ==================== 编程类任务 ====================
        elif task == "code":
            # Always use chat with appropriate prompt for code generation
            language = kwargs.get("language", "")
            style = kwargs.get("style", "")
            
            code_prompt = f"Please write code"
            if language:
                code_prompt += f" in {language}"
            code_prompt += f" for the following requirement:\n\n{input_data}\n\n"
            
            if style:
                code_prompt += f"Style requirements: {style}\n\n"
            
            code_prompt += "Please provide clean, working code with comments."
            
            result = await self.chat(code_prompt, show_reasoning=show_reasoning)
        elif task == "explain_code":
            result = await self.explain_code(input_data, kwargs.get("language"))
        elif task == "debug_code":
            result = await self.debug_code(input_data, kwargs.get("language"))
        elif task == "refactor_code":
            result = await self.refactor_code(input_data, kwargs.get("language"), kwargs.get("improvements"))
        
        # ==================== 推理类任务 ====================
        elif task == "reason":
            # Always use chat with appropriate prompt for reasoning
            reasoning_type = kwargs.get("reasoning_type", "")
            
            reason_prompt = f"Please analyze and explain the reasoning behind the following question or topic"
            if reasoning_type:
                reason_prompt += f" using {reasoning_type} reasoning"
            reason_prompt += f":\n\n{input_data}\n\n"
            reason_prompt += "Provide a clear, step-by-step explanation of your reasoning process."
            
            result = await self.chat(reason_prompt, show_reasoning=show_reasoning)
        elif task == "solve":
            # Always use chat with appropriate prompt for problem solving
            problem_type = kwargs.get("problem_type", "")
            
            solve_prompt = f"Please solve the following problem"
            if problem_type:
                solve_prompt += f" (type: {problem_type})"
            solve_prompt += f":\n\n{input_data}\n\n"
            solve_prompt += "Provide a clear solution with step-by-step explanation."
            
            result = await self.chat(solve_prompt, show_reasoning=show_reasoning)
        elif task == "plan":
            result = await self.create_plan(input_data, kwargs.get("plan_type"))
        elif task == "deep_research":
            result = await self.deep_research(input_data, kwargs.get("research_type"), kwargs.get("search_enabled", True))
        
        # ==================== 工具调用类任务 ====================
        elif task == "tool_call":
            result = await self.call_tools(input_data, kwargs.get("available_tools"))
        elif task == "function_call":
            function_name = kwargs.get("function_name")
            if not function_name:
                raise ValueError("function_name is required for function_call task")
            result = await self.call_function(input_data, function_name, kwargs.get("parameters"))
        
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
        
        # Apply output formatting if requested
        if result is not None and output_format:
            # Extract the raw response for formatting
            # If result is a dict with 'message' key, use the message for formatting
            format_input = result
            if isinstance(result, dict) and 'message' in result:
                format_input = result['message']
            
            formatted_result = self.format_structured_output(
                response=format_input,
                output_format=output_format,
                schema=json_schema,
                repair_attempts=format_options.get("repair_attempts", 3)
            )
            
            # If formatting succeeded, return formatted result
            if formatted_result.get("success", False):
                return {
                    "result": formatted_result["data"],
                    "formatted": True,
                    "format": output_format,
                    "original": result
                }
            else:
                # If formatting failed, return original with error info
                return {
                    "result": result,
                    "formatted": False,
                    "format_errors": formatted_result.get("errors", []),
                    "original": result
                }
        
        # Return unformatted result
        return result if result is not None else {"message": "Task completed but returned no result"}
    
    # ==================== 对话类方法 ====================
    
    async def chat(
        self,
        input_data: Union[str, List[Dict[str, str]], Any],
        max_tokens: Optional[int] = None,
        show_reasoning: bool = False
    ) -> Dict[str, Any]:
        """
        对话聊天 - 委托给 ainvoke 方法
        
        Args:
            input_data: 输入消息
            max_tokens: 最大生成token数
            show_reasoning: 是否显示推理过程
            
        Returns:
            Dict containing chat response
        """
        result = await self.ainvoke(input_data, show_reasoning=show_reasoning)
        # Ensure we return a proper response structure
        if result is None:
            logger.warning("ainvoke returned None - this may indicate an implementation issue")
            return {"message": ""}
        
        # Extract content if it's an AIMessage object
        if hasattr(result, 'content'):
            content = result.content
        else:
            content = str(result)
            
        return {"message": content}
    
    # ==================== 文本生成类方法 ====================
    
    async def complete_text(
        self,
        input_data: Union[str, Any],
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        文本补全 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support complete_text task")
    
    async def instruct(
        self,
        input_data: Union[str, Any],
        instruction: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        指令跟随 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support instruct task")
    
    async def generate_text(
        self,
        input_data: Union[str, Any],
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        通用文本生成 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support generate_text task")
    
    async def rewrite_text(
        self,
        input_data: Union[str, Any],
        style: Optional[str] = None,
        tone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文本重写 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support rewrite_text task")
    
    async def summarize_text(
        self,
        input_data: Union[str, Any],
        max_length: Optional[int] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文本摘要 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support summarize_text task")
    
    async def translate_text(
        self,
        input_data: Union[str, Any],
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文本翻译 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support translate_text task")
    
    # ==================== 分析类方法 ====================
    
    async def analyze_text(
        self,
        input_data: Union[str, Any],
        analysis_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文本分析 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support analyze_text task")
    
    async def classify_text(
        self,
        input_data: Union[str, Any],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        文本分类 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support classify_text task")
    
    async def extract_information(
        self,
        input_data: Union[str, Any],
        extract_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        信息提取 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support extract_information task")
    
    async def analyze_sentiment(
        self,
        input_data: Union[str, Any]
    ) -> Dict[str, Any]:
        """
        情感分析 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support analyze_sentiment task")
    
    # ==================== 编程类方法 ====================
    
    async def generate_code(
        self,
        input_data: Union[str, Any],
        language: Optional[str] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        代码生成 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support generate_code task")
    
    async def explain_code(
        self,
        input_data: Union[str, Any],
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        代码解释 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support explain_code task")
    
    async def debug_code(
        self,
        input_data: Union[str, Any],
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        代码调试 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support debug_code task")
    
    async def refactor_code(
        self,
        input_data: Union[str, Any],
        language: Optional[str] = None,
        improvements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        代码重构 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support refactor_code task")
    
    # ==================== 推理类方法 ====================
    
    async def reason_about(
        self,
        input_data: Union[str, Any],
        reasoning_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        推理分析 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support reason_about task")
    
    async def solve_problem(
        self,
        input_data: Union[str, Any],
        problem_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        问题求解 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support solve_problem task")
    
    async def create_plan(
        self,
        input_data: Union[str, Any],
        plan_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        计划制定 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support create_plan task")
    
    async def deep_research(
        self,
        input_data: Union[str, Any],
        research_type: Optional[str] = None,
        search_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        深度研究 - O-series模型专用任务，支持网络搜索和深入分析
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support deep_research task")
    
    # ==================== 工具调用类方法 ====================
    
    async def call_tools(
        self,
        input_data: Union[str, Any],
        available_tools: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        工具调用 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support call_tools task")
    
    async def call_function(
        self,
        input_data: Union[str, Any],
        function_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        函数调用 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support call_function task")
    
    # ==================== 工具绑定和管理 ====================
    
    def bind_tools(self, tools: List[Any], **kwargs) -> 'BaseLLMService':
        """
        Bind tools to this LLM service for function calling
        
        Args:
            tools: List of tools to bind (functions, LangChain tools, etc.)
            **kwargs: Additional tool binding parameters
            
        Returns:
            Self for method chaining
        """
        self._bound_tools = tools
        return self
    
    async def _prepare_tools_for_request(self) -> List[Dict[str, Any]]:
        """准备工具用于请求"""
        if not self._bound_tools:
            return []
        
        schemas, self._tool_mappings = await self.adapter_manager.convert_tools_to_schemas(self._bound_tools)
        return schemas
    
    def _prepare_messages(self, input_data: Union[str, List[Dict[str, str]], Any]) -> List[Dict[str, str]]:
        """使用适配器管理器转换消息格式"""
        return self.adapter_manager.convert_messages(input_data)
    
    def _format_response(self, response: Union[str, Any], original_input: Any) -> Union[str, Any]:
        """使用适配器管理器格式化响应"""
        return self.adapter_manager.format_response(response, original_input)
    
    async def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """使用适配器管理器执行工具调用"""
        return await self.adapter_manager.execute_tool(tool_name, arguments, self._tool_mappings)
    
    @abstractmethod
    async def astream(self, input_data: Union[str, List[Dict[str, str]], Any]) -> AsyncGenerator[str, None]:
        """
        True streaming method that yields tokens one by one as they arrive
        
        Args:
            input_data: Can be:
                - str: Simple text prompt
                - list: Message history like [{"role": "user", "content": "hello"}]
                - Any: LangChain message objects or other formats
            
        Yields:
            Individual tokens as they arrive from the model
        """
        pass
    
    @abstractmethod
    async def ainvoke(self, input_data: Union[str, List[Dict[str, str]], Any], show_reasoning: bool = False) -> Union[str, Any]:
        """
        Universal async invocation method that handles different input types
        
        Args:
            input_data: Can be:
                - str: Simple text prompt
                - list: Message history like [{"role": "user", "content": "hello"}]
                - Any: LangChain message objects or other formats
            show_reasoning: If True and model supports it, show reasoning process
            
        Returns:
            Model response (string for simple cases, object for complex cases)
        """
        pass
    
    def stream(self, input_data: Union[str, List[Dict[str, str]], Any]):
        """
        Synchronous wrapper for astream - returns the async generator
        
        Args:
            input_data: Same as astream
            
        Returns:
            AsyncGenerator that yields tokens
            
        Usage:
            async for token in llm.stream("Hello"):
                print(token, end="", flush=True)
        """
        return self.astream(input_data)
    
    
    def _has_bound_tools(self) -> bool:
        """Check if this service has bound tools"""
        return bool(self._bound_tools)
    
    def _get_bound_tools(self) -> List[Any]:
        """Get the bound tools"""
        return self._bound_tools
    
    @abstractmethod
    def get_token_usage(self) -> Dict[str, Any]:
        """Get cumulative token usage statistics"""
        pass
    
    @abstractmethod
    def get_last_token_usage(self) -> Dict[str, int]:
        """Get token usage from the last request"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources and close connections"""
        pass
    
    def get_last_usage_with_cost(self) -> Dict[str, Any]:
        """Get last request usage with cost information"""
        usage = self.get_last_token_usage()
        
        # Calculate cost using centralized pricing manager
        cost = self.model_manager.calculate_cost(
            provider=self.provider_name,
            model_name=self.model_name,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0)
        )
        
        return {
            **usage,
            "cost_usd": cost,
            "model": self.model_name,
            "provider": self.provider_name
        }
    
    async def _track_llm_usage(
        self,
        user_id: str,  # REQUIRED: User ID from gateway authentication
        operation: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Track LLM usage using the unified BaseService billing system

        Args:
            operation: Operation type (e.g., "chat", "generate")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Additional metadata
            user_id: User ID for billing (from gateway auth)

        Returns:
            Cost in USD
        """
        from isa_model.core.types import ServiceType

        await self._publish_billing_event(
            user_id=user_id,
            service_type=ServiceType.LLM,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata=metadata
        )

        # Return calculated cost
        if input_tokens is not None and output_tokens is not None:
            return self.model_manager.calculate_cost(
                provider=self.provider_name,
                model_name=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        return 0.0
    
    # ==================== JSON OUTPUT AND FORMATTING METHODS ====================
    
    def format_structured_output(
        self, 
        response: Union[str, Any], 
        output_format: str = "json",
        schema: Optional[Dict] = None,
        repair_attempts: int = 3
    ) -> Dict[str, Any]:
        """
        Format response as structured output (JSON, etc.)
        
        Args:
            response: Raw response from model
            output_format: Desired output format ("json", "code", "structured")
            schema: Optional JSON schema for validation
            repair_attempts: Number of JSON repair attempts
            
        Returns:
            Dict with formatted output and metadata
        """
        if output_format == "json":
            if isinstance(response, str):
                return self.text_processor.extract_json_from_text(response, schema, repair_attempts)
            else:
                # Handle response objects with content attribute
                content = getattr(response, 'content', str(response))
                return self.text_processor.extract_json_from_text(content, schema, repair_attempts)
        
        elif output_format == "code":
            content = response if isinstance(response, str) else getattr(response, 'content', str(response))
            code_blocks = self.text_processor.extract_code_blocks(content)
            return {
                "success": True,
                "data": code_blocks,
                "method": "code_block_extraction",
                "errors": []
            }
        
        elif output_format == "structured":
            # Use ResponseParser for general structured parsing
            content = response if isinstance(response, str) else getattr(response, 'content', str(response))
            parsed = self.response_parser.parse_structured_response(content, "json")
            if parsed:
                return {
                    "success": True,
                    "data": parsed,
                    "method": "structured_parsing",
                    "errors": []
                }
            else:
                return {
                    "success": False,
                    "data": content,
                    "method": "raw_fallback",
                    "errors": ["Failed to parse as structured output"]
                }
        
        # Fallback: return raw response
        return {
            "success": True,
            "data": response,
            "method": "raw_output",
            "errors": []
        }
    
    def create_json_prompt(
        self, 
        base_prompt: str, 
        json_schema: Optional[Dict] = None,
        output_instructions: Optional[str] = None
    ) -> str:
        """
        Create a prompt that requests JSON output
        
        Args:
            base_prompt: The base prompt content
            json_schema: Optional JSON schema to include in prompt
            output_instructions: Custom output format instructions
            
        Returns:
            Enhanced prompt requesting JSON output
        """
        if output_instructions:
            json_instruction = output_instructions
        else:
            json_instruction = LLMPromptTemplates.OUTPUT_FORMATS["json"]
        
        if json_schema:
            schema_text = f"\n\nPlease format your response according to this JSON schema:\n```json\n{json.dumps(json_schema, indent=2)}\n```"
            return f"{base_prompt}{schema_text}\n\n{json_instruction}"
        else:
            return f"{base_prompt}\n\n{json_instruction}"
    
    def create_structured_prompt(
        self, 
        task_type: str,
        content: str,
        output_format: str = "json",
        **kwargs
    ) -> str:
        """
        Create a structured prompt using LLMPrompts templates
        
        Args:
            task_type: Type of task (from LLMPrompts methods)
            content: Main content/input
            output_format: Desired output format
            **kwargs: Additional arguments for the prompt template
            
        Returns:
            Formatted prompt string
        """
        try:
            # Get the appropriate prompt template
            if hasattr(self.llm_prompts, f"{task_type}_prompt"):
                method = getattr(self.llm_prompts, f"{task_type}_prompt")
                base_prompt = method(content, **kwargs)
            else:
                # Fallback to generic prompt
                base_prompt = f"Please {task_type} the following:\n\n{content}"
            
            # Add output format instructions
            if output_format in LLMPromptTemplates.OUTPUT_FORMATS:
                format_instruction = LLMPromptTemplates.OUTPUT_FORMATS[output_format]
                return f"{base_prompt}\n\n{format_instruction}"
            
            return base_prompt
            
        except Exception as e:
            logger.warning(f"Failed to create structured prompt: {e}")
            return f"Please {task_type} the following:\n\n{content}"
    
    def count_tokens(self, text: Union[str, List[Dict[str, str]]]) -> int:
        """
        Count tokens in text or message list
        
        Args:
            text: String or message list to count tokens for
            
        Returns:
            Number of tokens
        """
        if isinstance(text, str):
            return self.token_counter.count_tokens(text)
        elif isinstance(text, list):
            return self.token_counter.count_messages_tokens(text)
        else:
            return self.token_counter.count_tokens(str(text))
    
    def truncate_to_token_limit(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token limit
        
        Args:
            text: Text to truncate
            max_tokens: Maximum number of tokens
            
        Returns:
            Truncated text
        """
        return self.token_counter.truncate_text(text, max_tokens)
    
    def split_text_by_tokens(self, text: str, chunk_size: int, overlap: int = 0) -> List[str]:
        """
        Split text into chunks by token count
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk in tokens
            overlap: Number of overlapping tokens between chunks
            
        Returns:
            List of text chunks
        """
        return self.token_counter.split_text_by_tokens(text, chunk_size, overlap)

    # ==================== METADATA AND UTILITY METHODS ====================
    
    def get_supported_tasks(self) -> List[str]:
        """
        获取provider支持的任务列表
        
        Returns:
            List of supported task names
        """
        supported = []
        
        # 检查各类任务支持情况
        method_task_map = {
            # 对话类
            'chat': 'chat',
            'complete_text': 'complete',
            'instruct': 'instruct',
            # 文本生成类
            'generate_text': 'generate',
            'rewrite_text': 'rewrite',
            'summarize_text': 'summarize',
            'translate_text': 'translate',
            # 分析类
            'analyze_text': 'analyze',
            'classify_text': 'classify',
            'extract_information': 'extract',
            'analyze_sentiment': 'sentiment',
            # 编程类
            'generate_code': 'code',
            'explain_code': 'explain_code',
            'debug_code': 'debug_code',
            'refactor_code': 'refactor_code',
            # 推理类
            'reason_about': 'reason',
            'solve_problem': 'solve',
            'create_plan': 'plan',
            'deep_research': 'deep_research',
            # 工具调用类
            'call_tools': 'tool_call',
            'call_function': 'function_call'
        }
        
        for method_name, task_name in method_task_map.items():
            if hasattr(self, method_name):
                # 检查是否是默认实现还是provider自己的实现
                try:
                    import inspect
                    source = inspect.getsource(getattr(self, method_name))
                    if 'NotImplementedError' not in source:
                        supported.append(task_name)
                except:
                    # 如果无法检查源码，假设支持
                    supported.append(task_name)
                    
        return supported
    
    def get_supported_languages(self) -> List[str]:
        """
        获取支持的编程语言列表 - Provider应该实现
        
        Returns:
            List of supported programming languages
        """
        return [
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 
            'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala',
            'r', 'matlab', 'sql', 'html', 'css', 'bash', 'powershell'
        ]  # 通用语言支持
    
    def get_max_context_length(self) -> int:
        """
        获取最大上下文长度 - Provider应该实现
        
        Returns:
            Maximum context length in tokens
        """
        return self.max_tokens or 4096  # 默认值
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的输入格式 - Provider应该实现
        
        Returns:
            List of supported input formats
        """
        return ['text', 'json', 'markdown', 'code']  # 通用格式
    
    def supports_streaming(self) -> bool:
        """
        检查是否支持流式输出
        
        Returns:
            True if streaming is supported
        """
        return self.streaming
    
    def supports_function_calling(self) -> bool:
        """
        检查是否支持函数调用
        
        Returns:
            True if function calling is supported
        """
        return hasattr(self, 'call_tools') or hasattr(self, 'call_function')
    
    def get_temperature_range(self) -> Dict[str, float]:
        """
        获取温度参数范围
        
        Returns:
            Dict with min and max temperature values
        """
        return {"min": 0.0, "max": 2.0, "default": self.temperature}
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        获取provider信息
        
        Returns:
            Dict containing provider information
        """
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "streaming": self.streaming,
            "supports_tools": self.supports_function_calling(),
            "supported_tasks": self.get_supported_tasks(),
            "supported_languages": self.get_supported_languages(),
            "max_context_length": self.get_max_context_length()
        }
