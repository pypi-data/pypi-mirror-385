#!/usr/bin/env python3
"""
调试docpipe返回的原始数据
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import docpipe as dp

def main():
    print("=" * 60)
    print("调试docpipe原始数据")
    print("=" * 60)

    test_file = os.path.join(os.path.dirname(__file__), "tests", "data", "pdf", "1.pdf")
    if not os.path.exists(test_file):
        print(f"[ERROR] 测试文件不存在: {test_file}")
        return

    print(f"[PASS] 测试文件: {test_file}")
    print("\n检查docpipe原始输出...\n")

    try:
        # 获取原始chunks
        chunks = dp.serialize(test_file)
        chunk_count = 0

        for chunk in chunks:
            chunk_count += 1
            print(f"Chunk {chunk_count}:")
            print(f"  Type: {getattr(chunk, 'type', 'Unknown')}")
            print(f"  Page: {getattr(chunk, 'page', 'Unknown')}")

            # 检查所有属性
            attrs = dir(chunk)
            print(f"  All attributes: {[attr for attr in attrs if not attr.startswith('_')]}")

            # 检查binary_data
            if hasattr(chunk, 'binary_data'):
                binary_data = chunk.binary_data
                print(f"  binary_data type: {type(binary_data)}")
                print(f"  binary_data size: {len(binary_data) if binary_data else 0}")

                if binary_data and isinstance(binary_data, bytes):
                    try:
                        # 尝试解码为文本
                        text_content = binary_data.decode('utf-8', errors='ignore')
                        print(f"  Decoded text length: {len(text_content)}")
                        print(f"  Text preview: {text_content[:100]}...")
                    except:
                        print(f"  binary_data cannot be decoded as text")
                elif binary_data and isinstance(binary_data, str):
                    print(f"  Text content length: {len(binary_data)}")
                    print(f"  Text preview: {binary_data[:100]}...")
                else:
                    print(f"  binary_data is empty or None")
            else:
                print(f"  No binary_data attribute")

            # 检查其他可能的文本属性
            for attr in ['text', 'content', 'content_str']:
                if hasattr(chunk, attr):
                    value = getattr(chunk, attr)
                    print(f"  {attr}: {str(value)[:100] if value else None}...")

            print("-" * 50)

            if chunk_count >= 5:  # 只检查前5个chunk
                print(f"检查了前5个chunk，停止")
                break

    except Exception as e:
        print(f"[ERROR] 处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()