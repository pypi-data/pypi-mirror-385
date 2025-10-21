#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM通用提示词模板和工具函数
提供标准化的提示词模板，用于不同类型的LLM任务
"""

from typing import Dict, List, Optional, Any
import json

class LLMPrompts:
    """LLM提示词模板管理器"""
    
    # ==================== 对话类提示词 ====================
    
    @staticmethod
    def chat_prompt(user_message: str, system_message: Optional[str] = None) -> List[Dict[str, str]]:
        """生成标准对话提示词格式"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": user_message})
        return messages
    
    @staticmethod
    def completion_prompt(text: str, instruction: Optional[str] = None) -> str:
        """生成文本补全提示词"""
        if instruction:
            return f"{instruction}\n\n{text}"
        return text
    
    @staticmethod
    def instruct_prompt(task: str, content: str, format_instruction: Optional[str] = None) -> str:
        """生成指令跟随提示词"""
        prompt = f"Task: {task}\n\nContent:\n{content}\n\n"
        if format_instruction:
            prompt += f"Output Format: {format_instruction}\n\n"
        prompt += "Response:"
        return prompt
    
    # ==================== 文本生成类提示词 ====================
    
    @staticmethod
    def rewrite_prompt(text: str, style: Optional[str] = None, tone: Optional[str] = None) -> str:
        """生成文本重写提示词"""
        prompt = f"Please rewrite the following text"
        if style:
            prompt += f" in {style} style"
        if tone:
            prompt += f" with a {tone} tone"
        prompt += f":\n\n{text}\n\nRewritten text:"
        return prompt
    
    @staticmethod
    def summarize_prompt(text: str, max_length: Optional[int] = None, style: Optional[str] = None) -> str:
        """生成文本摘要提示词"""
        prompt = f"Please summarize the following text"
        if max_length:
            prompt += f" in no more than {max_length} words"
        if style:
            prompt += f" in {style} style"
        prompt += f":\n\n{text}\n\nSummary:"
        return prompt
    
    @staticmethod
    def translate_prompt(text: str, target_language: str, source_language: Optional[str] = None) -> str:
        """生成翻译提示词"""
        prompt = f"Please translate the following text"
        if source_language:
            prompt += f" from {source_language}"
        prompt += f" to {target_language}:\n\n{text}\n\nTranslation:"
        return prompt
    
    # ==================== 分析类提示词 ====================
    
    @staticmethod
    def analyze_prompt(text: str, analysis_type: Optional[str] = None) -> str:
        """生成文本分析提示词"""
        if analysis_type:
            prompt = f"Please perform {analysis_type} analysis on the following text:\n\n{text}\n\nAnalysis:"
        else:
            prompt = f"Please analyze the following text:\n\n{text}\n\nAnalysis:"
        return prompt
    
    @staticmethod
    def classify_prompt(text: str, categories: Optional[List[str]] = None) -> str:
        """生成文本分类提示词"""
        prompt = f"Please classify the following text"
        if categories:
            prompt += f" into one of these categories: {', '.join(categories)}"
        prompt += f":\n\n{text}\n\nClassification:"
        return prompt
    
    @staticmethod
    def extract_prompt(text: str, extract_type: Optional[str] = None) -> str:
        """生成信息提取提示词"""
        if extract_type:
            prompt = f"Please extract {extract_type} from the following text:\n\n{text}\n\nExtracted {extract_type}:"
        else:
            prompt = f"Please extract key information from the following text:\n\n{text}\n\nExtracted information:"
        return prompt
    
    @staticmethod
    def sentiment_prompt(text: str) -> str:
        """生成情感分析提示词"""
        return f"Please analyze the sentiment of the following text and classify it as positive, negative, or neutral:\n\n{text}\n\nSentiment:"
    
    # ==================== 编程类提示词 ====================
    
    @staticmethod
    def code_generation_prompt(description: str, language: Optional[str] = None, style: Optional[str] = None) -> str:
        """生成代码生成提示词"""
        prompt = f"Please write code"
        if language:
            prompt += f" in {language}"
        prompt += f" for the following requirement:\n\n{description}\n\n"
        if style:
            prompt += f"Code style: {style}\n\n"
        prompt += "Code:"
        return prompt
    
    @staticmethod
    def code_explanation_prompt(code: str, language: Optional[str] = None) -> str:
        """生成代码解释提示词"""
        prompt = f"Please explain the following"
        if language:
            prompt += f" {language}"
        prompt += f" code:\n\n```{language or ''}\n{code}\n```\n\nExplanation:"
        return prompt
    
    @staticmethod
    def code_debug_prompt(code: str, language: Optional[str] = None, error: Optional[str] = None) -> str:
        """生成代码调试提示词"""
        prompt = f"Please debug the following"
        if language:
            prompt += f" {language}"
        prompt += f" code:\n\n```{language or ''}\n{code}\n```\n\n"
        if error:
            prompt += f"Error message: {error}\n\n"
        prompt += "Fixed code:"
        return prompt
    
    @staticmethod
    def code_refactor_prompt(code: str, language: Optional[str] = None, improvements: Optional[List[str]] = None) -> str:
        """生成代码重构提示词"""
        prompt = f"Please refactor the following"
        if language:
            prompt += f" {language}"
        prompt += f" code"
        if improvements:
            prompt += f" with these improvements: {', '.join(improvements)}"
        prompt += f":\n\n```{language or ''}\n{code}\n```\n\nRefactored code:"
        return prompt
    
    # ==================== 推理类提示词 ====================
    
    @staticmethod
    def reasoning_prompt(question: str, reasoning_type: Optional[str] = None) -> str:
        """生成推理分析提示词"""
        if reasoning_type:
            prompt = f"Please use {reasoning_type} reasoning to answer the following question:\n\n{question}\n\nReasoning and answer:"
        else:
            prompt = f"Please think step by step and answer the following question:\n\n{question}\n\nReasoning and answer:"
        return prompt
    
    @staticmethod
    def chain_of_thought_prompt(
        problem: str,
        domain: Optional[str] = None,
        format_json: bool = False,
        include_confidence: bool = False
    ) -> str:
        """Generate Chain-of-Thought reasoning prompt with structured output"""
        
        domain_context = ""
        if domain:
            domain_context = f" in the {domain} domain"
        
        if format_json:
            prompt = f"""Solve the following problem{domain_context} using step-by-step reasoning.

Problem: {problem}

Please provide your response in the following JSON format:
{{
    "reasoning_steps": [
        {{
            "step": 1,
            "description": "Brief description of this step",
            "thinking": "Detailed explanation of your thought process",
            "result": "What you conclude from this step"
        }}
    ],
    "final_answer": "Your final answer",
    "reasoning_chain": "Summary of your complete reasoning process"
"""
            
            if include_confidence:
                prompt += ',\n    "confidence_score": 0.85,\n    "confidence_explanation": "Why you have this level of confidence"'
            
            prompt += "\n}\n\nResponse:"
        else:
            prompt = f"""Solve the following problem{domain_context} using step-by-step reasoning.

Problem: {problem}

Please structure your response as follows:

**Step-by-Step Reasoning:**

Step 1: [Brief description]
- Thinking: [Detailed explanation]
- Result: [What you conclude]

Step 2: [Brief description]
- Thinking: [Detailed explanation]
- Result: [What you conclude]

[Continue for all steps...]

**Final Answer:**
[Your final answer]

**Reasoning Summary:**
[Brief summary of your complete reasoning process]
"""

            if include_confidence:
                prompt += "\n**Confidence Assessment:**\n[Your confidence level and explanation]\n"
            
            prompt += "\nResponse:"
        
        return prompt
    
    @staticmethod
    def tree_of_thoughts_prompt(
        problem: str,
        num_branches: int = 3,
        depth_levels: int = 3,
        format_json: bool = True
    ) -> str:
        """Generate Tree-of-Thoughts reasoning prompt for complex problem solving"""
        
        if format_json:
            prompt = f"""Solve the following complex problem using Tree-of-Thoughts reasoning. Generate {num_branches} different approaches and evaluate them through {depth_levels} levels of thinking.

Problem: {problem}

Please structure your response in JSON format:

{{
    "problem_analysis": "Initial understanding and breakdown of the problem",
    "thought_tree": [
        {{
            "approach": 1,
            "initial_thought": "First approach description",
            "levels": [
                {{
                    "level": 1,
                    "thoughts": ["Thought 1", "Thought 2", "Thought 3"],
                    "evaluations": ["Evaluation of thought 1", "Evaluation of thought 2", "Evaluation of thought 3"],
                    "best_thought": "Selected best thought with reasoning"
                }}
            ],
            "final_conclusion": "Where this approach leads",
            "viability_score": 0.8
        }}
    ],
    "best_approach": {{
        "approach_number": 1,
        "reasoning": "Why this approach is best",
        "final_answer": "The solution"
    }},
    "alternative_solutions": ["Other possible solutions"],
    "confidence_assessment": "Overall confidence in the solution"
}}

Response:"""
        else:
            prompt = f"""Solve the following complex problem using Tree-of-Thoughts reasoning. Generate {num_branches} different approaches and evaluate them through {depth_levels} levels of thinking.

Problem: {problem}

**Problem Analysis:**
[Initial understanding and breakdown]

**Approach 1:**
- Initial Thought: [Description]
- Level 1 Exploration:
  - Thought A: [Details] → Evaluation: [Assessment]
  - Thought B: [Details] → Evaluation: [Assessment]  
  - Thought C: [Details] → Evaluation: [Assessment]
  - Best: [Selected thought with reasoning]
- [Continue for {depth_levels} levels]
- Final Conclusion: [Where this approach leads]
- Viability: [Score/Assessment]

[Repeat for {num_branches} approaches]

**Best Approach Selection:**
- Chosen Approach: [Number and reasoning]
- Final Answer: [Solution]

**Alternative Solutions:**
[Other viable options]

**Confidence Assessment:**
[Overall confidence and reasoning]

Response:"""
        
        return prompt
    
    @staticmethod
    def step_back_reasoning_prompt(
        problem: str,
        domain: Optional[str] = None,
        include_principles: bool = True
    ) -> str:
        """Generate Step-Back reasoning prompt for principle-based problem solving"""
        
        domain_context = f" in {domain}" if domain else ""
        
        prompt = f"""Solve the following problem{domain_context} using step-back reasoning. First identify the underlying principles, then apply them to solve the specific problem.

Problem: {problem}

Please structure your response as follows:

**Step 1: Step Back - Identify General Principles**
What are the fundamental principles, concepts, or rules that apply to this type of problem?

**Step 2: Connect Principles to Problem**  
How do these general principles relate to the specific problem at hand?

**Step 3: Apply Principles**
Use the identified principles to work through the problem systematically.

**Step 4: Verify Solution**
Check if your solution aligns with the fundamental principles.

**Final Answer:**
[Your solution]

"""
        
        if include_principles:
            prompt += "**Principle Summary:**\n[Key principles used in solving this problem]\n\n"
        
        prompt += "Response:"
        
        return prompt
    
    @staticmethod
    def analogical_reasoning_prompt(
        problem: str,
        include_multiple_analogies: bool = True,
        format_structured: bool = True
    ) -> str:
        """Generate analogical reasoning prompt using similar problems/situations"""
        
        if format_structured:
            prompt = f"""Solve the following problem using analogical reasoning. Find similar problems or situations that can guide your thinking.

Problem: {problem}

**Step 1: Find Analogies**
Think of 2-3 similar problems, situations, or concepts that share structural similarities with this problem.

Analogy 1: [Description]
- Similarities: [How it's similar to the current problem]
- Key insights: [What can be learned from this analogy]

Analogy 2: [Description]
- Similarities: [How it's similar to the current problem] 
- Key insights: [What can be learned from this analogy]

{f'''Analogy 3: [Description]
- Similarities: [How it's similar to the current problem]
- Key insights: [What can be learned from this analogy]''' if include_multiple_analogies else ''}

**Step 2: Extract Patterns**
What common patterns or principles emerge from these analogies?

**Step 3: Apply to Current Problem**
How can the insights from these analogies be applied to solve the current problem?

**Step 4: Adapt and Refine** 
What modifications are needed to account for differences between the analogies and current problem?

**Final Answer:**
[Your solution based on analogical reasoning]

Response:"""
        else:
            prompt = f"""Solve this problem by thinking of similar situations: {problem}

Find analogous problems or situations, extract useful patterns, and apply them here.

Response:"""
        
        return prompt
    
    @staticmethod 
    def multi_perspective_reasoning_prompt(
        problem: str,
        perspectives: Optional[List[str]] = None,
        synthesis_required: bool = True
    ) -> str:
        """Generate multi-perspective reasoning prompt to consider different viewpoints"""
        
        if not perspectives:
            perspectives = [
                "practical/pragmatic",
                "theoretical/analytical", 
                "creative/innovative",
                "critical/skeptical",
                "ethical/moral"
            ]
        
        prompt = f"""Analyze and solve the following problem from multiple perspectives to gain a comprehensive understanding.

Problem: {problem}

"""
        
        for i, perspective in enumerate(perspectives, 1):
            prompt += f"""**Perspective {i}: {perspective.title()}**
From this viewpoint:
- How would you understand the problem?
- What solution approach would you take?
- What are the key considerations?
- What would be your recommended action?

"""
        
        if synthesis_required:
            prompt += f"""**Synthesis & Integration**
- Compare and contrast the insights from different perspectives
- Identify areas of agreement and disagreement
- Synthesize the best elements from each perspective
- Develop a balanced, comprehensive solution

**Final Integrated Solution:**
[Your solution that incorporates insights from multiple perspectives]

"""
        
        prompt += "Response:"
        
        return prompt
    
    @staticmethod
    def metacognitive_reasoning_prompt(
        problem: str,
        include_strategy_selection: bool = True,
        include_self_monitoring: bool = True
    ) -> str:
        """Generate metacognitive reasoning prompt with explicit thinking about thinking"""
        
        prompt = f"""Solve the following problem using metacognitive reasoning - explicitly think about your thinking process.

Problem: {problem}

"""
        
        if include_strategy_selection:
            prompt += """**Strategy Selection:**
- What type of problem is this?
- What reasoning strategies could be effective? (logical deduction, pattern recognition, analogy, etc.)
- Which strategy seems most promising and why?
- What are potential pitfalls to avoid?

"""
        
        prompt += """**Problem Solving Process:**
Now work through the problem while monitoring your thinking:

Step 1: [Your approach]
- Metacognitive check: Is this approach working? Do I need to adjust?

Step 2: [Continue reasoning] 
- Metacognitive check: Am I on the right track? What evidence supports this?

[Continue with metacognitive monitoring throughout]

"""
        
        if include_self_monitoring:
            prompt += """**Self-Monitoring Reflection:**
- How confident am I in this solution?
- What assumptions did I make?
- How could I verify this answer?
- What would I do differently next time?

"""
        
        prompt += """**Final Answer:**
[Your solution]

**Meta-Analysis:**
[Reflection on your reasoning process and what you learned about your own thinking]

Response:"""
        
        return prompt
    
    @staticmethod
    def problem_solving_prompt(problem: str, problem_type: Optional[str] = None) -> str:
        """生成问题求解提示词"""
        prompt = f"Please solve the following"
        if problem_type:
            prompt += f" {problem_type}"
        prompt += f" problem:\n\n{problem}\n\nSolution:"
        return prompt
    
    @staticmethod
    def planning_prompt(goal: str, plan_type: Optional[str] = None) -> str:
        """生成计划制定提示词"""
        prompt = f"Please create a"
        if plan_type:
            prompt += f" {plan_type}"
        prompt += f" plan for the following goal:\n\n{goal}\n\nPlan:"
        return prompt
    
    # ==================== 工具调用类提示词 ====================
    
    @staticmethod
    def tool_call_prompt(query: str, available_tools: List[Dict[str, Any]]) -> str:
        """生成工具调用提示词"""
        tools_desc = json.dumps(available_tools, indent=2)
        prompt = f"You have access to the following tools:\n\n{tools_desc}\n\n"
        prompt += f"User query: {query}\n\n"
        prompt += "Please use the appropriate tools to answer the query. Respond with tool calls in JSON format."
        return prompt
    
    @staticmethod
    def function_call_prompt(description: str, function_name: str, parameters: Dict[str, Any]) -> str:
        """生成函数调用提示词"""
        params_desc = json.dumps(parameters, indent=2)
        prompt = f"Please call the function '{function_name}' with the following parameters to {description}:\n\n"
        prompt += f"Parameters:\n{params_desc}\n\n"
        prompt += "Function call result:"
        return prompt

class LLMPromptTemplates:
    """预定义的提示词模板"""
    
    # 系统消息模板
    SYSTEM_MESSAGES = {
        "assistant": "You are a helpful AI assistant. Please provide accurate and helpful responses.",
        "code_expert": "You are an expert programmer. Please provide clean, efficient, and well-documented code.",
        "analyst": "You are a data analyst. Please provide detailed and insightful analysis.",
        "writer": "You are a professional writer. Please provide clear, engaging, and well-structured content.",
        "teacher": "You are a patient and knowledgeable teacher. Please explain concepts clearly and provide examples.",
        "translator": "You are a professional translator. Please provide accurate and natural translations."
    }
    
    # 输出格式模板
    OUTPUT_FORMATS = {
        "json": "Please format your response as valid JSON.",
        "markdown": "Please format your response using Markdown syntax.",
        "bullet_points": "Please format your response as bullet points.",
        "numbered_list": "Please format your response as a numbered list.",
        "table": "Please format your response as a table.",
        "code": "Please format your response as code with appropriate syntax highlighting."
    }
    
    # 任务特定模板
    TASK_TEMPLATES = {
        "email": "Please write a professional email with the following content:",
        "report": "Please write a detailed report on the following topic:",
        "proposal": "Please write a project proposal for the following idea:",
        "documentation": "Please write clear documentation for the following:",
        "test_cases": "Please write comprehensive test cases for the following:",
        "user_story": "Please write user stories for the following feature:"
    }

def get_prompt_template(task_type: str, **kwargs) -> str:
    """获取指定任务类型的提示词模板"""
    prompts = LLMPrompts()
    
    if hasattr(prompts, f"{task_type}_prompt"):
        method = getattr(prompts, f"{task_type}_prompt")
        return method(**kwargs)
    else:
        raise ValueError(f"Unsupported task type: {task_type}")

def format_messages(messages: List[Dict[str, str]], system_message: Optional[str] = None) -> List[Dict[str, str]]:
    """格式化消息列表，添加系统消息"""
    formatted = []
    if system_message:
        formatted.append({"role": "system", "content": system_message})
    formatted.extend(messages)
    return formatted

def combine_prompts(prompts: List[str], separator: str = "\n\n") -> str:
    """组合多个提示词"""
    return separator.join(prompts)