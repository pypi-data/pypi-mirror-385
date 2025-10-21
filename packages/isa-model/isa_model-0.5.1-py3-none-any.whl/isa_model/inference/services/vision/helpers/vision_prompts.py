"""
统一的Vision任务提示词服务
为不同的Vision模型提供标准化的提示词模板，避免重复代码
"""

from typing import List, Optional, Dict, Any


class VisionPromptService:
    """Vision任务的统一提示词生成服务"""
    
    @staticmethod
    def get_describe_prompt(detail_level: str = "medium") -> str:
        """生成图像描述提示词"""
        detail_prompts = {
            "brief": "Please provide a brief, one-sentence description of this image.",
            "medium": "Please provide a detailed description of this image, including main objects, people, setting, and notable details.",
            "detailed": "Please provide a comprehensive and detailed description of this image, including all visible objects, people, setting, colors, composition, style, mood, and any other notable details or context."
        }
        return detail_prompts.get(detail_level, detail_prompts["medium"])
    
    @staticmethod
    def get_extract_text_prompt() -> str:
        """生成文本提取(OCR)提示词"""
        return """Please extract ALL text content from this image. Requirements:
        1. Extract text exactly as it appears
        2. Preserve formatting, line breaks, and structure
        3. If there are tables, maintain table structure
        4. Include headers, captions, and footnotes
        5. Return as structured JSON with extracted text and layout information
        
        Format your response as JSON:
        {
            "extracted_text": "full text content",
            "structured_content": {
                "headers": [],
                "paragraphs": [],
                "tables": [],
                "other": []
            }
        }"""
    
    @staticmethod
    def get_detect_objects_prompt(confidence_threshold: float = 0.5) -> str:
        """生成物体检测提示词"""
        return f"""Please identify and locate all objects in this image. For each object:
        1. Object name/type
        2. Approximate location (describe position: top-left, center, bottom-right, etc.)
        3. Size (small, medium, large)
        4. Confidence level (high, medium, low)
        
        Only include objects you're confident about (confidence > {confidence_threshold})
        
        Format as JSON:
        {{
            "detected_objects": [
                {{
                    "name": "object_name",
                    "location": "position_description", 
                    "size": "relative_size",
                    "confidence": "confidence_level"
                }}
            ]
        }}"""
    
    @staticmethod
    def get_detect_ui_elements_prompt(element_types: Optional[List[str]] = None) -> str:
        """生成UI元素检测提示词"""
        element_filter = f"Focus on these element types: {', '.join(element_types)}" if element_types else "Identify all UI elements"
        
        return f"""Please analyze this user interface image and identify all interactive elements. {element_filter}
        
        For each UI element, provide:
        1. Element type (button, input field, dropdown, link, checkbox, radio button, text area, etc.)
        2. Text/label content
        3. Location description
        4. Interactive state (enabled, disabled, selected, etc.)
        
        Format as JSON:
        {{
            "ui_elements": [
                {{
                    "type": "element_type",
                    "text": "visible_text",
                    "location": "position_description",
                    "state": "element_state",
                    "confidence": "detection_confidence"
                }}
            ]
        }}"""
    
    @staticmethod
    def get_detect_document_elements_prompt() -> str:
        """生成文档元素检测提示词"""
        return """Please analyze this document image and extract its structure and content.
        
        Identify and extract:
        1. Headers and subheaders (with hierarchy level)
        2. Paragraphs and body text
        3. Tables (with rows and columns)
        4. Lists (ordered/unordered)
        5. Images and captions
        6. Footnotes and references
        
        Format as JSON:
        {
            "document_structure": {
                "title": "document_title",
                "headers": [
                    {"level": 1, "text": "header_text", "position": "location"}
                ],
                "paragraphs": [
                    {"text": "paragraph_content", "position": "location"}
                ],
                "tables": [
                    {"rows": [["cell1", "cell2"]], "caption": "table_caption"}
                ],
                "lists": [
                    {"type": "ordered/unordered", "items": ["item1", "item2"]}
                ]
            }
        }"""
    
    @staticmethod
    def get_extract_table_data_prompt(table_format: str = "json", preserve_formatting: bool = True) -> str:
        """生成表格数据抽取提示词"""
        format_instructions = {
            "json": "Return the table data as a JSON structure with arrays for headers and rows",
            "csv": "Return the table data in CSV format",
            "markdown": "Return the table data in Markdown table format", 
            "html": "Return the table data as an HTML table"
        }
        
        format_instruction = format_instructions.get(table_format, format_instructions["json"])
        formatting_note = "Preserve cell merging, formatting, and styling information" if preserve_formatting else "Extract data in simplified format"
        
        return f"""Please extract ALL table data from this image with high precision. {formatting_note}
        
        Requirements:
        1. Identify all tables in the image
        2. Extract headers, rows, and data accurately
        3. Maintain data relationships and structure
        4. Handle merged cells appropriately
        5. Include any table captions or titles
        6. {format_instruction}
        
        For each table, provide:
        - Table identifier/caption
        - Column headers
        - All row data
        - Metadata about structure (row/column counts, merged cells)
        
        Return as structured JSON:
        {{
            "tables": [
                {{
                    "table_id": "table_1",
                    "caption": "table_title_if_any",
                    "headers": ["Column1", "Column2", "Column3"],
                    "rows": [
                        ["data1", "data2", "data3"],
                        ["data4", "data5", "data6"]
                    ],
                    "metadata": {{
                        "row_count": 2,
                        "column_count": 3,
                        "has_headers": true,
                        "merged_cells": [
                            {{"row": 0, "col": 0, "rowspan": 1, "colspan": 2}}
                        ],
                        "data_types": ["text", "number", "text"]
                    }}
                }}
            ],
            "extraction_metadata": {{
                "total_tables": 1,
                "extraction_confidence": "high",
                "format": "{table_format}",
                "preserve_formatting": {str(preserve_formatting).lower()}
            }}
        }}
        
        Important: 
        - Be extremely accurate with data extraction
        - Preserve numbers exactly as they appear
        - Handle currency, percentages, and special characters correctly
        - If cells are empty, represent them as empty strings or null
        - For merged cells, include merge information in metadata"""
    
    @staticmethod
    def get_classify_image_prompt(categories: Optional[List[str]] = None) -> str:
        """生成图像分类提示词"""
        if categories:
            return f"""Please classify this image into one of these categories: {', '.join(categories)}
            
            Provide:
            1. The most appropriate category
            2. Confidence level (0.0-1.0) 
            3. Brief reasoning
            
            Format as JSON:
            {{
                "classification": "selected_category",
                "confidence": 0.95,
                "reasoning": "explanation"
            }}"""
        else:
            return """Please classify this image by identifying its main category and subcategory.
            
            Provide:
            1. Main category (e.g., nature, technology, people, etc.)
            2. Subcategory (more specific classification)
            3. Confidence level
            4. Key features that led to this classification
            
            Format as JSON:
            {
                "main_category": "primary_category",
                "subcategory": "specific_type", 
                "confidence": 0.95,
                "key_features": ["feature1", "feature2"]
            }"""
    
    @staticmethod
    def get_object_coordinates_prompt(object_name: str) -> str:
        """生成对象坐标检测提示词"""
        return f"""Please locate '{object_name}' in this image and provide detailed location information.
        
        Provide:
        1. Whether the object was found
        2. Detailed position description
        3. Approximate coordinates (if possible, describe as percentages from top-left)
        4. Size and boundaries
        
        Format as JSON:
        {{
            "found": true/false,
            "object_name": "{object_name}",
            "location": "detailed_position_description",
            "coordinates": "approximate_position_as_percentages",
            "size": "object_size_description",
            "confidence": "detection_confidence"
        }}"""
    
    @staticmethod
    def get_compare_images_prompt() -> str:
        """生成图像比较提示词"""
        return """Please compare the objects, styles, and content in this image. Highlight similarities and differences.
        
        Provide:
        1. Main similarities
        2. Key differences
        3. Style comparison
        4. Content analysis
        
        Format as JSON:
        {
            "comparison": {
                "similarities": ["similarity1", "similarity2"],
                "differences": ["difference1", "difference2"],
                "style_analysis": "style_comparison",
                "content_analysis": "content_comparison"
            }
        }"""


class VisionPromptMixin:
    """
    Mixin类，为Vision服务提供统一的提示词支持
    任何Vision服务都可以继承这个Mixin来获得标准提示词
    """
    
    def get_task_prompt(self, task: str, **kwargs) -> str:
        """根据任务类型获取对应的提示词"""
        if task == "describe":
            return VisionPromptService.get_describe_prompt(kwargs.get("detail_level", "medium"))
        elif task == "extract_text":
            return VisionPromptService.get_extract_text_prompt()
        elif task == "detect_objects":
            return VisionPromptService.get_detect_objects_prompt(kwargs.get("confidence_threshold", 0.5))
        elif task == "detect_ui_elements":
            return VisionPromptService.get_detect_ui_elements_prompt(kwargs.get("element_types"))
        elif task == "detect_document_elements":
            return VisionPromptService.get_detect_document_elements_prompt()
        elif task == "extract_table_data":
            return VisionPromptService.get_extract_table_data_prompt(
                kwargs.get("table_format", "json"), 
                kwargs.get("preserve_formatting", True)
            )
        elif task == "classify":
            return VisionPromptService.get_classify_image_prompt(kwargs.get("categories"))
        elif task == "get_coordinates":
            return VisionPromptService.get_object_coordinates_prompt(kwargs.get("object_name", ""))
        elif task == "compare":
            return VisionPromptService.get_compare_images_prompt()
        else:
            return "Please analyze this image and provide detailed information."