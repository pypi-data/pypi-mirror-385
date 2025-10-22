from dataclasses import dataclass
from typing import Dict, Literal
from docling.datamodel.pipeline_options import PdfPipelineOptions


TableProcessingMode = Literal["basic", "advanced", "tableformer"]
OCREngine = Literal["easyocr", "tesseract"]
OCRLanguage = Literal["en", "fr", "de", "es"]


@dataclass(frozen=True)
class ProcessingConfig:
    """Configuration for document processing."""
    enable_ocr: bool = True
    table_processing: TableProcessingMode = "advanced"
    ocr_engine: OCREngine = "easyocr"
    ocr_language: OCRLanguage = "en"
    table_confidence_threshold: float = 0.8
    enable_cell_matching: bool = True
    enable_table_structure: bool = True
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.table_confidence_threshold <= 1.0:
            raise ValueError("table_confidence_threshold must be between 0.0 and 1.0")


CONFIGS = {
    "basic": ProcessingConfig(
        enable_ocr=False,
        table_processing="basic",
        enable_table_structure=False,
        enable_cell_matching=False
    ),
    
    "standard": ProcessingConfig(
        enable_ocr=True,
        table_processing="advanced",
        ocr_engine="easyocr",
        ocr_language="en"
    ),
    
    "ocr_heavy": ProcessingConfig(
        enable_ocr=True,
        table_processing="advanced",
        ocr_engine="tesseract",
        ocr_language="en",
        table_confidence_threshold=0.9
    ),
    
    "table_focused": ProcessingConfig(
        enable_ocr=True,
        table_processing="tableformer",
        ocr_engine="easyocr",
        ocr_language="en",
        table_confidence_threshold=0.8,
        enable_cell_matching=True
    ),
    
    "high_quality": ProcessingConfig(
        enable_ocr=True,
        table_processing="tableformer",
        ocr_engine="easyocr",
        ocr_language="en",
        table_confidence_threshold=0.9,
        enable_cell_matching=True
    )
}


def get_config(config_name: str = "standard") -> ProcessingConfig:
    """
    Get a predefined processing configuration.
    
    Args:
        config_name: Name of the configuration preset
        
    Returns:
        Configuration object
        
    Raises:
        ValueError: If config_name is not found
    """
    if config_name not in CONFIGS:
        available_configs = ", ".join(CONFIGS.keys())
        raise ValueError(f"Unknown config '{config_name}'. Available configs: {available_configs}")
    
    return CONFIGS[config_name]


def create_pipeline_options(config: ProcessingConfig) -> PdfPipelineOptions:
    """
    Create PdfPipelineOptions from ProcessingConfig.
    
    Args:
        config: Processing configuration
        
    Returns:
        Configured pipeline options
    """
    pipeline_options = PdfPipelineOptions()
    
    pipeline_options.do_ocr = config.enable_ocr
    if config.enable_ocr:
        pipeline_options.ocr_options.lang = [config.ocr_language]
    
    pipeline_options.do_table_structure = config.enable_table_structure
    if config.enable_table_structure:
        pipeline_options.table_structure_options.do_cell_matching = config.enable_cell_matching
    
    return pipeline_options


def list_available_configs() -> Dict[str, str]:
    """
    List all available configuration presets with descriptions.
    
    Returns:
        Configuration names and descriptions
    """
    return {
        "basic": "Basic processing without OCR or advanced table handling",
        "standard": "Standard processing with OCR and advanced tables",
        "ocr_heavy": "Heavy OCR processing for scanned documents",
        "table_focused": "Optimized for documents with complex tables",
        "high_quality": "Highest quality processing with all features enabled"
    }
