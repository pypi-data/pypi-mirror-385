# RAG Knowledge Preparation Python

A comprehensive Python library for preparing knowledge bases for Retrieval-Augmented Generation (RAG) systems. This library provides powerful tools for document processing with OCR capabilities, advanced table processing, and intelligent codebase analysis.

## Features

### Document Processing Features

- **Multi-format Support**: Convert PDF, DOCX, HTML, CSV, and other formats to Markdown
- **OCR Integration**: Extract text from scanned documents using EasyOCR or Tesseract
- **Advanced Table Processing**: Intelligent table detection and conversion using TableFormer
- **Batch Processing**: Process multiple documents or entire folders efficiently
- **Configurable Quality**: Multiple processing presets for different use cases

### Codebase Analysis Features

- **Comprehensive Analysis**: Extract structure, dependencies, and metadata from codebases
- **Multi-language Support**: Python, JavaScript, TypeScript and more
- **AI-Powered Summaries**: Generate intelligent code summaries using Google Gemini
- **Dependency Analysis**: Identify and categorize internal, external, and standard library dependencies
- **Structure Extraction**: Parse classes, functions, imports, and code organization
- **Token Estimation**: Accurate token counting for RAG optimization

### Configuration & Customization

- **Flexible Configuration**: Extensive configuration options for both document and codebase processing
- **Preset Configurations**: Pre-built configurations for common use cases
- **Custom Metadata**: Configurable metadata fields for different analysis needs
- **Performance Optimization**: Built-in performance modes for large-scale processing

## Installation

```bash
pip install rag-knowledge-preparation-python
```

### Development Installation

```bash
git clone 
cd rag-knowledge-preparation-python
pip install -e ".[dev]"
```

## Quick Start

### Document Processing

```python
from rag_knowledge_preparation import (
    convert_document_to_markdown,
    convert_scanned_document_to_markdown,
    convert_documents_batch
)

# Convert a single document
markdown_content = convert_document_to_markdown("document.pdf")

# Convert a scanned document with OCR
scanned_content = convert_scanned_document_to_markdown("scanned_document.pdf")

# Process multiple documents
results = convert_documents_batch(["doc1.pdf", "doc2.docx", "doc3.html"])
```

### Codebase Analysis

```python
from rag_knowledge_preparation import (
    export_codebase_to_markdown,
    analyze_codebase_structure,
    get_codebase_overview
)

# Export entire codebase to Markdown
output_file = export_codebase_to_markdown("./my_project", "codebase_export.md")

# Analyze codebase structure
structure = analyze_codebase_structure("./my_project")

# Get high-level overview
overview = get_codebase_overview("./my_project")
```

## Document Processing Details

### Supported Formats

- **PDF**: Native PDF processing with OCR support
- **Microsoft Office**: DOCX, DOC, PPTX, PPT
- **Web Formats**: HTML, XML
- **Data Formats**: CSV, TSV, JSON
- **Text Formats**: TXT, MD, RST

### Processing Presets

#### Basic Processing

```python
from rag_knowledge_preparation import convert_document_to_markdown

# Basic processing without OCR
content = convert_document_to_markdown(
    "document.pdf", 
    processing_preset="basic"
)
```

#### Standard Document Processing

```python
# Standard processing with OCR and advanced tables
content = convert_document_to_markdown(
    "document.pdf", 
    processing_preset="standard"
)
```

#### OCR-Heavy Processing

```python
# Heavy OCR processing for scanned documents
content = convert_document_to_markdown(
    "scanned_document.pdf", 
    processing_preset="ocr_heavy"
)
```

#### Table-Focused Processing

```python
# Optimized for documents with complex tables
content = convert_document_to_markdown(
    "data_heavy_document.pdf", 
    processing_preset="table_focused"
)
```

#### High-Quality Processing

```python
# Maximum quality with all features enabled
content = convert_document_to_markdown(
    "important_document.pdf", 
    processing_preset="high_quality"
)
```

### Custom Configuration

```python
from rag_knowledge_preparation import convert_document_to_markdown

# Custom configuration
content = convert_document_to_markdown(
    "document.pdf",
    processing_preset="standard",
    ocr_engine="tesseract",
    ocr_language="en",
    table_confidence_threshold=0.9,
    enable_cell_matching=True
)
```

### Batch Processing

```python
from rag_knowledge_preparation import convert_documents_batch, convert_folder_to_markdown

# Process multiple files
results = convert_documents_batch([
    "document1.pdf",
    "document2.docx", 
    "document3.html"
])

# Process entire folder
folder_results = convert_folder_to_markdown("./documents/")
```

## Codebase Analysis Usage

### Basic Analysis

```python
from rag_knowledge_preparation import analyze_codebase_structure

# Analyze codebase structure
structure = analyze_codebase_structure("./my_project")

print(f"Total files: {structure['total_files']}")
print(f"Total lines: {structure['total_lines']}")
print(f"Languages: {structure['languages']}")
```

### Export to Markdown

```python
from rag_knowledge_preparation import export_codebase_to_markdown

# Export with default settings
output_file = export_codebase_to_markdown("./my_project")

# Export with custom output file
output_file = export_codebase_to_markdown(
    "./my_project", 
    output_file="my_codebase.md"
)
```

### AI-Powered Analysis

```python
from rag_knowledge_preparation import export_codebase_to_markdown

# Export with AI summaries (requires Gemini API key)
output_file = export_codebase_to_markdown(
    "./my_project",
    gemini_api_key="your-gemini-api-key",
    gemini_model="gemini-pro"
)
```

### Codebase Processing Presets

#### Minimal Processing

```python
from rag_knowledge_preparation import export_codebase_to_markdown

# Minimal processing - basic analysis only
output_file = export_codebase_to_markdown(
    "./my_project", 
    processing_preset="minimal"
)
```

#### Standard Processing

```python
# Standard processing with full analysis
output_file = export_codebase_to_markdown(
    "./my_project", 
    processing_preset="standard"
)
```

#### Comprehensive Processing

```python
# Comprehensive processing with all features
output_file = export_codebase_to_markdown(
    "./my_project", 
    processing_preset="comprehensive"
)
```

### Configuration Options

```python
from rag_knowledge_preparation import (
    CodebaseProcessingConfig,
    MetadataConfig,
    export_codebase_to_markdown
)

# Custom configuration
config = CodebaseProcessingConfig(
    max_file_size_mb=2.0,
    include_test_files=False,
    include_documentation=True,
    enable_ai_summary=True,
    gemini_api_key="your-api-key",
    custom_ignore_patterns=["*.log", "temp/*"]
)

# Custom metadata configuration
metadata_config = MetadataConfig(
    include_file_path=True,
    include_language=True,
    include_purpose=True,
    include_dependencies=True,
    include_structure=True,
    include_summary=True
)

config.metadata_config = metadata_config

# Use custom configuration
output_file = export_codebase_to_markdown(
    "./my_project",
    processing_preset="custom",
    **config.model_dump()
)
```

## Advanced Features

### Language Detection and Classification

The library automatically detects programming languages and classifies files by purpose:

```python
from rag_knowledge_preparation.codebase_processing.analysis import (
    get_language_from_extension,
    classify_file_by_purpose
)

# Detect language from file extension
language = get_language_from_extension("script.py")  # Returns "python"

# Classify file by purpose
purpose = classify_file_by_purpose("test_utils.py")  # Returns "Tests"
```

### Dependency Analysis

```python
from pathlib import Path
from rag_knowledge_preparation.codebase_processing.analysis import analyze_file_dependencies

# Analyze dependencies in a Python file
with open("main.py", "r") as f:
    content = f.read()
dependencies = analyze_file_dependencies(content, Path("main.py"), "python")

print("External packages:", dependencies["external_packages"])
print("Standard library:", dependencies["standard_library"])
print("Internal modules:", dependencies["internal_modules"])
```

### Code Structure Extraction

```python
from pathlib import Path
from rag_knowledge_preparation.codebase_processing.analysis import extract_code_structure

# Extract structure from code file
code_content = """
class MyClass:
    def __init__(self):
        pass
    
    def method(self):
        pass
"""
structure = extract_code_structure(Path("example.py"), "python", code_content)

print("Classes:", structure["classes"])
print("Functions:", structure["functions"])
```

### Token Estimation

```python
from rag_knowledge_preparation.codebase_processing.analysis import estimate_token_count

# Estimate tokens in text
token_count = estimate_token_count("Hello, world!")
print(f"Estimated tokens: {token_count}")

# Estimate tokens in code
code_tokens = estimate_token_count("""
def hello():
    print("Hello, world!")
""")
```

## Configuration Reference

### Document Processing Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_ocr` | bool | True | Enable OCR processing |
| `table_processing` | str | "advanced" | Table processing mode (basic, advanced, tableformer) |
| `ocr_engine` | str | "easyocr" | OCR engine (easyocr, tesseract) |
| `ocr_language` | str | "en" | OCR language (en, fr, de, es) |
| `table_confidence_threshold` | float | 0.8 | Table detection confidence threshold |
| `enable_cell_matching` | bool | True | Enable cell matching in tables |
| `enable_table_structure` | bool | True | Enable table structure analysis |

### Codebase Processing Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_file_size_mb` | float | 1.0 | Maximum file size to process |
| `include_hidden_files` | bool | False | Include hidden files |
| `include_test_files` | bool | True | Include test files |
| `include_documentation` | bool | True | Include documentation files |
| `include_config_files` | bool | True | Include configuration files |
| `enable_structure_analysis` | bool | True | Enable code structure analysis |
| `enable_ai_summary` | bool | True | Enable AI-powered summaries |
| `gemini_api_key` | str | None | Google Gemini API key |
| `gemini_model` | str | "gemini-pro" | Gemini model to use |
| `custom_ignore_patterns` | List[str] | None | Custom ignore patterns |

## Error Handling

The library provides comprehensive error handling with custom exceptions:

```python
from rag_knowledge_preparation import (
    RAGKnowledgePreparationError,
    DocumentNotFoundError,
    ConfigurationError,
    ConversionError,
    UnsupportedFormatError
)

try:
    content = convert_document_to_markdown("nonexistent.pdf")
except DocumentNotFoundError as e:
    print(f"Document not found: {e}")
except ConversionError as e:
    print(f"Conversion failed: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Performance Considerations

### Large File Processing

The library includes built-in optimizations for large files:

- **File Size Limits**: Configurable maximum file size limits
- **Memory Efficiency**: Streaming processing for large documents
- **Batch Processing**: Efficient processing of multiple files
- **Parallel Processing**: Concurrent processing where possible

### Performance Modes

```python
# Use performance-optimized settings
config = CodebaseProcessingConfig(
    max_file_size_mb=0.5,  # Smaller file limit
    enable_ai_summary=False,  # Disable AI for speed
    enable_structure_analysis=False  # Disable structure analysis
)
```

## Examples

### Complete Document Processing Pipeline

```python
from rag_knowledge_preparation import (
    convert_folder_to_markdown,
    list_document_configs
)

# List available configurations
configs = list_document_configs()
print("Available configurations:", list(configs.keys()))

# Process entire document folder
results = convert_folder_to_markdown(
    "./documents/",
    processing_preset="high_quality"
)

# Save results
for file_path, content in results.items():
    output_path = f"processed_{file_path.split('/')[-1]}.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
```

### Complete Codebase Analysis Pipeline

```python
from rag_knowledge_preparation import (
    export_codebase_to_markdown,
    analyze_codebase_structure,
    get_codebase_overview,
    list_available_codebase_configs
)

# List available configurations
configs = list_available_codebase_configs()
print("Available configurations:", list(configs.keys()))

# Get overview
overview = get_codebase_overview("./my_project")
print(f"Project: {overview['name']}")
print(f"Files: {overview['total_files']}")
print(f"Languages: {overview['languages']}")

# Analyze structure
structure = analyze_codebase_structure("./my_project")
print(f"Structure analysis complete: {structure['total_files']} files processed")

# Export to Markdown
output_file = export_codebase_to_markdown(
    "./my_project",
    output_file="project_analysis.md",
    gemini_api_key="your-api-key"
)
print(f"Exported to: {output_file}")
```

## Acknowledgments

- [Docling](https://github.com/DS4SD/docling) for document processing capabilities
- [Tree-sitter](https://tree-sitter.github.io/) for code parsing
- [Google Gemini](https://ai.google.dev/) for AI-powered summarization
- [Pygments](https://pygments.org/) for syntax highlighting and language detection

## Changelog

### Version 1.0.0

- Initial release
- Document processing with OCR support
- Codebase analysis and export
- AI-powered summarization
- Comprehensive configuration options
- Multi-language support
