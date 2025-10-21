# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview
**docpipe-ai** – **Protocol-oriented & Mixin-based** AI content processor for `docpipe-mini`.
Goal: provide **flexible AI processing capabilities** with:

1. **Protocol-oriented design** - define capabilities via `typing.Protocol`
2. **Mixin-based implementation** - reusable components via composition
3. **External flow control** - users control document parsing, AI processes content
4. **Adaptive batch processing** - dynamic optimization based on content
5. **Multi-provider support** - pluggable AI providers (OpenAI, Anthropic, etc.)

**Responsibility: AI-powered content analysis and description generation.**

## Project Status
- **Phase**: Refactoring to Protocol-oriented + Mixin architecture
- **Version**: 0.1.0a3 → 0.2.0 (refactoring)
- **Python**: 3.11+ locked
- **Package manager**: `uv`

## Architecture Evolution

### Current Architecture (Legacy)
```
PDF ──▶ docpipe-mini ──▶ Iterator[Dict] ──▶ OpenAIPipeline.iter_file()
                                      │         │
                                      │ (dynamic batch)
                                      ▼         ▼
                            ┌-------------------------┐
                            │  peek_len(head=200)     │  ← O(1) memory
                            │  ▼                      │
                            │ calc_batch_size(rem)    │  ← log ladder
                            │  ▼                      │
                            │ LangChain batch map     │  ← concurrency
                            │  ▼                      │
                            │ image→text (gpt-4o)     │  ← ONLY mutate
                            │  ▼                      │
                            │ text field updated      │  ← type unchanged
                            └-------------------------┘
                                      │
                                      ▼
                            Iterator[Dict] (schema不变)
```

### New Architecture (Protocol-oriented + Mixin)
```
User Flow Control ──▶ DocxSerializer ──▶ ImageContent[] ──▶ AdaptiveImageProcessor
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Protocol Layer                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │  Batchable      │  │  AIProcessable  │  │   Cacheable     │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Mixin Layer                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │DynamicBatching  │  │OpenAIProcessing │  │  MemoryCache    │     │
│  │Mixin            │  │Mixin            │  │Mixin            │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Concrete Implementation                            │
│              AdaptiveImageProcessor                                  │
│    (Combines protocols + mixins + hook methods)                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Design Rules (New Architecture)
1. **Protocol-oriented** – capabilities defined via `typing.Protocol`, no forced inheritance
2. **Mixin Composition** – reusable implementations via Mixin classes with `self: Protocol` typing
3. **External Flow Control** – users control document parsing, AI focuses on content processing
4. **Adaptive Batching** – dynamic optimization based on content type and processing load
5. **Type Safety** – static type checking with mypy/pyright, zero runtime overhead
6. **Pluggable Providers** – support multiple AI providers through unified interface

## Protocol-oriented + Mixin Design Pattern
```python
# Define capabilities via Protocol (interface contracts)
@runtime_checkable
class Batchable(Protocol):
    @abstractmethod
    def should_process_batch(self, batch_size: int, total_items: int) -> bool: ...

# Provide implementations via Mixin (reusable components)
class DynamicBatchingMixin(Generic[T]):
    def calculate_optimal_batch_size(self: "Batchable", remaining_items: int) -> int: ...

# Combine via composition (zero cost)
class AdaptiveImageProcessor(Batchable, DynamicBatchingMixin[ImageContent]):
    def should_process_batch(self, batch_size: int, total_items: int) -> bool:
        # Hook method implementation
        return batch_size <= self.config.max_concurrency * 2
```

## New User Journey (External Flow Control)
```python
# 1. install
uv add docpipe-mini docpipe-ai

# 2. User controls document parsing
from docpipe import DocxSerializer
from docpipe_ai.processors.image_processor import AdaptiveImageProcessor
from docpipe_ai._types import ImageContent, ProcessingConfig

# 3. Extract content externally
serializer = DocxSerializer()
images = []
for chunk in serializer.iterate_chunks("document.docx"):
    if chunk.type == "image":
        images.append(ImageContent(
            binary_data=chunk.binary_data,
            content_type=ContentType.IMAGE,
            page=chunk.page,
            bbox=chunk.bbox
        ))

# 4. AI processing (adaptive batching)
processor = AdaptiveImageProcessor(ProcessingConfig(model_name="gpt-4o-mini"))
results = processor.process_images(images)

# 5. Use processed results
for result in results:
    print(f"Page {result.original.page}: {result.processed_text}")
```

## New Directory Layout (Protocol-oriented + Mixin)
```
docpipe-ai/
├── src/docpipe_ai/
│   ├── _types.py                  # Enhanced type definitions (NEW)
│   ├── data/                      # Data structures (NEW)
│   │   ├── __init__.py
│   │   ├── content.py            # ImageContent, ProcessedContent
│   │   └── config.py             # ProcessingConfig, BatchConfig
│   ├── core/                      # Core protocols (NEW)
│   │   ├── __init__.py
│   │   └── protocols.py          # Batchable, AIProcessable, Cacheable
│   ├── mixins/                    # Reusable implementations (NEW)
│   │   ├── __init__.py
│   │   ├── batch_processing.py   # DynamicBatchingMixin
│   │   ├── ai_processing.py      # OpenAIProcessingMixin
│   │   └── caching.py            # MemoryCacheMixin
│   ├── providers/                 # AI provider abstractions (NEW)
│   │   ├── __init__.py
│   │   ├── base.py               # BaseProvider Protocol
│   │   ├── openai_provider.py    # OpenAI implementation
│   │   └── anthropic_provider.py # Anthropic implementation
│   ├── processors/                # Concrete processors (NEW)
│   │   ├── __init__.py
│   │   ├── image_processor.py    # AdaptiveImageProcessor
│   │   └── base_processor.py     # BaseProcessor ABC
│   ├── api/                       # Simple user interfaces (NEW)
│   │   ├── __init__.py
│   │   └── simple_interface.py   # DocPipeAI class
│   ├── pipelines/                 # Legacy support (DEPRECATED)
│   │   ├── __init__.py
│   │   ├── _base.py              # BasePipeline ABC
│   │   └── openai_compat.py      # OpenAIPipeline (legacy)
│   ├── cli/
│   │   └── _pipe.py
│   └── ...
├── tests/
├── docs/
└── pyproject.toml
```

## Key Classes (New Architecture)
| Module | Purpose |
|--------|---------|
| `core/protocols.py` | Core Protocol definitions (Batchable, AIProcessable, Cacheable) |
| `data/content.py` | Data structures (ImageContent, ProcessedContent) |
| `data/config.py` | Configuration classes (ProcessingConfig, BatchConfig) |
| `mixins/batch_processing.py` | DynamicBatchingMixin - reusable batch logic |
| `mixins/ai_processing.py` | OpenAIProcessingMixin - reusable AI logic |
| `mixins/caching.py` | MemoryCacheMixin - reusable caching logic |
| `processors/image_processor.py` | AdaptiveImageProcessor - concrete implementation |
| `providers/openai_provider.py` | OpenAI provider implementation |
| `api/simple_interface.py` | DocPipeAI - simplified user interface |

## Legacy Classes (Deprecated)
| File | Purpose |
|------|---------|
| `pipelines/_base.py` | `BasePipeline` ABC (legacy) |
| `pipelines/openai_compat.py` | `OpenAIPipeline` - legacy implementation |

## Dynamic Batch Algorithm
| Estimated Remaining | Batch Size | Notes |
|---------------------|------------|-------|
| ≤ 10                | = remaining| small file → 1 batch |
| ≤ 50                | 10         | mid tail |
| ≤ 200               | 25         | |
| ≤ 1 000             | 50         | |
| > 1 000             | 100        | upper cap (configurable) |

**Peek implementation**: `peek_len(iter, head=200)` → `(est_len, restored_iter)`  
Memory overhead = O(head) **only**.

## Dependencies
| Extra | Size | License | Purpose |
|-------|------|---------|---------|
| *(none)* | 0 MB | PSF | core + langchain-core |
| `openai` | +11 MB | Apache | default chat/vision |
| `anthropic` | +12 MB | Apache | Claude backend |
| `dev` | +90 MB | mixed | pytest, mypy, pytest-asyncio |

## Development Setup
```bash
git clone <repo> && cd docpipe-ai
uv sync --extra dev
pytest -m "not bench"
mypy --strict
```

## Configuration & ENV
| ENV VAR | Description |
|---------|-------------|
| `OPENAI_API_KEY` | fallback if not passed |
| `OPENAI_API_BASE` | optional custom endpoint |

## CLI Reference
```bash
docpipe-ai-pipe \
  [--model MODEL] \
  [--max-concurrency N] \
  [--peek-head N]          # default 200
```

## Performance Targets
| Metric | Target |
|--------|--------|
| wheel size | ≤ 4 MB |
| memory peak | ≤ 50 MB (100-batch, 10 MB PDF) |
| small file (≤10 obj) | 1 batch, < 3 s |
| large file (3 k obj) | 100-batch, < 120 s |
| mypy `--strict` | pass |

## Known Gotchas
| Gotcha | Mitigation |
|--------|------------|
| infinite iterator | falls back to `max_batch_size=100` |
| peek accuracy |误差 ≤ 200（head 可调） |
| rate-limit sleep | 阻塞式；后续可换 async |
| vision cost | image detail=`low` by default |

## Implementation Roadmap (Protocol-oriented + Mixin Refactoring)
| Phase | Task |
|-------|------|
| **Phase 1** | **Type System Refactoring** |
| P1-D1 | Update `_types.py` with Protocol-oriented types |
| P1-D2 | Create `core/protocols.py` with core protocols |
| P1-D3 | Create `data/` module with data structures |
| **Phase 2** | **Mixin Implementation** |
| P2-D1 | Create `mixins/batch_processing.py` |
| P2-D2 | Create `mixins/ai_processing.py` |
| P2-D3 | Create `mixins/caching.py` |
| **Phase 3** | **Provider Abstraction** |
| P3-D1 | Create `providers/base.py` |
| P3-D2 | Implement `providers/openai_provider.py` |
| P3-D3 | Add `providers/anthropic_provider.py` |
| **Phase 4** | **Processor Implementation** |
| P4-D1 | Create `processors/image_processor.py` |
| P4-D2 | Implement `AdaptiveImageProcessor` |
| P4-D3 | Add comprehensive unit tests |
| **Phase 5** | **User Interface** |
| P5-D1 | Create `api/simple_interface.py` |
| P5-D2 | Update CLI for new interface |
| P5-D3 | Add migration guide |

## Success Criteria for Refactoring
- [ ] All protocols defined with `typing.Protocol` + `@runtime_checkable`
- [ ] Mixin classes work with `self: Protocol` typing and pass mypy
- [ ] `AdaptiveImageProcessor` combines protocols + mixins correctly
- [ ] External flow control works with user-provided `ImageContent[]`
- [ ] Adaptive batching optimizes based on content type and load
- [ ] Memory caching improves performance for duplicate content
- [ ] Multiple AI providers supported through unified interface
- [ ] Legacy `OpenAIPipeline` remains functional for backward compatibility
- [ ] `mypy --strict` passes for all new code
- [ ] Comprehensive test coverage (>90%)

## Migration Guide
```python
# Old way (deprecated)
from docpipe_ai.pipelines.openai_compat import OpenAIPipeline
pipeline = OpenAIPipeline(model="gpt-4o")
for block in pipeline.iter_file("document.pdf"):
    print(block)  # legacy flow

# New way (recommended)
from docpipe_ai.processors.image_processor import AdaptiveImageProcessor
from docpipe_ai._types import ImageContent, ProcessingConfig

processor = AdaptiveImageProcessor(ProcessingConfig(model_name="gpt-4o"))
results = processor.process_images(image_list)  # external flow
```

---

Ready to refactor – start with `src/docpipe_ai/_types.py` and build Protocol-oriented architecture.