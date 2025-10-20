"""
文档加载器模块

提供各种文档格式的序列化器，基于 protocol-oriented 设计。

支持的格式：
- PDF: PdfiumLoader (BSD), PyMuPDFLoader (AGPL, 更高性能)
- DOCX: DocxSerializer
- XLSX: XlsxSerializer

使用示例：
    from docpipe.loaders import PyMuPDFLoader

    loader = PyMuPDFLoader()
    for chunk in loader.serialize("document.pdf"):
        print(chunk.to_jsonl())
"""

# 导入主要加载器类
from ._pdfium import PdfiumSerializer
from .pymupdf_serializer import PyMuPDFLoader
from ._docx import DocxSerializer
from ._xlsx import XlsxSerializer

# 新的重构版本
from .pymupdf_serializer import PyMuPDFLoader

# 为了向后兼容，提供旧名称
PyMuPDFSerializer = PyMuPDFLoader

__all__ = [
    "PdfiumSerializer",
    "PyMuPDFSerializer",
    "PyMuPDFLoader",  # 新的推荐名称
    "DocxSerializer",
    "XlsxSerializer"
]