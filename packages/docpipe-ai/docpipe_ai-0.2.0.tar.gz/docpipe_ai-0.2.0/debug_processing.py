#!/usr/bin/env python3
"""
调试处理流程 - 显示详细的AI处理日志
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from docpipe_ai.pipelines.openai_compat import OpenAIPipeline

def main():
    print("=" * 80)
    print("DOPIPE-AI 处理流程调试")
    print("=" * 80)

    # 创建pipeline
    pipeline = OpenAIPipeline(
        api_key="f7efc2365fbb43b5b203bb2f15dcc1be.PfLGGLhHUGMTopWX",
        api_base="https://open.bigmodel.cn/api/paas/v4/",
        model="glm-4.5v",
        max_concurrency=1,  # 限制并发便于观察
        peek_head=20,
        max_batch_size=3    # 小批次便于观察
    )
    print("[PASS] Pipeline创建成功")

    test_file = os.path.join(os.path.dirname(__file__), "tests", "data", "pdf", "1.pdf")
    if not os.path.exists(test_file):
        print(f"[ERROR] 测试文件不存在: {test_file}")
        return

    print(f"[PASS] 测试文件: {test_file}")
    print("\n开始处理，将显示详细的AI处理决策...")
    print("预期: TEXT块 -> PASS_THROUGH, IMAGE块 -> AI_PROCESS\n")

    try:
        start_time = time.time()
        processed_count = 0
        block_limit = 20  # 限制处理数量便于观察

        for block in pipeline.iter_file(test_file):
            processed_count += 1
            block_type = block['type'].upper()
            text_length = len(block.get('text', ''))
            binary_size = len(block.get('binary_data', b'')) if block.get('binary_data') else 0

            print(f"[RESULT] {block_type:6s} | Page:{block.get('page'):3d} | Text:{text_length:3d}ch | Binary:{binary_size:5d}B")

            if text_length > 0 and block_type == 'TEXT':
                # 安全地显示文本预览
                preview = block['text'][:50].replace('\n', ' ').replace('•', '*')
                print(f"         Text preview: {preview}...")
            elif text_length > 0 and block_type == 'IMAGE':
                # 显示AI生成的图片描述
                preview = block['text'][:80].replace('\n', ' ')
                print(f"         AI description: {preview}...")

            print("-" * 60)

            if processed_count >= block_limit:
                print(f"达到处理限制 {block_limit} 块")
                break

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"\n" + "=" * 80)
        print("处理总结")
        print("=" * 80)
        print(f"处理块数: {processed_count}")
        print(f"处理时间: {processing_time:.2f}秒")
        print(f"平均每块: {processing_time/processed_count:.2f}秒")

    except Exception as e:
        print(f"[ERROR] 处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()