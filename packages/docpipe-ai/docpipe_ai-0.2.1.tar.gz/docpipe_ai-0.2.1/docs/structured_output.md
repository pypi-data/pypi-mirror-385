# 结构化输出功能

docpipe-ai支持结构化AI输出，允许AI处理器返回格式化的JSON数据，而不仅仅是纯文本。

## 功能特性

### 1. 多种分析类型
- **合同分析** (`ContentAnalysisType.CONTRACT`) - 专门用于合同文档分析
- **表格提取** (`ContentAnalysisType.TABLE`) - 专门用于表格数据提取
- **通用分析** (`ContentAnalysisType.GENERAL`) - 通用图片内容分析
- **自定义分析** (`ContentAnalysisType.CUSTOM`) - 使用自定义JSON schema

### 2. 结构化数据格式
返回的数据包含以下结构：
```json
{
  "image_id": "唯一图片标识",
  "original_image_hash": "原始图片哈希",
  "summary_text": "主要摘要文本",
  "content_type": "内容类型 (table/text/non_text/mixed)",
  "content_details": {
    "content_summary": "内容摘要",
    "key_elements": ["关键信息1", "关键信息2"],
    "text_content": "文本内容",
    "non_text_content": "非文本内容描述",
    "document_structure": "文档结构信息"
  },
  "processing_metadata": {
    "confidence_score": 0.95,
    "model_used": "gpt-4o",
    "content_quality": "high/medium/low"
  },
  "tags": ["标签1", "标签2"],
  "categories": ["分类1", "分类2"]
}
```

## 使用方法

### 1. 基本配置

```python
from docpipe_ai.processors.adaptive_image_processor import AdaptiveImageProcessor
from docpipe_ai.data.config import ProcessingConfig, ContentAnalysisType

# 创建合同分析配置
config = ProcessingConfig.create_contract_analysis_config()
processor = AdaptiveImageProcessor.create_openai_processor(
    api_key="your-api-key",
    model="gpt-4o",
    config=config
)
```

### 2. 预定义配置

```python
# 合同分析配置
contract_config = ProcessingConfig.create_contract_analysis_config()

# 表格提取配置
table_config = ProcessingConfig.create_table_extraction_config()

# 结构化输出通用配置
structured_config = ProcessingConfig.create_structured_output_config(
    analysis_type=ContentAnalysisType.GENERAL,
    model_name="gpt-4o"
)
```

### 3. 自定义配置

```python
from docpipe_ai.data.config import ResponseFormatType, ContentAnalysisType

# 定义自定义Schema
custom_schema = {
    "type": "object",
    "properties": {
        "document_type": {"type": "string"},
        "title": {"type": "string"},
        "key_points": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["document_type", "title"]
}

# 创建自定义配置
config = ProcessingConfig(
    response_format=ResponseFormatType.STRUCTURED,
    content_analysis_type=ContentAnalysisType.CUSTOM,
    custom_schema=custom_schema,
    model_name="gpt-4o",
    temperature=0.3
)
```

### 4. 处理图片

```python
from docpipe_ai.data.content import ImageContent

# 创建ImageContent
image_content = ImageContent(
    binary_data=image_bytes,
    page=1,
    bbox=BoundingBox(0, 0, 100, 100),
    metadata=ImageMetadata(format=ContentFormat.JPEG, size_bytes=len(image_bytes))
)

# 处理图片
result = processor.process_batch([image_content])

# 访问结构化数据
for processed_result in result:
    if processed_result.structured_data:
        structured_data = processed_result.structured_data
        print(f"内容类型: {structured_data['content_type']}")
        print(f"摘要: {structured_data['summary_text']}")
        print(f"置信度: {structured_data['processing_metadata']['confidence_score']}")
```

## 配置参数

### ProcessingConfig参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `response_format` | `ResponseFormatType` | `TEXT` | 响应格式类型 |
| `content_analysis_type` | `ContentAnalysisType` | `GENERAL` | 内容分析类型 |
| `custom_schema` | `Dict[str, Any]` | `None` | 自定义JSON schema |
| `include_confidence_scores` | `bool` | `True` | 是否包含置信度评分 |
| `include_processing_metadata` | `bool` | `True` | 是否包含处理元数据 |

### 响应格式类型

- `ResponseFormatType.TEXT` - 纯文本响应
- `ResponseFormatType.JSON` - JSON格式响应
- `ResponseFormatType.STRUCTURED` - 结构化JSON响应（推荐）

### 内容分析类型

- `ContentAnalysisType.GENERAL` - 通用内容分析
- `ContentAnalysisType.CONTRACT` - 合同文档分析
- `ContentAnalysisType.TABLE` - 表格数据提取
- `ContentAnalysisType.DOCUMENT` - 文档结构分析
- `ContentAnalysisType.CUSTOM` - 自定义分析

## 完整示例

```python
from docpipe import PyMuPDFSerializer
from docpipe_ai.processors.adaptive_image_processor import AdaptiveImageProcessor
from docpipe_ai.data.config import ProcessingConfig
from docpipe_ai.data.content import ImageContent, BoundingBox, ImageMetadata, ContentFormat
import base64

# 1. 创建配置
config = ProcessingConfig.create_contract_analysis_config()

# 2. 创建处理器
processor = AdaptiveImageProcessor.create_openai_processor(
    api_key="your-api-key",
    api_base="https://api.openai.com/v1/",
    model="gpt-4o",
    config=config
)

# 3. 加载PDF文档
serializer = PyMuPDFSerializer()
image_contents = []

for chunk in serializer.iterate_chunks("document.pdf"):
    if chunk.type == "image":
        # 转换为ImageContent
        if isinstance(chunk.binary_data, str):
            image_bytes = base64.b64decode(chunk.binary_data)
        else:
            image_bytes = chunk.binary_data

        image_content = ImageContent(
            binary_data=image_bytes,
            page=chunk.page,
            bbox=BoundingBox.from_list(chunk.bbox),
            metadata=ImageMetadata(
                format=ContentFormat.JPEG,
                size_bytes=len(image_bytes)
            )
        )
        image_contents.append(image_content)

# 4. 处理图片
results = processor.process_batch(image_contents)

# 5. 处理结果
for result in results:
    if result.status.value == 'completed':
        print(f"图片 {result.original.page} 处理成功")

        # 访问结构化数据
        if result.structured_data:
            data = result.structured_data
            print(f"内容类型: {data['content_type']}")
            print(f"摘要: {data['summary_text']}")

            # 关键信息
            key_elements = data['content_details']['key_elements']
            for element in key_elements:
                print(f"  - {element}")

            # 处理元数据
            metadata = data['processing_metadata']
            print(f"置信度: {metadata['confidence_score']}")
            print(f"内容质量: {metadata['content_quality']}")
    else:
        print(f"处理失败: {result.error_message}")
```

## 注意事项

1. **API兼容性** - 确保使用的AI模型支持结构化输出（如GPT-4o、GPT-4 Turbo等）
2. **Schema验证** - 自定义schema必须符合JSON Schema规范
3. **性能考虑** - 结构化输出可能比纯文本输出稍慢，但提供更好的数据质量
4. **错误处理** - 当JSON解析失败时，系统会自动降级为错误结果

## 测试

运行测试来验证结构化输出功能：

```bash
python tests/test_structured_output.py
```

查看演示示例：

```bash
python examples/structured_output_demo.py
```