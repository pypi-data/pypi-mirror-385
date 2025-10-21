#!/usr/bin/env python3
"""
Run docpipe-ai pipeline with real processing to see the effects.
"""

import sys
import os
import time
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from docpipe_ai.pipelines.openai_compat import OpenAIPipeline
import docpipe as dp

def run_pipeline_demo():
    """Run the complete pipeline with real AI processing."""
    print("=" * 60)
    print("DOPIPE-AI REAL PROCESSING DEMO")
    print("=" * 60)

    # Create pipeline with your settings
    print("Creating pipeline with GLM-4.5v...")
    pipeline = OpenAIPipeline(
        api_key="f7efc2365fbb43b5b203bb2f15dcc1be.PfLGGLhHUGMTopWX",
        api_base="https://open.bigmodel.cn/api/paas/v4/",
        model="glm-4.5v",
        max_concurrency=2,
        peek_head=50,
        max_batch_size=3  # Small batch for demo
    )
    print("PASS Pipeline created successfully")

    # Test file
    test_file = os.path.join(os.path.dirname(__file__), "tests", "data", "pdf", "1.pdf")
    if not os.path.exists(test_file):
        print(f"ERROR: Test file {test_file} not found")
        return

    print(f"\nProcessing file: {test_file}")
    print("-" * 40)

    # Track processing statistics
    stats = {
        'total_blocks': 0,
        'processed_blocks': 0,
        'text_blocks': 0,
        'image_blocks': 0,
        'table_blocks': 0,
        'other_blocks': 0,
        'processing_time': 0,
        'results': []
    }

    try:
        start_time = time.time()

        # Process the file with limit to avoid too many API calls
        block_limit = 10  # Process only first 10 blocks for demo
        processed_count = 0

        print("Starting AI processing...")
        print("(Limiting to first 10 blocks for demo)\n")

        for block in pipeline.iter_file(test_file):
            if processed_count >= block_limit:
                break

            stats['total_blocks'] += 1

            # Count block types
            block_type = block['type']
            if block_type == 'text':
                stats['text_blocks'] += 1
            elif block_type == 'image':
                stats['image_blocks'] += 1
            elif block_type == 'table':
                stats['table_blocks'] += 1
            else:
                stats['other_blocks'] += 1

            # Check if block was actually processed (text field filled)
            if block['text'] and block['text'].strip():
                stats['processed_blocks'] += 1

            # Display result
            print(f"Block {processed_count + 1}: {block_type.upper()} (Page {block['page']})")
            print(f"  Generated Text: {block['text'][:150]}...")
            print("-" * 40)

            # Store result for summary
            stats['results'].append({
                'block_num': processed_count + 1,
                'type': block_type,
                'page': block['page'],
                'text_length': len(block['text']),
                'text_preview': block['text'][:100] + "..." if len(block['text']) > 100 else block['text']
            })

            processed_count += 1

        end_time = time.time()
        stats['processing_time'] = end_time - start_time

        # Print summary
        print("\n" + "=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        print(f"Total blocks processed: {stats['total_blocks']}")
        print(f"Blocks with AI-generated text: {stats['processed_blocks']}")
        print(f"Processing time: {stats['processing_time']:.2f} seconds")
        print(f"Average time per block: {stats['processing_time']/stats['total_blocks']:.2f} seconds")

        print(f"\nBlock type distribution:")
        print(f"  Text blocks: {stats['text_blocks']}")
        print(f"  Image blocks: {stats['image_blocks']}")
        print(f"  Table blocks: {stats['table_blocks']}")
        print(f"  Other blocks: {stats['other_blocks']}")

        # Save detailed results to file
        output_file = "pipeline_demo_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f"\nDetailed results saved to: {output_file}")

        # Show a few sample results
        print("\nSAMPLE RESULTS:")
        print("-" * 40)
        for result in stats['results'][:3]:
            print(f"Block {result['block_num']} ({result['type']}):")
            print(f"  Page: {result['page']}")
            print(f"  Text: {result['text_preview']}")
            print()

        print("PASS Demo completed successfully!")
        return True

    except Exception as e:
        print(f"ERROR during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_batch_size_demo():
    """Demonstrate different batch sizes with a small sample."""
    print("\n" + "=" * 60)
    print("BATCH SIZE DEMONSTRATION")
    print("=" * 60)

    try:
        # Create different pipeline configurations
        configs = [
            {"name": "Conservative", "max_batch_size": 1, "max_concurrency": 1},
            {"name": "Balanced", "max_batch_size": 3, "max_concurrency": 2},
            {"name": "Aggressive", "max_batch_size": 5, "max_concurrency": 3}
        ]

        test_file = os.path.join(os.path.dirname(__file__), "tests", "data", "pdf", "1.pdf")

        # Get a small sample of chunks
        chunks = list(dp.serialize(test_file))[:15]  # Only 15 chunks for demo

        for config in configs:
            print(f"\n{config['name']} Configuration:")
            print(f"  Max batch size: {config['max_batch_size']}")
            print(f"  Max concurrency: {config['max_concurrency']}")

            pipeline = OpenAIPipeline(
                api_key="f7efc2365fbb43b5b203bb2f15dcc1be.PfLGGLhHUGMTopWX",
                api_base="https://open.bigmodel.cn/api/paas/v4/",
                model="glm-4.5v",
                **config
            )

            # Convert chunks to blocks
            blocks = pipeline._chunks_to_blocks(chunks)
            print(f"  Processing {len(blocks)} blocks...")

            # This would normally call the AI, but we'll just simulate
            print(f"  Estimated processing time: {len(blocks) * 2.0:.1f} seconds (estimated)")
            print(f"  Estimated API calls: {len(blocks)}")

        print("\nNote: Actual processing time depends on API response speed and complexity.")

    except Exception as e:
        print(f"Batch size demo failed: {e}")

if __name__ == "__main__":
    # Run main demo
    success = run_pipeline_demo()

    # Run batch size demo
    run_batch_size_demo()

    if success:
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYour docpipe-ai pipeline is working with GLM-4.5v!")
        print("You can see the AI-generated text descriptions above.")
        print("\nTo process larger documents, adjust the parameters:")
        print("- Increase 'max_batch_size' for faster processing")
        print("- Increase 'max_concurrency' for parallel processing")
        print("- Adjust 'peek_head' for better length estimation")
    else:
        print("\nDemo failed. Please check the error messages above.")