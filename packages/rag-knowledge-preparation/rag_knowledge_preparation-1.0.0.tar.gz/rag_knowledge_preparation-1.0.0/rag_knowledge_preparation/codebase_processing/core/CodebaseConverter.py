from pathlib import Path
from typing import Union, Dict, Any, Optional

from .CodebaseConfig import CodebaseProcessingConfig, get_codebase_config
from ..export.CodebaseExporter import export_to_markdown, analyze_structure, get_overview
from ...utils.CustomExceptions import (
    DocumentNotFoundError,
    ConfigurationError,
    ConversionError
)


def _validate_and_get_config(target_path: Union[str, Path], processing_preset: str, **preset_overrides: Any) -> tuple[Path, CodebaseProcessingConfig]:
    target_path = Path(target_path)
    if not target_path.exists():
        raise DocumentNotFoundError(f"Target path not found: {target_path}")
    
    try:
        config = _get_customized_config(processing_preset, preset_overrides)
    except ValueError as e:
        raise ConfigurationError(f"Invalid configuration: {e}") from e
    
    return target_path, config


def _get_customized_config(preset_name: str, overrides: Dict[str, Any]) -> CodebaseProcessingConfig:
    try:
        base_config = get_codebase_config(preset_name)
    except ValueError as e:
        raise ValueError(f"Invalid preset name: {e}") from e
    
    if overrides:
        config_dict = base_config.model_dump()
        config_dict.update(overrides)
        return CodebaseProcessingConfig.model_validate(config_dict)
    
    return base_config


def export_codebase_to_markdown(
    target_path: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    processing_preset: str = "standard",
    gemini_api_key: Optional[str] = None,
    gemini_model: Optional[str] = None,
    **preset_overrides: Any
) -> str:
    target_path, config = _validate_and_get_config(target_path, processing_preset, **preset_overrides)
    
    if gemini_api_key:
        config.gemini_api_key = gemini_api_key
        config.enable_ai_summary = True
    if gemini_model:
        config.gemini_model = gemini_model
    
    if output_file is None:
        output_file = f"{target_path.name}_codebase_export.md"
    else:
        output_file = Path(output_file)
    
    try:
        export_to_markdown(target_path, output_file, config)
        return str(output_file)
    except Exception as e:
        raise ConversionError(f"Failed to export codebase to Markdown: {e}") from e


def analyze_codebase_structure(
    target_path: Union[str, Path],
    processing_preset: str = "standard",
    **preset_overrides: Any
) -> Dict[str, Any]:
    target_path, config = _validate_and_get_config(target_path, processing_preset, **preset_overrides)
    return analyze_structure(target_path, config)


def get_codebase_overview(
    target_path: Union[str, Path],
    processing_preset: str = "standard",
    **preset_overrides: Any
) -> Dict[str, Any]:
    target_path, config = _validate_and_get_config(target_path, processing_preset, **preset_overrides)
    return get_overview(target_path, config)