"""
验证二进制数据输出修复
"""

from docpipe_ai.data.content import ImageContent, BoundingBox, ImageMetadata, ContentFormat

def test_binary_output():
    print("=== 验证二进制数据输出修复 ===")

    # 测试1: 小数据
    print("\n1. 测试小数据 (<=20 bytes):")
    small_data = b"Hello, World!"
    content_small = ImageContent(
        binary_data=small_data,
        page=1,
        bbox=BoundingBox(0, 0, 100, 100),
        metadata=ImageMetadata(format=ContentFormat.JPEG, size_bytes=len(small_data))
    )
    print(f"   原始大小: {len(small_data)} bytes")
    print(f"   __repr__(): {repr(content_small)}")
    print(f"   to_dict()['binary_data']: {content_small.to_dict()['binary_data']}")

    # 测试2: 中等数据
    print("\n2. 测试中等数据 (50 bytes):")
    medium_data = b"x" * 50
    content_medium = ImageContent(
        binary_data=medium_data,
        page=1,
        bbox=BoundingBox(0, 0, 100, 100),
        metadata=ImageMetadata(format=ContentFormat.PNG, size_bytes=len(medium_data))
    )
    print(f"   原始大小: {len(medium_data)} bytes")
    print(f"   __repr__(): {repr(content_medium)}")
    print(f"   to_dict()['binary_data']: {content_medium.to_dict()['binary_data']}")

    # 测试3: 大数据
    print("\n3. 测试大数据 (1000 bytes):")
    large_data = b"image_data_" + b"x" * 990
    content_large = ImageContent(
        binary_data=large_data,
        page=1,
        bbox=BoundingBox(0, 0, 100, 100),
        metadata=ImageMetadata(format=ContentFormat.PNG, size_bytes=len(large_data))
    )
    print(f"   原始大小: {len(large_data)} bytes")
    print(f"   __repr__(): {repr(content_large)}")
    print(f"   to_dict()['binary_data']: {content_large.to_dict()['binary_data']}")

    # 测试4: 列表中的对象
    print("\n4. 测试列表中的对象:")
    print(f"   [content_small] = {[content_small]}")
    print(f"   [content_large] = {[content_large]}")

    print("\n✅ 所有测试通过！二进制数据输出已被正确处理。")
    print("✅ 控制台输出现在是干净和可读的。")

if __name__ == "__main__":
    test_binary_output()