"""
OpenAI-Compatible Pipeline with Dynamic Batching.

Implements OpenAIPipeline that accepts any OpenAI client parameters and
uses dynamic batch sizing for optimal performance.
"""

from __future__ import annotations

import os
import time
from typing import Dict, Iterator, Any, Union, Optional, List
from pathlib import Path
import logging
import concurrent.futures
from itertools import islice

from ._base import BasePipeline, PipelineConfig
from .._batchSizer import peek_len, calc_batch_size

# Import docpipe if available
try:
    import docpipe as dp
except ImportError:
    dp = None

# Import LangChain components
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
except ImportError:
    ChatOpenAI = None  # type: ignore
    HumanMessage = None  # type: ignore
    SystemMessage = None  # type: ignore
    RunnablePassthrough = None  # type: ignore
    StrOutputParser = None  # type: ignore

# Import OpenAI directly for compatibility
try:
    import openai
except ImportError:
    openai = None  # type: ignore

logger = logging.getLogger(__name__)


class OpenAIPipeline(BasePipeline):
    """
    OpenAI-Compatible pipeline with dynamic batch sizing.

    Accepts any parameters that work with openai.OpenAI() and automatically
    creates LangChain LLM instances internally. Uses dynamic batch sizing
    to optimize performance based on estimated remaining elements.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        max_concurrency: Optional[int] = None,
        peek_head: int = 200,
        max_batch_size: int = 100,
        **openai_kwargs: Any
    ):
        """
        Initialize the OpenAI pipeline.

        Args:
            model: OpenAI model name (default: "gpt-4o-mini")
            api_key: OpenAI API key (falls back to OPENAI_API_KEY env var)
            api_base: Custom API base URL (falls back to OPENAI_API_BASE env var)
            max_concurrency: Maximum number of concurrent API calls
            peek_head: Number of items to sample when estimating iterator length
            max_batch_size: Maximum batch size for processing
            **openai_kwargs: Additional arguments passed to openai.OpenAI()
        """
        self.config = PipelineConfig(
            model=model,
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            api_base=api_base or os.getenv("OPENAI_API_BASE"),
            max_concurrency=max_concurrency,
            peek_head=peek_head,
            max_batch_size=max_batch_size,
            **openai_kwargs
        )

        # Initialize OpenAI client
        if openai is None:
            raise ImportError("openai package is required. Install with: pip install openai")

        self.client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_base,
            **{k: v for k, v in self.config.extra_params.items()
               if k not in ["model", "api_key", "api_base", "max_concurrency", "peek_head", "max_batch_size"]}
        )

        # Initialize LangChain LLM
        if ChatOpenAI is None:
            raise ImportError("langchain-openai package is required. Install with: pip install langchain-openai")

        llm_kwargs = {
            "model": model,
            "base_url": self.config.api_base,
            **{k: v for k, v in self.config.extra_params.items()
               if k not in ["model", "api_key", "api_base", "max_concurrency", "peek_head", "max_batch_size"]}
        }

        # Only add api_key if it's not None (ChatOpenAI expects SecretStr or None)
        if self.config.api_key is not None:
            llm_kwargs["api_key"] = self.config.api_key

        self.llm = ChatOpenAI(**llm_kwargs)

        # Set up processing chain for text generation
        self._setup_processing_chain()

    def _setup_processing_chain(self) -> None:
        """Set up the LangChain processing chain for text generation."""
        # System prompt for generating descriptions
        system_prompt = """You are an AI assistant that analyzes document content and generates descriptive text.
Your task is to describe what you see in images, tables, or other non-text content in a clear, concise manner.

Guidelines:
- Be descriptive but concise
- Focus on the main content and purpose
- Use neutral, objective language
- Include relevant details that would help someone understand the content"""

        # Create the processing chain
        self.processing_chain = (
            {
                "content": lambda x: x.get("content", ""),
                "context": lambda x: x.get("context", "")
            }
            | {
                "prompt": lambda x: f"Context: {x['context']}\n\nContent: {x['content']}\n\nPlease provide a clear description of this content:"
            }
            | self.llm
            | StrOutputParser()
        )

    def iter_file(self, file_path: Union[str, Path]) -> Iterator[Dict[str, Any]]:
        """
        Process a file using docpipe and return processed blocks.

        Args:
            file_path: Path to the file to process

        Returns:
            Iterator of processed blocks with updated text fields
        """
        if dp is None:
            raise ImportError("docpipe package is required. Install with: pip install docpipe-mini")

        # Use docpipe to serialize file and convert chunks to dict format
        chunks = dp.serialize(str(file_path))

        # Convert docpipe chunks to the expected dict format
        doc_blocks = self._chunks_to_blocks(chunks)
        return self.iter_stream(doc_blocks)

    def _chunks_to_blocks(self, chunks) -> List[Dict[str, Any]]:
        """
        Convert docpipe chunks to the expected block dictionary format.

        Args:
            chunks: Docpipe chunks from serialize()

        Returns:
            List of block dictionaries
        """
        blocks = []
        for chunk in chunks:
            # For text chunks, use the text attribute directly
            if hasattr(chunk, 'text') and chunk.text:
                chunk_text = chunk.text
            # For binary content (images, tables), try to decode binary_data
            elif hasattr(chunk, 'binary_data') and chunk.binary_data:
                if isinstance(chunk.binary_data, bytes):
                    try:
                        chunk_text = chunk.binary_data.decode('utf-8', errors='ignore')
                    except:
                        chunk_text = str(chunk.binary_data)
                elif isinstance(chunk.binary_data, str):
                    chunk_text = chunk.binary_data
                else:
                    chunk_text = str(chunk.binary_data)
            else:
                chunk_text = ""

            # Use doc_id if available, otherwise create hash from text or binary_data
            if hasattr(chunk, 'doc_id'):
                doc_id = str(chunk.doc_id)
            else:
                # Create hash from available content for consistent ID
                content_for_hash = chunk_text or (chunk.binary_data if hasattr(chunk, 'binary_data') else "")
                doc_id = str(hash(content_for_hash)) if content_for_hash else str(id(chunk))

            block = {
                "doc_id": doc_id,
                "page": getattr(chunk, 'page', 1),
                "bbox": getattr(chunk, 'bbox', [0, 0, 100, 100]),
                "type": chunk.type,
                "text": chunk_text,  # Keep original text for ALL blocks
                "binary_data": chunk.binary_data if hasattr(chunk, 'binary_data') else None
            }
            blocks.append(block)
        return blocks

    def iter_stream(self, stream: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Process a stream of document blocks with dynamic batching.

        Args:
            stream: Iterator of document blocks to process

        Returns:
            Iterator of processed blocks with updated text fields
        """
        # Estimate iterator length using peek_len
        est_len, restored_stream = peek_len(stream, head=self.config.peek_head)
        logger.info(f"Estimated document length: {est_len}")

        # Process blocks with dynamic batching
        processed_count = 0
        remaining_est = est_len

        while True:
            # Calculate optimal batch size for remaining items
            batch_size = calc_batch_size(remaining_est, self.config.max_batch_size)
            logger.info(f"Processing batch of size {batch_size} (estimated remaining: {remaining_est})")

            # Get next batch
            batch = list(islice(restored_stream, batch_size))
            if not batch:
                break  # No more items

            # Process the batch
            processed_batch = self._process_batch(batch)
            yield from processed_batch

            processed_count += len(batch)
            remaining_est = max(0, remaining_est - len(batch))

        logger.info(f"Processed {processed_count} blocks total")

    def _process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of blocks concurrently.

        Args:
            batch: List of document blocks to process

        Returns:
            List of processed blocks
        """
        # Filter blocks that need processing
        blocks_to_process = [block for block in batch if self._should_process_block(block)]

        # 详细日志：显示批次中每个块的处理决策
        print(f"\n[BATCH] Processing batch of {len(batch)} blocks:")
        for block in batch:
            block_type = block.get("type", "unknown")
            should_process = self._should_process_block(block)
            text_len = len(block.get("text", ""))
            binary_size = len(block.get("binary_data", b"")) if block.get("binary_data") else 0
            action = "AI_PROCESS" if should_process else "PASS_THROUGH"
            print(f"  {action:12s} | {block_type:6s} | Page:{block.get('page'):3d} | Text:{text_len:3d}ch | Binary:{binary_size:5d}B")

        if not blocks_to_process:
            print(f"[BATCH] No blocks need AI processing, returning original batch")
            # Return original blocks unchanged
            return batch

        print(f"[BATCH] Sending {len(blocks_to_process)} blocks to AI for processing...")

        # Determine max concurrency
        max_workers = self.config.max_concurrency or min(len(blocks_to_process), 10)

        # Process blocks concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all processing tasks
            future_to_block = {
                executor.submit(self._process_single_block, block): block
                for block in blocks_to_process
            }

            # Collect results
            results = {}
            for future in concurrent.futures.as_completed(future_to_block):
                block = future_to_block[future]
                try:
                    start_time = time.time()
                    processed_text = future.result()
                    end_time = time.time()
                    processing_time = end_time - start_time
                    results[id(block)] = processed_text
                    print(f"[AI_DONE] {block.get('type'):6s} | Page:{block.get('page'):3d} | Time:{processing_time:.2f}s | Output:{len(processed_text)}ch")
                except Exception as e:
                    logger.error(f"Error processing block {block.get('doc_id', 'unknown')}: {e}")
                    # Use original text on error
                    results[id(block)] = block.get("text", "")

        # Create processed batch
        processed_batch = []
        for block in batch:
            if self._should_process_block(block):
                # Get processed text for this block
                processed_text = results.get(id(block), block.get("text", ""))
                processed_block = self._preserve_block_structure(block, processed_text)
                processed_batch.append(processed_block)
            else:
                # Block didn't need processing, keep as-is
                processed_batch.append(block)

        return processed_batch

    def _should_process_block(self, block: Dict[str, Any]) -> bool:
        """
        Determine if a block should be processed by AI.

        Only process non-text blocks (image, table, etc.) that need AI-generated descriptions.
        Text blocks should pass through unchanged.

        Args:
            block: Document block dictionary

        Returns:
            True if the block should be processed by AI, False otherwise
        """
        block_type = block.get("type", "").lower()
        # Only process non-text blocks with AI
        return block_type not in ["text"]

    def _process_single_block(self, block: Dict[str, Any]) -> str:
        """
        Process a single block and return the generated text.

        Args:
            block: Document block to process

        Returns:
            Generated text for the block
        """
        block_type = block.get("type", "unknown")
        content = self._extract_content_for_processing(block)

        # Create context for the block
        context = f"Block type: {block_type}"
        if "page" in block:
            context += f", Page: {block['page']}"
        if "doc_id" in block:
            context += f", Document: {block['doc_id']}"

        # Create prompt for the LLM
        if block_type == "image":
            prompt = f"""请分析这张图片并提供清晰、简洁的中文描述。

{context}
内容: {content}

请用中文描述这张图片展示的内容，保持客观中性的表达方式。"""
        elif block_type == "table":
            prompt = f"""请分析这个表格并提供内容的清晰描述。

{context}
内容: {content}

请用中文描述这个表格包含的内容，使用结构化的表达方式。"""
        elif block_type == "text":
            prompt = f"""请分析这段文本内容并在需要时提供摘要或描述。

{context}
内容: {content}

请用中文提供这段文本的清晰描述或摘要。"""
        else:
            prompt = f"""请分析这个内容并提供描述。

{context}
内容: {content}

请用中文提供这个{block_type}内容的清晰描述。"""

        try:
            # Use the LLM directly with a simple prompt
            import base64

            system_message = """你是一个专业的文档内容分析AI助手。你的任务是分析文档中的图片、表格等非文本内容，并生成清晰的中文描述。

要求：
- 使用中文进行描述
- 描述要简洁但详细
- 专注于主要内容和用途
- 使用中性、客观的语言
- 包含有助于理解内容的相关细节"""

            # For images, include the actual image data
            if block_type == "image" and block.get("binary_data"):
                try:
                    # Convert binary image data to base64
                    image_base64 = base64.b64encode(block["binary_data"]).decode('utf-8')

                    # Create message with image
                    messages = [
                        SystemMessage(content=system_message),
                        HumanMessage(content=[
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ])
                    ]
                except Exception as img_error:
                    logger.error(f"Error encoding image: {img_error}")
                    # Fallback to text-only if image encoding fails
                    messages = [
                        SystemMessage(content=system_message),
                        HumanMessage(content=prompt + "\n\n注意：图片数据编码失败，请基于元信息进行描述。")
                    ]
            else:
                # For non-image content or no image data, use text-only
                messages = [
                    SystemMessage(content=system_message),
                    HumanMessage(content=prompt)
                ]

            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Error generating text for block {block.get('doc_id', 'unknown')}: {e}")
            # Return a fallback description
            return f"处理{block_type}内容失败 (生成失败)"

    def _extract_content_for_processing(self, block: Dict[str, Any]) -> str:
        """
        Extract relevant content from a block for processing.

        Args:
            block: Document block

        Returns:
            String content for AI processing
        """
        block_type = block.get("type", "").lower()

        if block_type == "image":
            # For images, we have binary data from docpipe
            binary_data = block.get("binary_data")
            if binary_data and isinstance(binary_data, bytes):
                return f"Image data (size: {len(binary_data)} bytes) from page {block.get('page', 'unknown')}"
            else:
                return f"Image content from page {block.get('page', 'unknown')}"
        elif block_type == "table":
            # For tables, we have binary data from docpipe
            binary_data = block.get("binary_data")
            if binary_data and isinstance(binary_data, bytes):
                return f"Table data (size: {len(binary_data)} bytes) from page {block.get('page', 'unknown')}"
            else:
                return f"Table content from page {block.get('page', 'unknown')}"
        elif block_type == "text":
            # For text blocks, use existing text or get from binary_data
            existing_text = block.get("text", "")
            if existing_text.strip():
                return existing_text
            else:
                binary_data = block.get("binary_data")
                if binary_data and isinstance(binary_data, (str, bytes)):
                    if isinstance(binary_data, bytes):
                        return binary_data.decode('utf-8', errors='ignore')
                    return str(binary_data)
                else:
                    return f"Text content from page {block.get('page', 'unknown')}"
        else:
            # For other types, use generic description
            return f"Content of type {block_type} from page {block.get('page', 'unknown')}"