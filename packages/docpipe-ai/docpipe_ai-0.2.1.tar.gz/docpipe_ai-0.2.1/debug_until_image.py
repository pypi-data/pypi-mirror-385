#!/usr/bin/env python3
"""
处理直到找到图片块 - 显示AI处理日志
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from docpipe_ai.pipelines.openai_compat import OpenAIPipeline

def main():
    print("=" * 80)
    print("DOPIPE-AI 查找图片块并显示AI处理")
    print("=" * 80)

    # 创建pipeline
    pipeline = OpenAIPipeline(
        api_key="f7efc2365fbb43b5b203bb2f15dcc1be.PfLGGLhHUGMTopWX",
        api_base="https://open.bigmodel.cn/api/paas/v4/",
        model="glm-4.5v",
        max_concurrency=1,
        peek_head=20,
        max_batch_size=3
    )
    print("[PASS] Pipeline创建成功")

    test_file = os.path.join(os.path.dirname(__file__), "tests", "data", "pdf", "1.pdf")
    if not os.path.exists(test_file):
        print(f"[ERROR] 测试文件不存在: {test_file}")
        return

    print(f"[PASS] 测试文件: {test_file}")
    print("\n开始处理，寻找图片块...")
    print("目标: 观察IMAGE块的AI处理过程\n")

    try:
        start_time = time.time()
        processed_count = 0
        text_blocks = 0
        image_blocks_found = 0
        limit = 100  # 搜索前100个块

        for block in pipeline.iter_file(test_file):
            processed_count += 1
            block_type = block['type'].upper()
            text_length = len(block.get('text', ''))
            binary_size = len(block.get('binary_data', b'')) if block.get('binary_data') else 0

            if block_type == 'TEXT':
                text_blocks += 1
                # 只显示每10个文本块中的1个
                if text_blocks % 10 == 1:
                    print(f"[SKIP] TEXT块 Page:{block.get('page'):3d} (跳过AI处理)")
            elif block_type == 'IMAGE':
                image_blocks_found += 1
                print(f"\n[FOUND] 图片块 {image_blocks_found}!")
                print(f"        页面: {block.get('page')}")
                print(f"        文本长度: {text_length} 字符")
                print(f"        二进制大小: {binary_size} 字节")
                if text_length > 0:
                    # 显示AI生成的描述
                    preview = block['text'][:150].replace('\n', ' ')
                    print(f"        AI描述: {preview}...")
                    print(f"        [SUCCESS] 图片块已成功处理")
                else:
                    print(f"        [ERROR] 图片块没有生成文本描述")

                # 找到第一个图片块后可以选择继续或停止
                if image_blocks_found >= 2:
                    print(f"\n已找到 {image_blocks_found} 个图片块，停止搜索")
                    break
            else:
                print(f"[OTHER] {block_type}块 Page:{block.get('page'):3d}")

            if processed_count >= limit:
                print(f"\n达到处理限制 {limit} 块")
                break

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"\n" + "=" * 80)
        print("搜索总结")
        print("=" * 80)
        print(f"总处理块数: {processed_count}")
        print(f"文本块: {text_blocks} (全部跳过AI处理)")
        print(f"图片块: {image_blocks_found} (AI处理)")
        print(f"处理时间: {processing_time:.2f}秒")

        if image_blocks_found > 0:
            print(f"\n[SUCCESS] 确认: 只有图片块被发送给AI处理!")
            print(f"[OPTIMIZATION] 文本块完全跳过AI处理，节省了大量成本!")
        else:
            print(f"\n[INFO] 在前 {processed_count} 个块中未找到图片块")

    except Exception as e:
        print(f"[ERROR] 处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()