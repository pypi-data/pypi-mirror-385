from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class MetadataConfig(BaseModel):
    include_file_path: bool = Field(default=True, description="Include relative file path")
    include_language: bool = Field(default=True, description="Include programming language")
    include_purpose: bool = Field(default=True, description="Include file purpose classification")
    include_file_size: bool = Field(default=True, description="Include file size in characters")
    include_line_count: bool = Field(default=True, description="Include line count")
    include_token_count: bool = Field(default=True, description="Include estimated token count")
    include_summary: bool = Field(default=True, description="Include AI or fallback summary")
    include_dependencies: bool = Field(default=True, description="Include dependency analysis")
    include_structure: bool = Field(default=True, description="Include code structure (classes, functions, etc.)")
    include_creation_date: bool = Field(default=False, description="Include file creation date")
    include_modification_date: bool = Field(default=False, description="Include file modification date")
    include_encoding: bool = Field(default=False, description="Include file encoding")
    include_git_info: bool = Field(default=False, description="Include git information (last commit, author)")
    
    def get_enabled_fields(self) -> Set[str]:
        enabled = set()
        for field_name, field_value in self.model_dump().items():
            if field_value:
                enabled.add(field_name)
        return enabled


class CodebaseProcessingConfig(BaseModel):
    max_file_size_mb: float = Field(default=1.0, gt=0)
    include_hidden_files: bool = Field(default=False)
    include_test_files: bool = Field(default=True)
    include_documentation: bool = Field(default=True)
    include_config_files: bool = Field(default=True)
    enable_structure_analysis: bool = Field(default=True)
    enable_ai_summary: bool = Field(default=True)
    gemini_api_key: Optional[str] = Field(default=None)
    gemini_model: str = Field(default="gemini-pro")
    custom_ignore_patterns: Optional[List[str]] = Field(default=None)
    metadata_config: Optional[MetadataConfig] = Field(default=None, description="Custom metadata fields configuration")


# Predefined metadata configurations
METADATA_PRESETS = {
    "minimal": MetadataConfig(
        include_file_path=True,
        include_language=True,
        include_purpose=False,
        include_file_size=False,
        include_line_count=False,
        include_token_count=False,
        include_summary=False,
        include_dependencies=False,
        include_structure=False,
        include_creation_date=False,
        include_modification_date=False,
        include_encoding=False,
        include_git_info=False,
    ),
    
    "standard": MetadataConfig(),  # All default fields enabled
    
    "comprehensive": MetadataConfig(
        include_file_path=True,
        include_language=True,
        include_purpose=True,
        include_file_size=True,
        include_line_count=True,
        include_token_count=True,
        include_summary=True,
        include_dependencies=True,
        include_structure=True,
        include_creation_date=True,
        include_modification_date=True,
        include_encoding=True,
        include_git_info=True,
    ),
    
    "ai_focused": MetadataConfig(
        include_file_path=True,
        include_language=True,
        include_purpose=True,
        include_file_size=False,
        include_line_count=False,
        include_token_count=True,
        include_summary=True,
        include_dependencies=True,
        include_structure=True,
        include_creation_date=False,
        include_modification_date=False,
        include_encoding=False,
        include_git_info=False,
    ),
    
    "analysis_focused": MetadataConfig(
        include_file_path=True,
        include_language=True,
        include_purpose=True,
        include_file_size=True,
        include_line_count=True,
        include_token_count=True,
        include_summary=False,
        include_dependencies=True,
        include_structure=True,
        include_creation_date=False,
        include_modification_date=False,
        include_encoding=False,
        include_git_info=False,
    )
}


CONFIGS = {
    "minimal": CodebaseProcessingConfig(
        include_test_files=False,
        include_documentation=False,
        include_config_files=False,
        enable_structure_analysis=False,
        metadata_config=METADATA_PRESETS["minimal"],
    ),
    
    "standard": CodebaseProcessingConfig(
        metadata_config=METADATA_PRESETS["standard"],
    ),
    
    "comprehensive": CodebaseProcessingConfig(
        max_file_size_mb=5.0,
        include_hidden_files=True,
        metadata_config=METADATA_PRESETS["comprehensive"],
    ),
}


def get_codebase_config(config_name: str = "standard") -> CodebaseProcessingConfig:
    if config_name not in CONFIGS:
        available_configs = ", ".join(CONFIGS.keys())
        raise ValueError(f"Unknown config '{config_name}'. Available configs: {available_configs}")
    
    return CONFIGS[config_name]


def list_available_codebase_configs() -> Dict[str, str]:
    return {
        "minimal": "Minimal processing - only essential code files",
        "standard": "Standard processing with tests, docs, and config files",
        "comprehensive": "Comprehensive processing including hidden files and larger files",
    }


def list_available_metadata_presets() -> Dict[str, str]:
    return {
        "minimal": "Minimal metadata - only file path and language",
        "standard": "Standard metadata - common fields for most use cases",
        "comprehensive": "Comprehensive metadata - all available fields",
        "ai_focused": "AI-focused metadata - optimized for AI processing",
        "analysis_focused": "Analysis-focused metadata - for code analysis tools",
    }


def get_metadata_config(preset_name: str = "standard") -> MetadataConfig:
    if preset_name not in METADATA_PRESETS:
        available_presets = ", ".join(METADATA_PRESETS.keys())
        raise ValueError(f"Unknown metadata preset '{preset_name}'. Available presets: {available_presets}")
    
    return METADATA_PRESETS[preset_name]


def create_custom_metadata_config(**field_overrides) -> MetadataConfig:
    base_config = MetadataConfig()
    config_dict = base_config.model_dump()
    config_dict.update(field_overrides)
    return MetadataConfig(**config_dict)
