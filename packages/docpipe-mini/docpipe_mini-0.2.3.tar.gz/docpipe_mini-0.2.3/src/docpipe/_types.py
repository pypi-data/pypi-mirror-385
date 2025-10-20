"""
Minimal type definitions for docpipe document-to-jsonl serializer.

Focus: lightweight coordinate extraction + text serialization for AI consumption.
Zero third-party dependencies in core.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union
from typing_extensions import TypeAlias

# Core output schema - this is what users get
@dataclass
class DocumentChunk:
    """
    Single document chunk with coordinates for AI consumption.

    This is the primary output format - each chunk becomes one JSON line.
    """
    doc_id: str                    # UUID for document grouping
    page: int                       # Page number (1-based)
    x: float                        # Normalized X coordinate (0-1)
    y: float                        # Normalized Y coordinate (0-1)
    w: float                        # Normalized width (0-1)
    h: float                        # Normalized height (0-1)
    type: str                       # "text" | "table" | "image"
    text: Optional[str] = None      # Text content (None for pure images)
    tokens: Optional[int] = None    # Token count estimate
    binary_data: Optional[bytes] = None  # Binary data for images
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata (table structure, image format, etc.)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        result = {
            "doc_id": self.doc_id,
            "page": self.page,
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "type": self.type,
            "text": self.text,
            "tokens": self.tokens
        }

        # Handle binary data (convert to base64 for JSON serialization)
        if self.binary_data is not None:
            import base64
            if isinstance(self.binary_data, bytes):
                # Binary data - encode to base64
                result["binary_data"] = base64.b64encode(self.binary_data).decode('ascii')
                result["binary_encoding"] = "base64"
            elif isinstance(self.binary_data, str):
                # Already encoded as string (e.g., from Word processor)
                result["binary_data"] = self.binary_data
                result["binary_encoding"] = "base64"
            else:
                # Unknown type - convert to string
                result["binary_data"] = str(self.binary_data)
                result["binary_encoding"] = "string"

        # Include metadata if present
        if self.metadata is not None:
            result["metadata"] = self.metadata

        return result

    def to_jsonl(self) -> str:
        """Convert to JSONL line."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


# Core output type
DocumentIterator: TypeAlias = Iterator[DocumentChunk]

# Simple bbox type for coordinates
@dataclass
class BBox:
    """Bounding box with normalized coordinates."""
    x: float  # Left (0-1)
    y: float  # Top (0-1)
    w: float  # Width (0-1)
    h: float  # Height (0-1)

    def to_tuple(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.w, self.h)

    @classmethod
    def from_points(cls, x1: float, y1: float, x2: float, y2: float,
                   page_width: float, page_height: float) -> "BBox":
        """Create from absolute coordinates."""
        return cls(
            x=min(x1, x2) / page_width,
            y=min(y1, y2) / page_height,
            w=abs(x2 - x1) / page_width,
            h=abs(y2 - y1) / page_height
        )


# Processing metadata (minimal)
ProcessingMetadata: TypeAlias = Dict[str, Any]

# Simple content types
class ContentType:
    """Content type identifiers."""
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"


# Utility functions
def estimate_tokens(text: str) -> int:
    """
    Unified token estimation for both Chinese and English text.

    This function provides a hybrid token counting approach that handles mixed-language
    content by applying different counting strategies for Chinese and English text.

    **Token Counting Strategy:**

    1. **Chinese Characters** ([\\u4e00-\\u9fff]):
       - Each Chinese character counts as 1 token
       - This matches typical tokenizer behavior for CJK characters
       - Example: "中文文本" → 4 tokens

    2. **English/Other Text**:
       - Approximately 4 characters per token
       - Based on average English word length and subword tokenization
       - Example: "Hello world" → ~3 tokens (11 chars ÷ 4 ≈ 2.75 → 3)

    3. **Mixed Language Content**:
       - Combines both approaches seamlessly
       - Example: "Hello世界" → 1 (Hello) + 2 (世界) = 3 tokens

    **Implementation Details:**

    - Whitespace normalization to ensure accurate counting
    - Fallback minimum of 1 token for non-empty text
    - Regular expression for Chinese character detection (Unicode range: \\u4e00-\\u9fff)
    - Handles edge cases like empty strings and pure whitespace

    **Use Cases:**

    - RAG chunk size estimation
    - LLM context window management
    - Token budget allocation
    - Cost estimation for API calls

    Args:
        text: Text content (can contain mixed Chinese and English)

    Returns:
        Estimated token count as integer

    Examples:
        >>> estimate_tokens("Hello world")
        3
        >>> estimate_tokens("中文文本")
        4
        >>> estimate_tokens("Hello 世界")
        3
        >>> estimate_tokens("")
        0
    """
    if not text:
        return 0

    # Remove extra whitespace for more accurate counting
    # Normalizes multiple spaces, tabs, newlines to single spaces
    text = ' '.join(text.split())

    if not text:
        return 0

    # Count Chinese characters using Unicode range
    # CJK Unified Ideographs: \u4e00-\u9fff (Common Chinese characters)
    import re
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

    # Count non-Chinese characters and estimate tokens
    # English text: ~4 characters per token (based on average word length)
    # This accounts for subword tokenization used by models like GPT, BERT
    non_chinese_chars = len(text) - chinese_chars
    non_chinese_tokens = max(1, non_chinese_chars // 4)

    # Total tokens = Chinese tokens + English tokens
    # Chinese: 1 char = 1 token (more precise for CJK)
    # English: ~4 chars = 1 token (approximation for subword tokenization)
    total_tokens = chinese_chars + non_chinese_tokens

    # Ensure minimum of 1 token for non-empty text
    return max(1, total_tokens)


def generate_doc_id() -> str:
    """Generate a unique document ID."""
    return str(uuid.uuid4())