"""
Structured output mixins for docpipe-ai.

This module provides Mixin implementations for structured AI output,
enabling type-safe and validated responses from AI providers.
"""

from typing import Protocol, Dict, Any, Optional, Union
import json
import time
import base64
import logging
from abc import abstractmethod

from ..core.protocols import AIProcessable
from ..data.content import ImageContent, ProcessedContent, ProcessingMetrics, ProcessingStatus, ContentFormat
from ..data.schemas import StructuredImageResult, ProcessingMetadata, ContentDetails, ContentType
from ..data.config import ResponseFormatType, ContentAnalysisType

logger = logging.getLogger(__name__)


class StructuredOutputMixin:
    """
    结构化输出Mixin - 提供结构化AI输出功能

    这个Mixin实现了与AI providers的结构化输出集成，包括JSON schema
    定义、响应解析和验证。
    """

    def __init__(self: "AIProcessable", ai_client, model_name: str = "gpt-4o"):
        """
        初始化结构化输出处理

        Args:
            ai_client: AI客户端实例
            model_name: 模型名称
        """
        self.ai_client = ai_client
        self.model_name = model_name
        self._request_count = 0

    def prepare_structured_request(self: "AIProcessable", content: ImageContent) -> Dict[str, Any]:
        """
        准备结构化输出的AI请求数据

        Args:
            content: 图片内容

        Returns:
            AI API请求数据（包含response_format）
        """
        try:
            # 获取配置
            config = getattr(self, 'config', None)
            if not config:
                raise ValueError("Configuration not found")

            # 准备系统提示词
            system_prompt = self._get_structured_system_prompt(config.content_analysis_type)

            # 准备用户提示词
            user_prompt = self._create_structured_user_prompt(content, config.content_analysis_type)

            # 构建消息列表
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": []}
            ]

            # 添加图片数据
            if content.binary_data:
                image_message = self._create_image_message(content)
                if image_message:
                    messages[1]["content"].append({"type": "text", "text": user_prompt})
                    messages[1]["content"].append(image_message)
                else:
                    messages[1]["content"] = user_prompt
            else:
                messages[1]["content"] = user_prompt

            # 构建基础请求参数
            request_data = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
            }

            # 添加结构化输出格式
            if config.response_format == ResponseFormatType.STRUCTURED:
                # 检查是否为GLM模型（智谱AI）
                if "glm" in self.model_name.lower():
                    # GLM模型：在系统提示词中指定JSON格式要求
                    system_prompt = request_data["messages"][0]["content"]
                    json_schema = config.custom_schema or self._get_default_schema()
                    json_instruction = f"\n\n请严格按照以下JSON格式返回结果：\n{json.dumps(json_schema, ensure_ascii=False, indent=2)}\n返回的必须是有效的JSON格式，不要包含其他文本。"
                    request_data["messages"][0]["content"] = system_prompt + json_instruction
                elif hasattr(self.ai_client, 'chat') and hasattr(self.ai_client.chat, 'completions'):
                    # OpenAI格式
                    request_data["response_format"] = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "image_analysis",
                            "schema": config.custom_schema or self._get_default_schema()
                        }
                    }
                else:
                    # 其他provider的格式
                    request_data["response_format"] = {"type": "json_object"}

            self._request_count += 1
            return request_data

        except Exception as e:
            logger.error(f"Error preparing structured request: {e}")
            raise

    def process_structured_response(self: "AIProcessable", response_text: str,
                                   original_content: ImageContent,
                                   processing_time: float) -> ProcessedContent:
        """
        处理结构化响应并转换为ProcessedContent

        Args:
            response_text: AI响应的JSON文本
            original_content: 原始图片内容
            processing_time: 处理时间

        Returns:
            ProcessedContent对象
        """
        try:
            # 清理响应文本，移除可能的格式化字符
            cleaned_text = response_text.strip()

            # 尝试找到JSON的开始和结束
            json_start = cleaned_text.find('{')
            json_end = cleaned_text.rfind('}')

            if json_start != -1 and json_end != -1 and json_end > json_start:
                # 提取JSON部分
                json_text = cleaned_text[json_start:json_end + 1]
                logger.debug(f"Extracted JSON text length: {len(json_text)}")
            else:
                # 如果找不到JSON格式，使用原始文本
                json_text = cleaned_text

            # 解析JSON响应
            response_data = json.loads(json_text)

            # 转换为StructuredImageResult
            structured_result = self._parse_structured_response(response_data, original_content)

            # 转换为ProcessedContent
            processed_content = self._convert_to_processed_content(structured_result, original_content, processing_time)

            return processed_content

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return ProcessedContent.create_error_result(
                original=original_content,
                error_message=f"Invalid JSON response: {str(e)}",
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Error processing structured response: {e}")
            return ProcessedContent.create_error_result(
                original=original_content,
                error_message=f"Response processing failed: {str(e)}",
                processing_time=processing_time
            )

    def _get_structured_system_prompt(self: "AIProcessable", analysis_type: ContentAnalysisType) -> str:
        """获取结构化输出的系统提示词"""
        base_prompt = """你是一个专业的文档分析助手。请分析提供的图片并返回结构化的JSON响应。

要求：
1. 仔细观察图片中的所有内容
2. 准确识别文本、表格、图表等信息
3. 按照指定的JSON格式返回结果
4. 确保JSON格式正确，可以被解析
5. 提供准确的信息提取和总结"""

        if analysis_type == ContentAnalysisType.CONTRACT:
            return base_prompt + """

重点关注：
- 合同标题和编号
- 签约双方信息
- 关键条款和条件
- 金额和日期信息
- 页码和章节结构
"""
        elif analysis_type == ContentAnalysisType.TABLE:
            return base_prompt + """

重点关注：
- 表格的行列结构
- 表头和数据内容
- 数值和文本信息
- 表格的层次关系
"""
        else:
            return base_prompt

    def _create_structured_user_prompt(self: "AIProcessable", content: ImageContent,
                                      analysis_type: ContentAnalysisType) -> str:
        """创建结构化输出的用户提示词"""
        if analysis_type == ContentAnalysisType.CONTRACT:
            return """请分析这个合同文档页面，提取以下信息：
- 文档类型和标题
- 签约双方（委托方、受托方等）
- 关键条款内容
- 金额、日期等数字信息
- 页码信息

请返回详细的JSON格式分析结果。"""
        elif analysis_type == ContentAnalysisType.TABLE:
            return """请分析这个表格，提取以下信息：
- 表格的主要内容和结构
- 表头信息
- 数据行内容
- 重要的数值信息

请返回详细的JSON格式分析结果。"""
        else:
            return """请分析这个图片，提取并总结其中的主要内容。
请返回详细的JSON格式分析结果，包括内容类型、主要信息和关键点。"""

    def _get_default_schema(self: "AIProcessable") -> Dict[str, Any]:
        """获取默认的JSON schema"""
        return {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Brief summary of what's in the image"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["table", "text", "non_text", "mixed"],
                    "description": "Primary type of content in the image"
                },
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key points or information extracted from the image"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Confidence score of the analysis"
                }
            },
            "required": ["summary", "content_type", "key_points", "confidence"]
        }

    def _parse_structured_response(self: "AIProcessable", response_data: Dict[str, Any],
                                   original_content: ImageContent) -> StructuredImageResult:
        """解析结构化响应数据"""
        try:
            # 提取基本信息
            summary = response_data.get("summary", "")

            # 确定内容类型
            content_type_str = response_data.get("content_type", "text")
            content_type = ContentType(content_type_str) if content_type_str in ContentType.__members__ else ContentType.TEXT

            # 提取关键点
            key_points = response_data.get("key_points", [])
            if isinstance(key_points, str):
                key_points = [key_points]

            # 计算置信度
            confidence = response_data.get("confidence", 0.8)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                confidence = 0.8

            # 创建内容详情
            content_details = ContentDetails(
                content_summary=summary,
                key_elements=key_points,
                text_content=summary if content_type == ContentType.TEXT else None,
                non_text_content=response_data.get("non_text_description"),
                document_structure=response_data.get("structure")
            )

            # 创建处理元数据
            processing_metadata = ProcessingMetadata(
                confidence_score=confidence,
                model_used=self.model_name,
                language_detected="zh" if any('\u4e00' <= c <= '\u9fff' for c in summary) else "en",
                content_quality=self._assess_content_quality(response_data)
            )

            # 生成图片ID
            import hashlib
            image_hash = hashlib.md5(original_content.binary_data).hexdigest()[:8]

            return StructuredImageResult(
                image_id=f"img_{image_hash}_{int(time.time())}",
                original_image_hash=image_hash,
                summary_text=summary,
                content_type=content_type,
                content_details=content_details,
                processing_metadata=processing_metadata,
                tags=response_data.get("tags", []),
                categories=response_data.get("categories", [])
            )

        except Exception as e:
            logger.error(f"Error parsing structured response: {e}")
            # 创建默认的结构化结果
            return self._create_default_structured_result(original_content, str(e))

    def _convert_to_processed_content(self: "AIProcessable", structured_result: StructuredImageResult,
                                     original_content: ImageContent,
                                     processing_time: float) -> ProcessedContent:
        """将StructuredImageResult转换为ProcessedContent"""
        # 构建处理后的文本
        processed_text = structured_result.summary_text

        if structured_result.content_details.key_elements:
            elements_text = "\n关键信息：\n" + "\n".join(f"- {element}" for element in structured_result.content_details.key_elements)
            processed_text += elements_text

        # 创建处理指标
        metrics = ProcessingMetrics(
            processing_time=processing_time,
            confidence=structured_result.processing_metadata.confidence_score,  # 使用confidence而不是confidence_score
            token_usage=None  # 需要从API响应中获取
        )

        return ProcessedContent(
            original=original_content,
            processed_text=processed_text,
            status=ProcessingStatus.COMPLETED,
            processing_id=structured_result.image_id,
            metrics=metrics,
            structured_data=structured_result.model_dump()  # 使用model_dump而不是dict
        )

    def _assess_content_quality(self: "AIProcessable", response_data: Dict[str, Any]) -> str:
        """评估内容质量"""
        summary = response_data.get("summary", "")
        key_points = response_data.get("key_points", [])

        if len(summary) > 100 and len(key_points) >= 3:
            return "high"
        elif len(summary) > 50 and len(key_points) >= 1:
            return "medium"
        else:
            return "low"

    def _create_default_structured_result(self: "AIProcessable", original_content: ImageContent,
                                         error_message: str) -> StructuredImageResult:
        """创建默认的结构化结果（当解析失败时）"""
        import hashlib
        image_hash = hashlib.md5(original_content.binary_data).hexdigest()[:8]

        return StructuredImageResult(
            image_id=f"img_{image_hash}_{int(time.time())}",
            original_image_hash=image_hash,
            summary_text=f"图片处理完成，但解析时遇到问题：{error_message}",
            content_type=ContentType.TEXT,
            content_details=ContentDetails(
                content_summary="处理结果可能不完整",
                key_elements=["解析过程中遇到错误"]
            ),
            processing_metadata=ProcessingMetadata(
                confidence_score=0.3,
                model_used=self.model_name,
                content_quality="low"
            )
        )

    def _create_image_message(self: "AIProcessable", content: ImageContent) -> Optional[Dict[str, Any]]:
        """创建图片消息格式"""
        try:
            if not content.binary_data:
                return None

            # 编码图片数据
            if isinstance(content.binary_data, bytes):
                base64_image = base64.b64encode(content.binary_data).decode('utf-8')
            else:
                base64_image = content.binary_data

            # 确定MIME类型
            mime_type = self._get_mime_type(content)

            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}",
                    "detail": "low"  # 使用低分辨率以节省token
                }
            }

        except Exception as e:
            logger.error(f"Error creating image message: {e}")
            return None

    def _get_mime_type(self: "AIProcessable", content: ImageContent) -> str:
        """获取图片的MIME类型"""
        if hasattr(content, 'metadata') and hasattr(content.metadata, 'format'):
            format_mapping = {
                ContentFormat.JPEG: "image/jpeg",
                ContentFormat.PNG: "image/png",
                ContentFormat.GIF: "image/gif",
                ContentFormat.BMP: "image/bmp",
                ContentFormat.WEBP: "image/webp",
                ContentFormat.TIFF: "image/tiff"
            }
            return format_mapping.get(content.metadata.format, "image/jpeg")
        return "image/jpeg"

    def _call_ai_service(self: "AIProcessable", request_data: Dict[str, Any]) -> str:
        """调用AI服务"""
        try:
            logger.debug(f"Calling AI service with structured output, model: {self.model_name}")
            response = self.ai_client.chat.completions.create(**request_data)

            if response.choices and response.choices[0].message:
                generated_text = response.choices[0].message.content or ""
                self._request_count += 1
                return generated_text
            else:
                raise ValueError("Empty response from AI service")

        except Exception as e:
            logger.error(f"AI service call failed: {e}")
            raise