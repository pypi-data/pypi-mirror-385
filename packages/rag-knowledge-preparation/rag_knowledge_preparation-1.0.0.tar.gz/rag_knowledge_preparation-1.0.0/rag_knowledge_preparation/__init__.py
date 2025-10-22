# Document processing
from .document_processing import (
    convert_document_to_markdown,
    convert_scanned_document_to_markdown,
    convert_document_with_table_processing,
    convert_document_with_maximum_quality,
    convert_documents_batch,
    convert_folder_to_markdown,
    ProcessingConfig as DocumentProcessingConfig,
    get_config as get_document_config,
    create_pipeline_options,
    list_available_configs as list_document_configs,
)

# Codebase processing
from .codebase_processing import (
    export_codebase_to_markdown,
    analyze_codebase_structure,
    get_codebase_overview,
    CodebaseProcessingConfig,
    get_codebase_config,
    list_available_codebase_configs,
)

from .utils.CustomExceptions import (
    RAGKnowledgePreparationError,
    DocumentNotFoundError,
    ConfigurationError,
    ConversionError,
    UnsupportedFormatError
)

__version__ = "1.0.0"
__all__ = [
    # Document conversion functions
    "convert_document_to_markdown",
    "convert_scanned_document_to_markdown",
    "convert_document_with_table_processing",
    "convert_document_with_maximum_quality",
    "convert_documents_batch",
    "convert_folder_to_markdown",
    
    # Document configuration
    "DocumentProcessingConfig",
    "get_document_config",
    "create_pipeline_options",
    "list_document_configs",
    
    # Codebase processing functions
    "export_codebase_to_markdown",
    "analyze_codebase_structure",
    "get_codebase_overview",
    
    # Codebase configuration
    "CodebaseProcessingConfig",
    "get_codebase_config",
    "list_available_codebase_configs",
    
    # Exceptions
    "RAGKnowledgePreparationError",
    "DocumentNotFoundError",
    "ConfigurationError",
    "ConversionError",
    "UnsupportedFormatError"
]
