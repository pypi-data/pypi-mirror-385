#!/usr/bin/env python3
"""
结构化输出功能演示

这个示例展示了如何使用docpipe-ai的结构化输出功能，
包括合同分析、表格提取和通用图片分析。
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from docpipe import PyMuPDFSerializer
from docpipe_ai.processors.adaptive_image_processor import AdaptiveImageProcessor
from docpipe_ai.data.config import ProcessingConfig, ContentAnalysisType, ResponseFormatType
from docpipe_ai.data.content import ImageContent, BoundingBox, ImageMetadata, ContentFormat
from docpipe_ai.data.schemas import StructuredImageResult
import base64
import json


def create_image_content_from_chunk(chunk, page_num):
    """从chunk创建ImageContent"""
    # 简化的格式检测
    if isinstance(chunk.binary_data, str):
        image_bytes = base64.b64decode(chunk.binary_data)
        format_type = ContentFormat.JPEG  # 默认
    else:
        image_bytes = chunk.binary_data
        format_type = ContentFormat.JPEG  # 默认

    return ImageContent(
        binary_data=image_bytes,
        page=page_num,
        bbox=BoundingBox.from_list(getattr(chunk, 'bbox', [0, 0, 100, 100])),
        metadata=ImageMetadata(
            format=format_type,
            size_bytes=len(image_bytes)
        )
    )


def demo_contract_analysis():
    """演示合同分析功能"""
    print("=" * 60)
    print("演示1: 合同文档分析")
    print("=" * 60)

    # 创建合同分析配置
    config = ProcessingConfig.create_contract_analysis_config()
    processor = AdaptiveImageProcessor.create_openai_processor(
        api_key="your-api-key-here",
        api_base="https://open.bigmodel.cn/api/paas/v4/",
        model="glm-4.5v",
        config=config
    )

    print(f"配置信息:")
    print(f"  模型: {config.model_name}")
    print(f"  响应格式: {config.response_format.value}")
    print(f"  分析类型: {config.content_analysis_type.value}")
    print(f"  温度: {config.temperature}")
    print(f"  最大token: {config.max_tokens}")

    # 示例：处理PDF文档
    serializer = PyMuPDFSerializer()
    file_path = "example_contract.pdf"

    print(f"\n处理文档: {file_path}")

    # 收集图片
    image_contents = []
    for chunk in serializer.iterate_chunks(file_path):
        if chunk.type == "image":
            image_content = create_image_content_from_chunk(chunk, len(image_contents) + 1)
            image_contents.append(image_content)
            if len(image_contents) >= 2:  # 限制处理数量
                break

    if not image_contents:
        print("未找到图片内容")
        return

    print(f"找到 {len(image_contents)} 张图片")

    # 处理图片
    try:
        results = processor.process_batch(image_contents)

        print(f"\n处理结果:")
        for i, result in enumerate(results):
            print(f"\n--- 图片 {i+1} ---")
            print(f"状态: {result.status.value}")
            print(f"处理时间: {result.metrics.processing_time:.2f}s" if result.metrics else "N/A")

            if result.status.value == 'completed' and result.structured_data:
                # 显示结构化数据
                data = result.structured_data
                print(f"内容类型: {data.get('content_type')}")
                print(f"摘要: {data.get('summary_text', '')[:100]}...")

                # 处理元数据
                metadata = data.get('processing_metadata', {})
                print(f"置信度: {metadata.get('confidence_score', 'N/A')}")
                print(f"内容质量: {metadata.get('content_quality', 'N/A')}")

            if result.error_message:
                print(f"错误: {result.error_message}")

    except Exception as e:
        print(f"处理失败: {e}")


def demo_table_extraction():
    """演示表格提取功能"""
    print("\n" + "=" * 60)
    print("演示2: 表格数据提取")
    print("=" * 60)

    # 创建表格提取配置
    config = ProcessingConfig.create_table_extraction_config()
    processor = AdaptiveImageProcessor.create_openai_processor(
        api_key="your-api-key-here",
        model="gpt-4o-mini",
        config=config
    )

    print(f"配置信息:")
    print(f"  模型: {config.model_name}")
    print(f"  响应格式: {config.response_format.value}")
    print(f"  分析类型: {config.content_analysis_type.value}")

    # 这里可以添加具体的表格处理逻辑
    print("表格提取配置已就绪，请提供包含表格的图片文档。")


def demo_general_analysis():
    """演示通用图片分析"""
    print("\n" + "=" * 60)
    print("演示3: 通用图片分析")
    print("=" * 60)

    # 创建通用分析配置
    config = ProcessingConfig.create_structured_output_config(
        analysis_type=ContentAnalysisType.GENERAL,
        model_name="gpt-4o-mini"
    )
    processor = AdaptiveImageProcessor.create_openai_processor(
        api_key="your-api-key-here",
        model="gpt-4o-mini",
        config=config
    )

    print(f"配置信息:")
    print(f"  模型: {config.model_name}")
    print(f"  响应格式: {config.response_format.value}")
    print(f"  分析类型: {config.content_analysis_type.value}")

    print("通用分析配置已就绪，可处理各种类型的图片文档。")


def demo_custom_schema():
    """演示自定义Schema"""
    print("\n" + "=" * 60)
    print("演示4: 自定义JSON Schema")
    print("=" * 60)

    # 定义自定义Schema
    custom_schema = {
        "type": "object",
        "properties": {
            "document_type": {
                "type": "string",
                "description": "文档类型"
            },
            "title": {
                "type": "string",
                "description": "文档标题"
            },
            "key_information": {
                "type": "array",
                "items": {"type": "string"},
                "description": "关键信息列表"
            },
            "importance_level": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "重要程度"
            }
        },
        "required": ["document_type", "title"]
    }

    # 创建自定义配置
    config = ProcessingConfig(
        response_format=ResponseFormatType.STRUCTURED,
        content_analysis_type=ContentAnalysisType.CUSTOM,
        custom_schema=custom_schema,
        model_name="gpt-4o",
        temperature=0.3
    )

    print(f"自定义Schema:")
    print(json.dumps(custom_schema, ensure_ascii=False, indent=2))
    print(f"\n配置信息:")
    print(f"  响应格式: {config.response_format.value}")
    print(f"  分析类型: {config.content_analysis_type.value}")

    print("自定义Schema配置已就绪，可根据需要调整JSON结构。")


def demo_configuration_options():
    """演示配置选项"""
    print("\n" + "=" * 60)
    print("演示5: 配置选项对比")
    print("=" * 60)

    configs = {
        "快速处理": ProcessingConfig.create_fast_config(),
        "高质量处理": ProcessingConfig.create_quality_config(),
        "合同分析": ProcessingConfig.create_contract_analysis_config(),
        "表格提取": ProcessingConfig.create_table_extraction_config()
    }

    for name, config in configs.items():
        print(f"\n{name}配置:")
        print(f"  模型: {config.model_name}")
        print(f"  并发数: {config.max_concurrency}")
        print(f"  温度: {config.temperature}")
        print(f"  最大token: {config.max_tokens}")
        print(f"  响应格式: {getattr(config, 'response_format', 'text')}")


def main():
    """主演示函数"""
    print("docpipe-ai 结构化输出功能演示")
    print("=" * 60)

    # 运行所有演示
    demo_configuration_options()
    demo_contract_analysis()
    demo_table_extraction()
    demo_general_analysis()
    demo_custom_schema()

    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)
    print("\n使用说明:")
    print("1. 替换API密钥和文档路径")
    print("2. 根据需要选择合适的配置")
    print("3. 处理结果包含结构化JSON数据")
    print("4. 可通过result.structured_data访问结构化结果")


if __name__ == "__main__":
    main()