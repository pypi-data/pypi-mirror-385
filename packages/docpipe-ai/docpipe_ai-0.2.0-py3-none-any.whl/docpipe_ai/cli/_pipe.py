"""
CLI interface for docpipe-ai pipe command.

Provides the `docpipe-ai-pipe` command that reads JSONL from stdin,
processes it using OpenAI models, and writes JSONL to stdout.
"""

import argparse
import json
import logging
import sys
from typing import Any, Dict, Iterator

from ..pipelines.openai_compat import OpenAIPipeline

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def read_jsonl_from_stdin() -> Iterator[Dict[str, Any]]:
    """
    Read JSONL lines from stdin.

    Yields:
        Parsed JSON objects from stdin
    """
    for line in sys.stdin:
        line = line.strip()
        if line:
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON line: {e}")
                continue


def write_jsonl_to_stdout(items: Iterator[Dict[str, Any]]) -> None:
    """
    Write items as JSONL to stdout.

    Args:
        items: Iterator of dictionaries to write
    """
    for item in items:
        try:
            json.dump(item, sys.stdout, ensure_ascii=False)
            sys.stdout.write("\n")
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"Error writing JSON line: {e}")
            continue


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser for the CLI.

    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Process document blocks with AI to generate text descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default model
  docpipe-mini document.pdf | docpipe-ai-pipe > processed.jsonl

  # Use specific model
  docpipe-mini document.pdf | docpipe-ai-pipe --model gpt-4o > processed.jsonl

  # Custom concurrency and peek settings
  docpipe-mini document.pdf | docpipe-ai-pipe --max-concurrency 5 --peek-head 100 > processed.jsonl

  # With custom OpenAI endpoint
  docpipe-mini document.pdf | docpipe-ai-pipe --api-base https://api.example.com/v1 > processed.jsonl
        """
    )

    # OpenAI parameters
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (falls back to OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--api-base",
        help="Custom OpenAI API base URL (falls back to OPENAI_API_BASE env var)"
    )

    # Performance parameters
    parser.add_argument(
        "--max-concurrency",
        type=int,
        help="Maximum number of concurrent API calls (default: auto)"
    )
    parser.add_argument(
        "--peek-head",
        type=int,
        default=200,
        help="Number of items to sample when estimating iterator length (default: 200)"
    )
    parser.add_argument(
        "--max-batch-size",
        type=int,
        default=100,
        help="Maximum batch size for processing (default: 100)"
    )

    # Debugging parameters
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all logging output"
    )

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging
    if args.quiet:
        logging.getLogger().setLevel(logging.CRITICAL + 1)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate arguments
    if args.peek_head <= 0:
        logger.error("peek-head must be positive")
        sys.exit(1)

    if args.max_batch_size <= 0:
        logger.error("max-batch-size must be positive")
        sys.exit(1)

    if args.max_concurrency is not None and args.max_concurrency <= 0:
        logger.error("max-concurrency must be positive")
        sys.exit(1)

    try:
        # Initialize the pipeline
        logger.info(f"Initializing OpenAI pipeline with model: {args.model}")
        pipeline = OpenAIPipeline(
            model=args.model,
            api_key=args.api_key,
            api_base=args.api_base,
            max_concurrency=args.max_concurrency,
            peek_head=args.peek_head,
            max_batch_size=args.max_batch_size
        )

        # Read input from stdin
        logger.info("Reading JSONL input from stdin...")
        input_stream = read_jsonl_from_stdin()

        # Process the stream
        logger.info("Processing document blocks...")
        processed_stream = pipeline.iter_stream(input_stream)

        # Write output to stdout
        logger.info("Writing processed JSONL to stdout...")
        write_jsonl_to_stdout(processed_stream)

        logger.info("Processing completed successfully")

    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()