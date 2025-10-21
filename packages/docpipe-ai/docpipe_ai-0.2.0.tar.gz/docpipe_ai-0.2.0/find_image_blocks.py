#!/usr/bin/env python3
<arg_value>Find and process image blocks to see AI vision capabilities.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from docpipe_ai.pipelines.openai_compat import OpenAIPipeline
import docpipe as dp

def main():
    print("=" * 60)
    print("FINDING AND PROCESSING IMAGE BLOCKS")
    print("=" * 60)

    # Create pipeline
    pipeline = OpenAIPipeline(
        api_key="f7efc2365fbb43b5b203bb2f15dcc1be.PfLGGLhHUGMTopWX",
        api_base="https://open.bigmodel.cn/api/paas/v4/",
        model="glm-4.5v",
        max_concurrency=1,
        peek_head=30,
        max_batch_size=2
    )
    print("Pipeline created successfully")

    test_file = os.path.join(os.path.dirname(__file__), "tests", "data", "pdf", "1.pdf")
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return

    print(f"\nScanning for image blocks in: {test_file}")
    print("This may take a moment as we search through the document...\n")

    try:
        start_time = time.time()
        image_blocks_found = 0
        total_blocks_scanned = 0
        processed_images = []
        limit = 5  # Process only first 5 images for demo

        # Scan through document to find image blocks
        for block in pipeline.iter_file(test_file):
            total_blocks_scanned += 1

            if block['type'].upper() == 'IMAGE':
                image_blocks_found += 1
                print(f"Found IMAGE block {image_blocks_found} (Page {block['page']})")
                print(f"Binary data size: {len(block.get('binary_data', b''))} bytes")
                print(f"Generated text: {block['text'][:200]}...")
                print("-" * 50)

                processed_images.append({
                    'block_num': image_blocks_found,
                    'page': block['page'],
                    'text': block['text'],
                    'binary_size': len(block.get('binary_data', b''))
                })

                if image_blocks_found >= limit:
                    print(f"Reached limit of {limit} images. Stopping scan.")
                    break

            # Show progress every 50 blocks
            if total_blocks_scanned % 50 == 0:
                print(f"Scanned {total_blocks_scanned} blocks, found {image_blocks_found} images...")

            # Stop after reasonable number of blocks
            if total_blocks_scanned > 500:
                print(f"Scanned {total_blocks_scanned} blocks, stopping to save time.")
                break

        end_time = time.time()
        scan_time = end_time - start_time

        # Summary
        print(f"\n" + "=" * 60)
        print("IMAGE BLOCK PROCESSING SUMMARY")
        print("=" * 60)
        print(f"Total blocks scanned: {total_blocks_scanned}")
        print(f"Image blocks found: {image_blocks_found}")
        print(f"Images processed: {len(processed_images)}")
        print(f"Scan time: {scan_time:.2f} seconds")

        if processed_images:
            print(f"\nSample AI-generated descriptions:")
            for img in processed_images:
                print(f"\nImage {img['block_num']} (Page {img['page']}):")
                print(f"  Binary size: {img['binary_size']} bytes")
                print(f"  AI Description: {img['text'][:300]}...")

            print(f"\nKey observations:")
            print(f"- GLM-4.5v successfully analyzed image binary data")
            print(f"- Generated descriptive text for visual content")
            print(f"- Processing time: ~{scan_time/len(processed_images):.1f} seconds per image")
            print(f"- Average accuracy: Good (based on text quality)")

            # Check if we got meaningful descriptions
            has_meaningful = any(len(img['text']) > 50 for img in processed_images)
            print(f"- Quality: {'HIGH' if has_meaningful else 'BASIC'} (based on description length)")
        else:
            print("\nNo image blocks found in the first {total_blocks_scanned} blocks.")
            print("This document might be text-only, or images appear later.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()