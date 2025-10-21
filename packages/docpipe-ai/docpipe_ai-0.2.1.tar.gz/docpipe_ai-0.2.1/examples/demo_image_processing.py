"""
图片处理演示脚本
展示如何使用 docpipe-ai 处理文档中的图片
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from docpipe_ai.llms import create_openai_vlm, create_ollama_vlm, get_predefined_vlm
from docpipe_ai.agents import (
    create_descriptive_agent, create_table_agent, create_chart_agent,
    AgentFactory
)
from docpipe_ai.image_processor import (
    ImageProcessor, ImageProcessingConfig, create_image_processor,
    process_document_images
)
from docpipe_ai.batch_processor import (
    AdvancedBatchProcessor, ProcessingOptions,
    process_document_with_advanced_batching, create_progress_callback
)

import docpipe as dp

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_image_processing():
    """基础图片处理演示"""
    print("=" * 60)
    print("基础图片处理演示")
    print("=" * 60)

    # 获取第一个图片块
    try:
        chunks = list(dp.serialize("tests/data/pdf/1.pdf"))
        image_chunk = None
        for chunk in chunks:
            if chunk.type == 'image':
                image_chunk = chunk
                break

        if not image_chunk:
            print("未找到图片块")
            return

        print(f"找到图片块：页面 {image_chunk.page}, 大小 {len(image_chunk.binary_data)} bytes")

        # 创建不同类型的处理器
        processors = [
            ("描述性处理器", create_image_processor(agent_type="descriptive")),
            ("表格处理器", create_image_processor(agent_type="table", output_format="markdown")),
            ("结构化处理器", create_image_processor(agent_type="structured", output_format="json")),
        ]

        for name, processor in processors:
            print(f"\n--- {name} ---")
            try:
                result = processor.invoke(image_chunk.to_dict())
                print(f"处理结果（前200字符）：{result['text'][:200]}...")
            except Exception as e:
                print(f"处理失败：{e}")

    except Exception as e:
        print(f"演示失败：{e}")


def demo_custom_vlm_and_agent():
    """自定义 VLM 和 Agent 演示"""
    print("\n" + "=" * 60)
    print("自定义 VLM 和 Agent 演示")
    print("=" * 60)

    try:
        # 创建自定义 VLM
        vlm = create_openai_vlm(
            model_name="gpt-4o",
            temperature=0.2,
            detail_level="low"
        )

        # 创建自定义 Agent
        agent = create_descriptive_agent(vlm, language="zh")

        # 创建自定义配置的处理器
        config = ImageProcessingConfig(
            custom_vlm=vlm,
            custom_agent=agent,
            max_concurrency=2
        )
        processor = ImageProcessor(config)

        print(f"使用自定义 VLM: {vlm.model_name}")
        print(f"使用自定义 Agent: {type(agent).__name__}")

        # 处理一个图片块
        chunks = list(dp.serialize("tests/data/pdf/1.pdf"))
        for chunk in chunks[:50]:  # 只检查前50个块
            if chunk.type == 'image':
                result = processor.invoke(chunk.to_dict())
                print(f"\n处理结果：{result['text'][:150]}...")
                break

    except Exception as e:
        print(f"演示失败：{e}")


def demo_batch_processing():
    """批次处理演示"""
    print("\n" + "=" * 60)
    print("批次处理演示")
    print("=" * 60)

    try:
        # 创建配置
        config = ImageProcessingConfig(
            vlm_provider="openai",
            vlm_model="gpt-4o",
            agent_type="descriptive",
            max_concurrency=2,
            batch_size=5
        )

        # 创建批次处理器
        from docpipe_ai.image_processor import BatchImageProcessor
        batch_processor = BatchImageProcessor(config)

        print("开始批次处理...")

        # 统计信息
        total_chunks = 0
        image_chunks = 0
        processed_images = 0

        # 处理前100个块作为演示
        chunks = list(dp.serialize("tests/data/pdf/1.pdf"))[:100]

        for chunk in batch_processor.process_images(iter(chunks)):
            total_chunks += 1
            if chunk.get("type") == "image":
                image_chunks += 1
                if chunk.get("text") and chunk["text"].strip():
                    processed_images += 1

        print(f"批次处理完成：")
        print(f"  总块数：{total_chunks}")
        print(f"  图片块数：{image_chunks}")
        print(f"  成功处理的图片：{processed_images}")

    except Exception as e:
        print(f"演示失败：{e}")


def demo_advanced_batch_processing():
    """高级批次处理演示"""
    print("\n" + "=" * 60)
    print("高级批次处理演示")
    print("=" * 60)

    try:
        # 创建进度回调
        progress_callback = create_progress_callback(log_interval=5)

        # 创建处理选项
        options = ProcessingOptions(
            max_concurrency=2,
            batch_size=5,
            enable_progress=True,
            progress_callback=progress_callback,
            save_errors=False,  # 演示时不保存错误文件
            continue_on_error=True
        )

        # 创建图片处理器
        config = ImageProcessingConfig(
            vlm_provider="openai",
            vlm_model="gpt-4o",
            agent_type="descriptive"
        )
        image_processor = ImageProcessor(config)

        # 创建高级批次处理器
        advanced_processor = AdvancedBatchProcessor(image_processor, options)

        print("开始高级批次处理...")

        # 处理前50个块作为演示
        chunks = list(dp.serialize("tests/data/pdf/1.pdf"))[:50]
        processed_chunks = list(advanced_processor.process_chunks(iter(chunks)))

        # 获取摘要
        summary = advanced_processor.get_summary()
        print(f"\n处理摘要：")
        for key, value in summary.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"演示失败：{e}")


def demo_different_agents():
    """不同类型 Agent 演示"""
    print("\n" + "=" * 60)
    print("不同类型 Agent 演示")
    print("=" * 60)

    try:
        # 找到图片块
        chunks = list(dp.serialize("tests/data/pdf/1.pdf"))
        image_chunk = None
        for chunk in chunks:
            if chunk.type == 'image':
                image_chunk = chunk
                break

        if not image_chunk:
            print("未找到图片块")
            return

        # 测试不同类型的 Agent
        agent_configs = [
            ("描述性 Agent", {"agent_type": "descriptive"}),
            ("表格 Agent", {"agent_type": "table", "output_format": "markdown"}),
            ("图表 Agent", {"agent_type": "chart"}),
            ("结构化 Agent", {"agent_type": "structured", "output_format": "json"}),
        ]

        for name, config in agent_configs:
            print(f"\n--- {name} ---")
            try:
                processor = create_image_processor(**config)
                result = processor.invoke(image_chunk.to_dict())
                print(f"结果预览：{result['text'][:100]}...")
            except Exception as e:
                print(f"处理失败：{e}")

    except Exception as e:
        print(f"演示失败：{e}")


def main():
    """主函数"""
    print("docpipe-ai 图片处理演示")
    print("注意：这些演示需要配置有效的 OpenAI API 密钥")

    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("警告：未设置 OPENAI_API_KEY 环境变量")
        print("某些演示可能会失败")

    try:
        # 运行各种演示
        demo_basic_image_processing()
        demo_custom_vlm_and_agent()
        demo_batch_processing()
        demo_advanced_batch_processing()
        demo_different_agents()

        print("\n" + "=" * 60)
        print("所有演示完成！")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()