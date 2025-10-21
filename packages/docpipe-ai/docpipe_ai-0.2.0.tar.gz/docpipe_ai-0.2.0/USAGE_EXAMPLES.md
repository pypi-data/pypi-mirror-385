# docpipe-ai 使用示例

## 概述

docpipe-ai 是一个 OpenAI 兼容的动态批次 AI 后处理器，专为 docpipe-mini 设计。它能够智能地估计文档长度并优化批次大小，只为 `text` 字段生成 AI 描述，保持其他字段不变。

## 基本使用

### 1. 命令行管道使用

```bash
# 基本用法：处理 PDF 文件
docpipe-mini document.pdf | docpipe-ai-pipe --model gpt-4o-mini > processed.jsonl

# 使用自定义模型和并发数
docpipe-mini document.pdf | docpipe-ai-pipe --model gpt-4o --max-concurrency 5 > processed.jsonl

# 自定义 peek 头大小和批次大小
docpipe-mini document.pdf | docpipe-ai-pipe --peek-head 100 --max-batch-size 50 > processed.jsonl

# 使用自定义 API 端点
docpipe-mini document.pdf | docpipe-ai-pipe --api-base https://api.example.com/v1 > processed.jsonl
```

### 2. Python 编程接口

```python
from docpipe_ai.pipelines.openai_compat import OpenAIPipeline

# 创建管道实例
pipeline = OpenAIPipeline(
    model="gpt-4o-mini",
    api_key="your-api-key",
    max_concurrency=10,
    peek_head=200,
    max_batch_size=100
)

# 处理文件
for block in pipeline.iter_file("document.pdf"):
    print(f"Type: {block['type']}, Text: {block['text']}")

# 处理流
blocks = iter([...])  # 来自 docpipe-mini 的块
processed = pipeline.iter_stream(blocks)
for block in processed:
    print(block)
```

## 输入输出格式

### 输入格式
```json
{"doc_id":"doc1","page":1,"bbox":[0,0,100,100],"type":"image","text":""}
{"doc_id":"doc1","page":1,"bbox":[100,0,200,100],"type":"table","text":""}
{"doc_id":"doc1","page":2,"bbox":[0,0,150,150],"type":"text","text":"已有文本"}
```

### 输出格式
```json
{"doc_id":"doc1","page":1,"bbox":[0,0,100,100],"type":"image","text":"AI 生成的图像描述"}
{"doc_id":"doc1","page":1,"bbox":[100,0,200,100],"type":"table","text":"AI 生成的表格描述"}
{"doc_id":"doc1","page":2,"bbox":[0,0,150,150],"type":"text","text":"已有文本"}
```

**注意：**
- 只有 `text` 字段被更新
- `type`、`bbox`、`page`、`doc_id` 等字段保持原值
- 已有内容的 `text` 字段不会被处理

## 动态批次算法

| 剩余项目数 | 批次大小 | 说明 |
|-----------|----------|------|
| ≤ 10      | = 剩余数 | 小文件 → 1 批次 |
| ≤ 50      | 10       | 中等规模 |
| ≤ 200     | 25       | 大规模 |
| ≤ 1,000   | 50       | 超大规模 |
| > 1,000   | 100      | 上限（可配置） |

## 环境变量

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://api.openai.com/v1"
```

## 性能优化建议

1. **小文件（< 50 个块）**：使用默认设置，会在一个批次中完成
2. **中等文件（50-500 个块）**：调整 `--max-concurrency` 控制并发数
3. **大文件（> 500 个块）**：考虑增加 `--peek-head` 以获得更好的长度估计
4. **成本控制**：使用较小的模型如 `gpt-4o-mini` 或调整 `--max-batch-size`

## 故障排除

### 常见错误

1. **ImportError: No module named 'docpipe_mini'**
   ```bash
   pip install docpipe-mini
   ```

2. **ImportError: No module named 'langchain_openai'**
   ```bash
   pip install "docpipe-ai[openai]"
   ```

3. **API 密钥错误**
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

### 调试模式

```bash
# 启用详细日志
docpipe-ai-pipe --verbose --model gpt-4o-mini < input.jsonl > output.jsonl

# 静默模式
docpipe-ai-pipe --quiet --model gpt-4o-mini < input.jsonl > output.jsonl
```

## 示例工作流

### 完整文档处理管道

```bash
# 1. 使用 docpipe-mini 提取文档块
docpipe-mini research_paper.pdf > blocks.jsonl

# 2. 使用 docpipe-ai 处理非文本块
docpipe-ai-pipe --model gpt-4o-mini < blocks.jsonl > processed_blocks.jsonl

# 3. 检查结果
head -5 processed_blocks.jsonl
```

### Python 批处理脚本

```python
import json
from docpipe_ai.pipelines.openai_compat import OpenAIPipeline

def batch_process_documents(file_paths):
    pipeline = OpenAIPipeline(model="gpt-4o-mini", max_concurrency=5)

    for file_path in file_paths:
        print(f"Processing {file_path}...")
        results = list(pipeline.iter_file(file_path))

        # 保存结果
        output_path = file_path.replace('.pdf', '_processed.jsonl')
        with open(output_path, 'w') as f:
            for result in results:
                json.dump(result, f)
                f.write('\n')

        print(f"Saved {len(results)} processed blocks to {output_path}")

# 使用示例
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
batch_process_documents(documents)
```

## 性能基准

基于动态批次大小的典型性能：

| 文档大小 | 块数量 | 预计批次 | 处理时间 |
|----------|--------|----------|----------|
| 小型文档 | 5-20   | 1        | < 10s    |
| 中型文档 | 50-200 | 2-8      | 30s-2min |
| 大型文档 | 500+   | 10+      | 2min-10min |

*注意：实际时间取决于模型速度和网络延迟。*