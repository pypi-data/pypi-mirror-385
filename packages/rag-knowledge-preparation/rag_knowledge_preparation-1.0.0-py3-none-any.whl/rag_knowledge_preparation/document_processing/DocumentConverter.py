from pathlib import Path
from typing import Union, Dict, Any

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from .DocumentProcessingConfig import ProcessingConfig, get_config, create_pipeline_options
from ..utils.CustomExceptions import (
    DocumentNotFoundError, 
    ConfigurationError, 
    ConversionError
)


def convert_document_to_markdown(
    document_path: Union[str, Path],
    processing_preset: str = "standard",
    **preset_overrides: Any
) -> str:
    """
    Convert a document to Markdown format for RAG knowledge preparation.
    Supports OCR for scanned documents and advanced table processing.
    
    Args:
        document_path: Path to the document file (PDF, DOCX, etc.)
        processing_preset: Processing configuration preset - "basic", "standard", 
                          "ocr_heavy", "table_focused", or "high_quality"
        **preset_overrides: Additional configuration options to override preset
        
    Returns:
        Markdown content of the document
        
    Raises:
        DocumentNotFoundError: If the document file doesn't exist
        ConfigurationError: If configuration is invalid
        ConversionError: If document conversion fails
    """
    document_path = Path(document_path)
    if not document_path.exists():
        raise DocumentNotFoundError(f"Document not found: {document_path}")
    
    try:
        processing_config = _get_customized_config(processing_preset, preset_overrides)
    except ValueError as e:
        raise ConfigurationError(f"Invalid configuration: {e}") from e
    
    document_converter = _create_configured_converter(processing_config)
    
    try:
        conversion_result = document_converter.convert(str(document_path))
        return conversion_result.document.export_to_markdown()
    except Exception as e:
        raise ConversionError(f"Failed to convert document: {e}") from e


def _get_customized_config(preset_name: str, overrides: Dict[str, Any]) -> ProcessingConfig:
    """Get configuration with custom overrides applied."""
    try:
        base_config = get_config(preset_name)
    except ValueError as e:
        raise ValueError(f"Invalid preset name: {e}") from e
    
    if overrides:
        for option_name in overrides.keys():
            if not hasattr(base_config, option_name):
                raise ValueError(f"Unknown configuration option: {option_name}")
        
        config_dict = {
            'enable_ocr': base_config.enable_ocr,
            'table_processing': base_config.table_processing,
            'ocr_engine': base_config.ocr_engine,
            'ocr_language': base_config.ocr_language,
            'table_confidence_threshold': base_config.table_confidence_threshold,
            'enable_cell_matching': base_config.enable_cell_matching,
            'enable_table_structure': base_config.enable_table_structure,
        }
        
        config_dict.update(overrides)
        return ProcessingConfig(**config_dict)
    
    return base_config


def _create_configured_converter(processing_config: ProcessingConfig) -> DocumentConverter:
    """Create a DocumentConverter with the given configuration."""
    if processing_config.enable_ocr or processing_config.enable_table_structure:
        pipeline_options = create_pipeline_options(processing_config)
        return DocumentConverter(
            format_options={
                InputFormat.PDF: pipeline_options,
            }
        )
    return DocumentConverter()


def convert_scanned_document_to_markdown(
    document_path: Union[str, Path], 
    ocr_engine: str = "easyocr"
) -> str:
    """
    Convert a scanned document to Markdown using OCR processing.
    
    Args:
        document_path: Path to the scanned document file
        ocr_engine: OCR engine to use ("easyocr", "tesseract")
        
    Returns:
        Markdown content with OCR-processed text
    """
    return convert_document_to_markdown(
        document_path=document_path,
        processing_preset="ocr_heavy",
        ocr_engine=ocr_engine
    )


def convert_document_with_table_processing(document_path: Union[str, Path]) -> str:
    """
    Convert a document with advanced table processing using TableFormer.
    
    Args:
        document_path: Path to the document file
        
    Returns:
        Markdown content with properly formatted tables
    """
    return convert_document_to_markdown(
        document_path=document_path,
        processing_preset="table_focused"
    )


def convert_document_with_maximum_quality(document_path: Union[str, Path]) -> str:
    """
    Convert a document with maximum quality processing (OCR + TableFormer).
    
    Args:
        document_path: Path to the document file
        
    Returns:
        Markdown content with maximum quality processing
    """
    return convert_document_to_markdown(
        document_path=document_path,
        processing_preset="high_quality"
    )


def convert_documents_batch(
    document_paths: Union[list, tuple, str, Path],
    processing_preset: str = "standard",
    **preset_overrides: Any
) -> Dict[str, str]:
    """
    Convert multiple documents to Markdown format in batch.
    
    Args:
        document_paths: List of document paths, or a directory path to process all supported files
        processing_preset: Processing configuration preset
        **preset_overrides: Additional configuration options to override preset
        
    Returns:
        Dictionary mapping file paths to their Markdown content
        
    Raises:
        DocumentNotFoundError: If any document file doesn't exist
        ConfigurationError: If configuration is invalid
        ConversionError: If document conversion fails
    """
    if isinstance(document_paths, (str, Path)):
        document_paths = Path(document_paths)
        if document_paths.is_dir():
            document_paths = _find_supported_documents(document_paths)
        else:
            document_paths = [document_paths]
    
    for doc_path in document_paths:
        doc_path = Path(doc_path)
        if not doc_path.exists():
            raise DocumentNotFoundError(f"Document not found: {doc_path}")
    
    try:
        processing_config = _get_customized_config(processing_preset, preset_overrides)
    except ValueError as e:
        raise ConfigurationError(f"Invalid configuration: {e}") from e
    
    document_converter = _create_configured_converter(processing_config)
    
    results = {}
    try:
        conversion_results = list(document_converter.convert_all(document_paths))
        
        for i, result in enumerate(conversion_results):
            doc_path = Path(document_paths[i])
            markdown_content = result.document.export_to_markdown()
            results[str(doc_path)] = markdown_content
            
    except Exception as e:
        raise ConversionError(f"Failed to convert documents in batch: {e}") from e
    
    return results


def convert_folder_to_markdown(
    folder_path: Union[str, Path],
    processing_preset: str = "standard",
    **preset_overrides: Any
) -> Dict[str, str]:
    """
    Convert all supported documents in a folder to Markdown format.
    
    Args:
        folder_path: Path to the folder containing documents
        processing_preset: Processing configuration preset
        **preset_overrides: Additional configuration options to override preset
        
    Returns:
        Dictionary mapping file paths to their Markdown content
        
    Raises:
        DocumentNotFoundError: If the folder doesn't exist
        ConfigurationError: If configuration is invalid
        ConversionError: If document conversion fails
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise DocumentNotFoundError(f"Folder not found: {folder_path}")
    
    if not folder_path.is_dir():
        raise DocumentNotFoundError(f"Path is not a directory: {folder_path}")
    
    return convert_documents_batch(
        document_paths=folder_path,
        processing_preset=processing_preset,
        **preset_overrides
    )


def _find_supported_documents(folder_path: Path) -> list[Path]:
    """
    Find all supported document files in a folder.
    
    Args:
        folder_path: Path to the folder to search
        
    Returns:
        List of supported document file paths
    """
    supported_extensions = set()
    for fmt in InputFormat:
        if fmt.value:
            supported_extensions.add(f".{fmt.value}")
    
    supported_files = []
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            supported_files.append(file_path)
    
    return sorted(supported_files)
