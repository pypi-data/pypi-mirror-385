#!/usr/bin/env python3
"""
Simple pipeline demo to see AI processing effects.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from docpipe_ai.pipelines.openai_compat import OpenAIPipeline
import docpipe as dp

def main():
    print("=" * 50)
    print("DOPIPE-AI AI PROCESSING DEMO")
    print("=" * 50)

    # Create pipeline
    print("Creating pipeline with GLM-4.5v...")
    pipeline = OpenAIPipeline(
        api_key="f7efc2365fbb43b5b203bb2f15dcc1be.PfLGGLhHUGMTopWX",
        api_base="https://open.bigmodel.cn/api/paas/v4/",
        model="glm-4.5v",
        max_concurrency=1,  # Conservative for demo
        peek_head=20,
        max_batch_size=2   # Small batch for demo
    )
    print("Pipeline created successfully")

    # Test file
    test_file = os.path.join(os.path.dirname(__file__), "tests", "data", "pdf", "1.pdf")
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return

    print(f"\nProcessing: {test_file}")
    print("Limiting to first 5 blocks for demo...\n")

    try:
        start_time = time.time()
        processed_count = 0
        block_limit = 5

        for block in pipeline.iter_file(test_file):
            if processed_count >= block_limit:
                break

            print(f"Block {processed_count + 1}: {block['type'].upper()} (Page {block['page']})")
            print(f"Generated text: {block['text'][:200]}...")
            print("-" * 40)

            processed_count += 1

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"\nCompleted! Processed {processed_count} blocks in {processing_time:.2f} seconds")
        print(f"Average: {processing_time/processed_count:.2f} seconds per block")

        print("\nThe AI generated descriptive text for each block!")
        print("You can see the quality of GLM-4.5v's understanding above.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()