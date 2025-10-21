"""
Enhanced Image Format Detector

This module provides comprehensive image format detection for both
base64 strings and raw binary data.
"""

import struct
from typing import Optional, Union
from enum import Enum

class ImageFormat(Enum):
    """Supported image formats with their signatures."""
    JPEG = ("jpeg", b'\xff\xd8\xff')
    PNG = ("png", b'\x89PNG\r\n\x1a\n')
    GIF87 = ("gif", b'GIF87a')
    GIF89 = ("gif", b'GIF89a')
    BMP = ("bmp", b'BM')
    TIFF_LE = ("tiff", b'II*\x00')
    TIFF_BE = ("tiff", b'MM\x00*')
    WEBP = ("webp", b'RIFF')
    ICO = ("ico", b'\x00\x00\x01\x00')

    @classmethod
    def get_all_signatures(cls):
        """Get all format signatures for detection."""
        signatures = {}
        for format_type in cls:
            signatures[format_type.value[1]] = format_type.value[0]
        return signatures

def detect_image_format(data: Union[bytes, str]) -> Optional[str]:
    """
    Detect image format from binary data or base64 string.

    Args:
        data: Binary data or base64 string

    Returns:
        Format name (lowercase) or None if unknown
    """
    import base64

    # Convert base64 string to bytes if needed
    if isinstance(data, str):
        try:
            binary_data = base64.b64decode(data)
        except Exception:
            binary_data = data.encode('utf-8')  # Fallback
    else:
        binary_data = data

    # Check if we have enough data
    if len(binary_data) < 8:
        return None

    # Check each known format signature
    signatures = ImageFormat.get_all_signatures()

    for signature, format_name in signatures.items():
        if binary_data.startswith(signature):
            return format_name

    # Special case for WEBP (needs additional check)
    if binary_data.startswith(b'RIFF') and len(binary_data) >= 12:
        # WEBP format: RIFF...WEBP
        if binary_data[8:12] == b'WEBP':
            return 'webp'

    # Additional format detection based on more complex patterns
    return None

def get_detailed_format_info(data: Union[bytes, str]) -> dict:
    """
    Get detailed format information about the image data.

    Args:
        data: Binary data or base64 string

    Returns:
        Dictionary with format information
    """
    import base64

    # Convert to bytes if needed
    if isinstance(data, str):
        try:
            binary_data = base64.b64decode(data)
            is_base64 = True
        except Exception:
            binary_data = data.encode('utf-8')
            is_base64 = False
    else:
        binary_data = data
        is_base64 = False

    result = {
        'format': detect_image_format(data),
        'is_base64': is_base64,
        'size_bytes': len(binary_data),
        'confidence': 'high'
    }

    # Add confidence based on detection method
    if result['format'] is None:
        result['confidence'] = 'none'
    elif result['format'] == 'jpeg' and binary_data.startswith(b'\xff\xd8\xff\xe0'):
        result['confidence'] = 'very_high'  # JFIF header
    elif result['format'] == 'png' and binary_data.startswith(b'\x89PNG\r\n\x1a\n'):
        result['confidence'] = 'very_high'  # Full PNG signature

    # Add some header information for debugging
    result['header_hex'] = binary_data[:16].hex()
    result['header_ascii'] = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in binary_data[:16]])

    return result

# Quick test function
def test_format_detection():
    """Test the format detection with some sample data."""
    test_cases = [
        (b'\xff\xd8\xff\xe0\x00\x10JFIF', 'jpeg'),
        (b'\x89PNG\r\n\x1a\n', 'png'),
        (b'GIF87a', 'gif'),
        (b'BM', 'bmp'),
    ]

    print("Testing image format detection:")
    for data, expected in test_cases:
        detected = detect_image_format(data)
        status = "PASS" if detected == expected else "FAIL"
        print(f"Expected: {expected}, Detected: {detected}, Status: {status}")

if __name__ == "__main__":
    test_format_detection()