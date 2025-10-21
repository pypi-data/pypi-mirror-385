#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM工具函数和实用程序
提供LLM服务的通用工具函数，包括文本处理、token计算、响应解析等
"""

import re
import json
import tiktoken
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

logger = logging.getLogger(__name__)

class TokenCounter:
    """Token计数器"""
    
    def __init__(self, model_name: str = "gpt-4"):
        """初始化token计数器"""
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # 如果模型不支持，使用默认编码
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        return len(self.encoding.encode(text))
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """计算消息列表的总token数量"""
        total_tokens = 0
        for message in messages:
            # 每个消息有固定的开销（role等）
            total_tokens += 4  # 每个消息的基本开销
            for key, value in message.items():
                total_tokens += self.count_tokens(str(value))
        total_tokens += 2  # 对话的基本开销
        return total_tokens
    
    def truncate_text(self, text: str, max_tokens: int) -> str:
        """截断文本以适应token限制"""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)
    
    def split_text_by_tokens(self, text: str, chunk_size: int, overlap: int = 0) -> List[str]:
        """按token数量分割文本"""
        tokens = self.encoding.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunks.append(self.encoding.decode(chunk_tokens))
            
            if end >= len(tokens):
                break
            
            start = end - overlap
        
        return chunks

class TextProcessor:
    """文本处理工具"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本，移除多余的空白字符"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除首尾空白
        text = text.strip()
        return text
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[Dict[str, str]]:
        """从文本中提取代码块"""
        code_pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(code_pattern, text, re.DOTALL)
        
        code_blocks = []
        for language, code in matches:
            code_blocks.append({
                "language": language or "text",
                "code": code.strip()
            })
        
        return code_blocks
    
    @staticmethod
    def extract_json_from_text(text: str, schema: Optional[Dict] = None, repair_attempts: int = 3) -> Dict[str, Any]:
        """Enhanced JSON extraction with validation and error recovery"""
        result = {
            "success": False,
            "data": None,
            "errors": [],
            "method": None,
            "repaired": False
        }
        
        extraction_methods = [
            ("direct_parse", TextProcessor._try_direct_json_parse),
            ("json_code_block", TextProcessor._try_json_code_block),
            ("first_json_object", TextProcessor._try_first_json_object),
            ("between_braces", TextProcessor._try_between_braces),
            ("multiple_objects", TextProcessor._try_multiple_json_objects),
            ("yaml_like", TextProcessor._try_yaml_like_parsing)
        ]
        
        for method_name, extraction_func in extraction_methods:
            try:
                extracted_data = extraction_func(text)
                if extracted_data is not None:
                    # Validate against schema if provided
                    if schema:
                        validation_result = TextProcessor._validate_json_schema(extracted_data, schema)
                        if validation_result["valid"]:
                            result.update({
                                "success": True,
                                "data": extracted_data,
                                "method": method_name
                            })
                            return result
                        else:
                            result["errors"].append(f"{method_name}: {validation_result['error']}")
                    else:
                        result.update({
                            "success": True,
                            "data": extracted_data,
                            "method": method_name
                        })
                        return result
            except Exception as e:
                result["errors"].append(f"{method_name}: {str(e)}")
                continue
        
        # If all methods failed, try repair attempts
        if repair_attempts > 0:
            repair_result = TextProcessor._attempt_json_repair(text, schema, repair_attempts)
            if repair_result["success"]:
                result.update(repair_result)
                result["repaired"] = True
                return result
            else:
                result["errors"].extend(repair_result["errors"])
        
        return result
    
    @staticmethod
    def _try_direct_json_parse(text: str) -> Optional[Dict[str, Any]]:
        """Try to parse text directly as JSON"""
        text = text.strip()
        if not text:
            return None
        return json.loads(text)
    
    @staticmethod
    def _try_json_code_block(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from code blocks"""
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```JSON\s*(.*?)\s*```',
            r'```\s*(\{.*?\})\s*```'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                json_str = match.group(1).strip()
                if json_str:
                    return json.loads(json_str)
        
        return None
    
    @staticmethod
    def _try_first_json_object(text: str) -> Optional[Dict[str, Any]]:
        """Find and parse the first JSON object in text"""
        # Look for the first { and find its matching }
        start_idx = text.find('{')
        if start_idx == -1:
            return None
        
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i, char in enumerate(text[start_idx:], start_idx):
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_str = text[start_idx:i+1]
                        return json.loads(json_str)
        
        return None
    
    @staticmethod
    def _try_between_braces(text: str) -> Optional[Dict[str, Any]]:
        """Extract content between first { and last }"""
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_str = text[first_brace:last_brace+1]
            return json.loads(json_str)
        
        return None
    
    @staticmethod
    def _try_multiple_json_objects(text: str) -> Optional[List[Dict[str, Any]]]:
        """Try to extract multiple JSON objects"""
        objects = []
        remaining_text = text
        
        while True:
            try:
                obj = TextProcessor._try_first_json_object(remaining_text)
                if obj is None:
                    break
                objects.append(obj)
                
                # Find where this object ends and continue
                obj_str = json.dumps(obj)
                obj_end = remaining_text.find('}')
                if obj_end == -1:
                    break
                remaining_text = remaining_text[obj_end+1:]
                
            except:
                break
        
        return objects if objects else None
    
    @staticmethod
    def _try_yaml_like_parsing(text: str) -> Optional[Dict[str, Any]]:
        """Try to parse YAML-like structures and convert to JSON"""
        try:
            # Simple YAML-like parsing for basic cases
            lines = text.strip().split('\n')
            result = {}
            
            for line in lines:
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    key = key.strip().strip('"\'')
                    value = value.strip().strip('"\'')
                    
                    # Try to convert value to appropriate type
                    if value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'
                    elif value.isdigit():
                        value = int(value)
                    elif '.' in value and value.replace('.', '').isdigit():
                        value = float(value)
                    
                    result[key] = value
            
            return result if result else None
        except:
            return None
    
    @staticmethod
    def _validate_json_schema(data: Any, schema: Dict) -> Dict[str, Any]:
        """Validate JSON data against a simple schema"""
        try:
            # Try jsonschema library first
            try:
                import jsonschema
                jsonschema.validate(instance=data, schema=schema)
                return {"valid": True, "error": None}
            except ImportError:
                # Fallback to basic validation
                return TextProcessor._basic_schema_validation(data, schema)
            except jsonschema.ValidationError as e:
                return {"valid": False, "error": str(e)}
                
        except Exception as e:
            return {"valid": False, "error": f"Schema validation error: {str(e)}"}
    
    @staticmethod
    def _basic_schema_validation(data: Any, schema: Dict) -> Dict[str, Any]:
        """Basic schema validation without jsonschema library"""
        try:
            if "type" in schema:
                expected_type = schema["type"]
                if expected_type == "object" and not isinstance(data, dict):
                    return {"valid": False, "error": f"Expected object, got {type(data).__name__}"}
                elif expected_type == "array" and not isinstance(data, list):
                    return {"valid": False, "error": f"Expected array, got {type(data).__name__}"}
                elif expected_type == "string" and not isinstance(data, str):
                    return {"valid": False, "error": f"Expected string, got {type(data).__name__}"}
                elif expected_type == "number" and not isinstance(data, (int, float)):
                    return {"valid": False, "error": f"Expected number, got {type(data).__name__}"}
                elif expected_type == "boolean" and not isinstance(data, bool):
                    return {"valid": False, "error": f"Expected boolean, got {type(data).__name__}"}
            
            if "required" in schema and isinstance(data, dict):
                for required_field in schema["required"]:
                    if required_field not in data:
                        return {"valid": False, "error": f"Missing required field: {required_field}"}
            
            return {"valid": True, "error": None}
        except Exception as e:
            return {"valid": False, "error": f"Basic validation error: {str(e)}"}
    
    @staticmethod
    def _attempt_json_repair(text: str, schema: Optional[Dict], max_attempts: int) -> Dict[str, Any]:
        """Attempt to repair malformed JSON"""
        result = {"success": False, "data": None, "errors": []}
        
        repair_strategies = [
            TextProcessor._repair_missing_quotes,
            TextProcessor._repair_trailing_commas,
            TextProcessor._repair_unescaped_quotes,
            TextProcessor._repair_incomplete_objects
        ]
        
        current_text = text
        
        for attempt in range(max_attempts):
            for strategy_name, repair_func in [
                ("missing_quotes", TextProcessor._repair_missing_quotes),
                ("trailing_commas", TextProcessor._repair_trailing_commas),
                ("unescaped_quotes", TextProcessor._repair_unescaped_quotes),
                ("incomplete_objects", TextProcessor._repair_incomplete_objects)
            ]:
                try:
                    repaired_text = repair_func(current_text)
                    if repaired_text != current_text:
                        # Try to parse the repaired text
                        try:
                            repaired_data = json.loads(repaired_text)
                            
                            # Validate if schema provided
                            if schema:
                                validation = TextProcessor._validate_json_schema(repaired_data, schema)
                                if validation["valid"]:
                                    result.update({
                                        "success": True,
                                        "data": repaired_data,
                                        "method": f"repair_{strategy_name}"
                                    })
                                    return result
                                else:
                                    result["errors"].append(f"repair_{strategy_name}: {validation['error']}")
                            else:
                                result.update({
                                    "success": True,
                                    "data": repaired_data,
                                    "method": f"repair_{strategy_name}"
                                })
                                return result
                        except json.JSONDecodeError as e:
                            result["errors"].append(f"repair_{strategy_name}: Still invalid JSON after repair - {str(e)}")
                        
                        current_text = repaired_text
                except Exception as e:
                    result["errors"].append(f"repair_{strategy_name}: Repair attempt failed - {str(e)}")
        
        return result
    
    @staticmethod
    def _repair_missing_quotes(text: str) -> str:
        """Add quotes around unquoted keys"""
        # Simple regex to add quotes around keys
        pattern = r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:'
        return re.sub(pattern, r'\1"\2":', text)
    
    @staticmethod
    def _repair_trailing_commas(text: str) -> str:
        """Remove trailing commas"""
        # Remove trailing commas before } or ]
        text = re.sub(r',\s*([}\]])', r'\1', text)
        return text
    
    @staticmethod
    def _repair_unescaped_quotes(text: str) -> str:
        """Escape unescaped quotes in strings"""
        # This is a simplified approach - in practice this is quite complex
        # Replace unescaped quotes that are clearly inside string values
        return text.replace('\\"', '"').replace('"', '\\"').replace('\\\\"', '\\"')
    
    @staticmethod
    def _repair_incomplete_objects(text: str) -> str:
        """Try to complete incomplete JSON objects"""
        text = text.strip()
        
        # Add missing closing braces
        open_braces = text.count('{')
        close_braces = text.count('}')
        if open_braces > close_braces:
            text += '}' * (open_braces - close_braces)
        
        # Add missing closing brackets
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        if open_brackets > close_brackets:
            text += ']' * (open_brackets - close_brackets)
        
        return text
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """将文本分割为句子"""
        # 简单的句子分割，基于句号、问号、感叹号
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def extract_entities(text: str, entity_types: List[str] = None) -> Dict[str, List[str]]:
        """提取文本中的实体（简单版本）"""
        entities = {}
        
        if not entity_types:
            entity_types = ["email", "url", "phone", "date"]
        
        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        }
        
        for entity_type in entity_types:
            if entity_type in patterns:
                matches = re.findall(patterns[entity_type], text)
                entities[entity_type] = matches
        
        return entities

class ResponseParser:
    """响应解析器"""
    
    @staticmethod
    def parse_structured_response(response: str, expected_format: str = "json") -> Any:
        """解析结构化响应"""
        if expected_format == "json":
            return TextProcessor.extract_json_from_text(response)
        elif expected_format == "code":
            return TextProcessor.extract_code_blocks(response)
        else:
            return response
    
    @staticmethod
    def parse_classification_response(response: str, categories: List[str]) -> Tuple[str, float]:
        """解析分类响应，返回类别和置信度"""
        response_lower = response.lower()
        
        # 查找匹配的类别
        for category in categories:
            if category.lower() in response_lower:
                # 尝试提取置信度
                confidence_pattern = r'(\d+(?:\.\d+)?)%|confidence[:\s]*(\d+(?:\.\d+)?)'
                match = re.search(confidence_pattern, response_lower)
                confidence = float(match.group(1) or match.group(2)) / 100 if match else 0.8
                return category, confidence
        
        # 如果没有找到匹配的类别，返回最可能的一个
        return categories[0] if categories else "unknown", 0.5
    
    @staticmethod
    def parse_sentiment_response(response: str) -> Tuple[str, float]:
        """解析情感分析响应"""
        response_lower = response.lower()
        
        # 定义情感关键词
        sentiments = {
            "positive": ["positive", "good", "great", "excellent", "happy", "pleased"],
            "negative": ["negative", "bad", "terrible", "awful", "sad", "disappointed"],
            "neutral": ["neutral", "okay", "average", "mixed", "unclear"]
        }
        
        # 查找匹配的情感
        for sentiment, keywords in sentiments.items():
            for keyword in keywords:
                if keyword in response_lower:
                    # 尝试提取置信度
                    confidence_pattern = r'(\d+(?:\.\d+)?)%|confidence[:\s]*(\d+(?:\.\d+)?)'
                    match = re.search(confidence_pattern, response_lower)
                    confidence = float(match.group(1) or match.group(2)) / 100 if match else 0.7
                    return sentiment, confidence
        
        return "neutral", 0.5

class LLMMetrics:
    """
    LLM性能指标计算工具

    注意：计费和使用跟踪功能已经统一到BaseService中的_publish_billing_event()方法。
    LLM服务应该使用BaseLLMService中的_track_llm_usage()方法来跟踪使用情况。
    """
    
    @staticmethod  
    def calculate_latency_metrics(start_time: float, end_time: float, token_count: int) -> Dict[str, float]:
        """计算延迟指标"""
        total_time = end_time - start_time
        tokens_per_second = token_count / total_time if total_time > 0 else 0
        
        return {
            "total_time": total_time,
            "tokens_per_second": tokens_per_second,
            "ms_per_token": (total_time * 1000) / token_count if token_count > 0 else 0
        }
    

def validate_model_response(response: Any, expected_type: type = str) -> bool:
    """验证模型响应是否符合预期类型"""
    return isinstance(response, expected_type)

def format_chat_history(messages: List[Dict[str, str]], max_history: int = 10) -> List[Dict[str, str]]:
    """格式化聊天历史，保留最近的消息"""
    if len(messages) <= max_history:
        return messages
    
    # 保留系统消息和最近的消息
    system_messages = [msg for msg in messages if msg.get("role") == "system"]
    other_messages = [msg for msg in messages if msg.get("role") != "system"]
    
    recent_messages = other_messages[-max_history+len(system_messages):]
    return system_messages + recent_messages

def extract_function_calls(response: str) -> List[Dict[str, Any]]:
    """从响应中提取函数调用"""
    function_calls = []
    
    # 查找JSON格式的函数调用
    json_pattern = r'\{[^{}]*"function_name"[^{}]*\}'
    matches = re.findall(json_pattern, response)
    
    for match in matches:
        try:
            call = json.loads(match)
            if "function_name" in call:
                function_calls.append(call)
        except json.JSONDecodeError:
            continue
    
    return function_calls

def merge_streaming_tokens(tokens: List[str]) -> str:
    """合并流式token为完整文本"""
    return ''.join(tokens)

def detect_language(text: str) -> str:
    """检测文本语言（简单版本）"""
    # 简单的语言检测，基于字符模式
    if re.search(r'[\u4e00-\u9fff]', text):
        return "zh"
    elif re.search(r'[а-яё]', text, re.IGNORECASE):
        return "ru"
    elif re.search(r'[ひらがなカタカナ]', text):
        return "ja"
    elif re.search(r'[가-힣]', text):
        return "ko"
    else:
        return "en"