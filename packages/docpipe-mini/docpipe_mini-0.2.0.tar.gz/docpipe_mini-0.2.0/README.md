# docpipe

**Protocol-oriented document serialization with coordinate-aware chunks for AI**

`docpipe` converts documents into coordinate-aware chunks perfect for AI consumption. Built with a protocol-oriented mixin design for extensibility, zero-dependency core, and enterprise-grade logging.

## 🚀 Quick Start

```bash
# Install (5 MB core, zero dependencies)
pip install docpipe

# Install PDF support (+11 MB, BSD license)
pip install docpipe[pdf]

# Convert document to JSONL
python -m docpipe serialize document.pdf > document.jsonl
```

## 📖 Usage

### Python API

```python
from docpipe import DocxSerializer, XlsxSerializer, PdfiumSerializer

# Word documents with advanced features
with DocxSerializer() as serializer:
    # Configure logging and serialization
    serializer.configure_logging(enable_performance_logging=True, log_level="DEBUG")
    serializer.configure_memory_limit(max_mem_mb=512)

    # Stream chunks for memory efficiency
    for chunk in serializer.iterate_chunks("report.docx"):
        print(f"Type: {chunk.type}, Position: ({chunk.x:.2f}, {chunk.y:.2f})")
        print(f"Content: {chunk.text[:100]}...")

# Excel files with header injection
excel = XlsxSerializer()
excel.configure_header_injection(header_row=1)  # Use first row as headers
for chunk in excel.iterate_chunks("data.xlsx"):
    headers = chunk.metadata.get('headers', [])
    print(f"Headers: {headers}")
    print(f"Data: {chunk.text}")

# PDF processing
pdf = PdfiumSerializer()
for chunk in pdf.iterate_chunks("document.pdf"):
    if chunk.type == "table":
        print(f"Table with {chunk.metadata.get('row_count', 0)} rows")
    elif chunk.type == "text":
        print(f"Text: {chunk.text[:100]}...")
```

### Context Manager Pattern

```python
# All serializers support context managers for resource management
with XlsxSerializer() as serializer:
    serializer.configure_memory_limit(max_mem_mb=256)
    serializer.configure_logging(enable_performance_logging=True)

    # Process multiple files with consistent configuration
    for file_path in ["data1.xlsx", "data2.xlsx"]:
        for chunk in serializer.iterate_chunks(file_path):
            # Process chunk
            process_chunk(chunk)

# Automatic cleanup on context exit
# Logs performance statistics
# Resets configuration to defaults
```

### Memory-Efficient Iterator Pattern

```python
# For large documents, use iterator pattern
serializer = DocxSerializer()
chunk_count = 0
for chunk in serializer.iterate_chunks("large_document.docx"):
    chunk_count += 1
    # Process chunk immediately without loading all into memory
    process_chunk(chunk)

    # Optional: limit processing
    if chunk_count >= 1000:
        break

print(f"Processed {chunk_count} chunks efficiently")
```

### Command Line

```bash
# Basic usage
python -m docpipe serialize document.pdf > output.jsonl

# Advanced options
python -m docpipe serialize document.docx \
    --memory-limit 512 \
    --enable-logging \
    --log-level DEBUG \
    --output formatted.jsonl

# Excel with header injection
python -m docpipe serialize data.xlsx \
    --header-row 1 \
    --rag-format

# List supported formats
python -m docpipe formats

# Show system information
python -m docpipe info
```

## ✨ Key Features

### 🔧 Protocol-Oriented Architecture
- **Mixin Design**: LoggingMixin, SerializerMixin for composable functionality
- **Type Safety**: Runtime checkable protocols with mypy strict compliance
- **Extensibility**: Easy to add new serializers via protocol implementation
- **Zero Dependencies**: Core functionality uses only Python standard library

### 📝 Advanced Excel Processing
- **Header Injection**: Automatic or custom header support
  ```python
  # Use first row as headers
  serializer.configure_header_injection(header_row=1)

  # Or provide custom headers
  custom_headers = ["Name", "Age", "Department"]
  serializer.configure_header_injection(custom_headers=custom_headers)
  ```
- **Cell-Level Processing**: Individual cell extraction with coordinates
- **Table Structure**: Maintain spreadsheet structure in output
- **Embedded Images**: Extract images from worksheets
- **Chart Detection**: Identify and describe Excel charts
- **RAG Format**: Optimized output for Retrieval-Augmented Generation

### 📄 Word Document Processing
- **Correct Content Ordering**: Images appear in document reading order (not at end)
- **Mixed Content**: Handle text and images in their natural sequence
- **Coordinate Estimation**: Smart positioning based on document structure
- **Format Preservation**: Detect bold, italic, and other formatting
- **Image Extraction**: Base64 encoding with format detection

### 📊 PDF Processing
- **Text Extraction**: Accurate text with coordinates
- **Table Recognition**: Automatic table detection and extraction
- **Image Support**: Extract images with position data
- **Memory Safe**: Proper resource management for large files

### 🗂️ Enterprise Logging
- **Structured Logging**: Comprehensive logging with performance metrics
- **Timing Information**: Operation timing with context data
- **Progress Tracking**: Real-time processing progress
- **Error Handling**: Detailed error reporting with context
- **Performance Analytics**: Built-in performance monitoring

### 🎛️ Rich Configuration
```python
serializer = XlsxSerializer()

# Configure multiple aspects with method chaining
serializer.configure_memory_limit(max_mem_mb=512)\
          .configure_logging(enable_performance_logging=True, log_level="INFO")\
          .configure_header_injection(header_row=1)\
          .configure_rag_format(enable_backward_compatible=True)

# Use with context manager for automatic cleanup
with serializer:
    for chunk in serializer.iterate_chunks("data.xlsx"):
        print(chunk.to_dict())
```

## 📊 Output Format

Each chunk is a DocumentChunk object:

```python
@dataclass
class DocumentChunk:
    doc_id: str                    # Document identifier
    page: int                      # Page number (1-based)
    x: float                       # Normalized X coordinate (0-1)
    y: float                       # Normalized Y coordinate (0-1)
    w: float                       # Normalized width (0-1)
    h: float                       # Normalized height (0-1)
    type: str                      # Content type: "text" | "table" | "image"
    text: Optional[str]            # Text content
    tokens: Optional[int]          # Estimated token count
    binary_data: Optional[str]     # Base64 encoded image data
    metadata: Dict[str, Any]       # Additional metadata
```

### JSONL Output

```json
{
  "doc_id": "uuid",
  "page": 1,
  "x": 0.123,
  "y": 0.456,
  "w": 0.7,
  "h": 0.08,
  "type": "text",
  "text": "Sample content...",
  "tokens": 42,
  "binary_data": null,
  "metadata": {
    "source_file": "document.docx",
    "serializer": "DocxSerializer",
    "extraction_method": "docx_stdlib_ordered",
    "paragraph_index": 15,
    "has_formatting": true,
    "font_sizes": [12, 14],
    "processing_time": 0.045
  }
}
```

## 📦 Installation

### Core Installation (5 MB)
```bash
pip install docpipe
```
Zero third-party dependencies for core functionality.

### Optional Formats

```bash
# PDF support with PyMuPDF (AGPL, recommended, +11 MB)
pip install docpipe[pdf]

# Development tools
pip install docpipe[dev]
```

### Development
```bash
git clone https://github.com/docpipe/docpipe
cd docpipe
uv sync --extra dev
pytest
mypy --strict
```

## 🏗️ Architecture

### Protocol-Oriented Design

```
Protocols (Interfaces) ← Mixins (Implementations) ← Serializers (Concrete Classes)
```

1. **Protocols** (`_protocols.py`):
   - `DocumentSerializer`: Core serialization interface
   - `LoggingMixinProto`: Structured logging interface
   - `SerializerMixinProto`: Configuration and context management

2. **Mixins** (Default implementations):
   - `LoggingMixin`: Performance logging, timing, error tracking
   - `SerializerMixin`: Memory limits, context management, configuration

3. **Serializers** (Concrete implementations):
   - `DocxSerializer`: Word document processing
   - `XlsxSerializer`: Excel spreadsheet processing
   - `PdfiumSerializer`: PDF document processing

### Data Flow

```
Document File → Serializer → DocumentChunk(s) → JSONL/Objects
     ↓              ↓              ↓
   File I/O    Protocol API   Structured Output
```

## 📋 Supported Formats

| Format | Status | Library | License | Features |
|--------|--------|---------|---------|----------|
| PDF | ✅ | pypdfium2 | BSD | Text, images, tables with coordinates |
| DOCX | ✅ | Standard Library | MIT | Text, images, formatting, correct ordering |
| XLSX | ✅ | Standard Library | MIT | Cells, tables, headers, charts, images |

## 🔧 Advanced Configuration

### Excel Header Injection

```python
# Method 1: Use first row as headers
excel = XlsxSerializer()
excel.configure_header_injection(header_row=1)

# Method 2: Custom headers
custom_headers = ["Product", "Price", "Quantity", "Category"]
excel.configure_header_injection(custom_headers=custom_headers)

# Method 3: Per-file configuration
with excel.configure_header_injection(header_row=1) as configured:
    for chunk in configured.iterate_chunks("sales_data.xlsx"):
        # Headers are automatically injected into metadata
        print(f"Headers: {chunk.metadata.get('headers', [])}")
        print(f"Data: {chunk.text}")
```

### Memory Management

```python
# Set memory limits
serializer = DocxSerializer()
serializer.configure_memory_limit(max_mem_mb=256)

# Iterator pattern for large files
for chunk in serializer.iterate_chunks("large_file.docx"):
    # Process chunk immediately
    process_chunk(chunk)
    # Memory usage stays low
```

### Logging Configuration

```python
# Enable detailed logging
serializer = XlsxSerializer()
serializer.configure_logging(
    enable_performance_logging=True,
    log_level="DEBUG"
)

# Logs include:
# - Operation timing
# - Memory usage
# - Processing progress
# - Error context
# - Performance metrics
```

### Context Manager Usage

```python
# Automatic resource management
with XlsxSerializer() as serializer:
    serializer.configure_memory_limit(max_mem_mb=512)
    serializer.configure_logging(enable_performance_logging=True)

    # Process multiple files
    for file_path in ["file1.xlsx", "file2.xlsx"]:
        for chunk in serializer.iterate_chunks(file_path):
            process_chunk(chunk)

# Automatic cleanup on exit:
# - Reset configuration
# - Close file handles
# - Log performance summary
# - Clean up resources
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific serializer tests
pytest tests/test_docx.py
pytest tests/test_xlsx.py
pytest tests/test_pdf.py

# Type checking
mypy --strict

# Performance benchmarks
pytest -m benchmark
```

## 📈 Performance

- **Installation**: 5 MB core, zero dependencies
- **Processing**: ~300ms/MB for typical documents
- **Memory**: Configurable limits, iterator pattern for large files
- **Output**: Clean, coordinate-aware chunks optimized for AI

## 🎯 Design Goals

- **Protocol-First**: Composable architecture via protocols and mixins
- **Zero Dependencies**: Core functionality uses only Python standard library
- **Memory Safe**: Built-in memory limits and iterator pattern
- **Enterprise Ready**: Comprehensive logging and error handling
- **AI-Optimized**: Coordinate-aware output for LLM consumption
- **Correct Ordering**: Content appears in natural reading order
- **Type Safe**: Full type hints and mypy strict compliance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure `mypy --strict` passes
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](https://docpipe.readthedocs.io)
- [Repository](https://github.com/docpipe/docpipe)
- [Issues](https://github.com/docpipe/docpipe/issues)

---

**docpipe** - Protocol-oriented document serialization for AI applications.