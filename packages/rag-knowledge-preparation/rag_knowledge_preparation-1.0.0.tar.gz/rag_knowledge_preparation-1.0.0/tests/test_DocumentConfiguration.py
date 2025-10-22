import pytest
from rag_knowledge_preparation.document_processing.DocumentProcessingConfig import (
    ProcessingConfig,
    get_config,
    list_available_configs,
    create_pipeline_options,
    CONFIGS
)


class TestProcessingConfig:
    def test_default_config(self):
        config = ProcessingConfig()
        
        assert config.enable_ocr is True
        assert config.table_processing == "advanced"
        assert config.ocr_engine == "easyocr"
        assert config.ocr_language == "en"
        assert config.table_confidence_threshold == 0.8
        assert config.enable_cell_matching is True
        assert config.enable_table_structure is True
    
    def test_custom_config(self):
        config = ProcessingConfig(
            enable_ocr=False,
            table_processing="basic",
            ocr_engine="tesseract",
            ocr_language="fr",
            table_confidence_threshold=0.9,
            enable_cell_matching=False,
            enable_table_structure=False
        )
        
        assert config.enable_ocr is False
        assert config.table_processing == "basic"
        assert config.ocr_engine == "tesseract"
        assert config.ocr_language == "fr"
        assert config.table_confidence_threshold == 0.9
        assert config.enable_cell_matching is False
        assert config.enable_table_structure is False
    
    def test_invalid_table_confidence_threshold(self):
        with pytest.raises(ValueError, match="table_confidence_threshold must be between 0.0 and 1.0"):
            ProcessingConfig(table_confidence_threshold=1.5)
        
        with pytest.raises(ValueError, match="table_confidence_threshold must be between 0.0 and 1.0"):
            ProcessingConfig(table_confidence_threshold=-0.1)
    
    def test_valid_table_confidence_threshold(self):
        # Test boundary values
        config1 = ProcessingConfig(table_confidence_threshold=0.0)
        assert config1.table_confidence_threshold == 0.0
        
        config2 = ProcessingConfig(table_confidence_threshold=1.0)
        assert config2.table_confidence_threshold == 1.0
        
        config3 = ProcessingConfig(table_confidence_threshold=0.5)
        assert config3.table_confidence_threshold == 0.5


class TestConfigManagement:
    
    def test_get_config_valid_preset(self):
        config = get_config("basic")
        assert isinstance(config, ProcessingConfig)
        assert config.enable_ocr is False
        assert config.table_processing == "basic"
        
        config = get_config("standard")
        assert isinstance(config, ProcessingConfig)
        assert config.enable_ocr is True
        assert config.table_processing == "advanced"
        
        config = get_config("high_quality")
        assert isinstance(config, ProcessingConfig)
        assert config.enable_ocr is True
        assert config.table_processing == "tableformer"
    
    def test_get_config_invalid_preset(self):
        with pytest.raises(ValueError):
            get_config("invalid_preset")
    
    def test_get_config_default(self):
        config = get_config()  # Should default to "standard"
        assert isinstance(config, ProcessingConfig)
        assert config.enable_ocr is True
        assert config.table_processing == "advanced"
    
    def test_list_available_configs(self):
        configs = list_available_configs()
        
        assert isinstance(configs, dict)
        assert len(configs) == len(CONFIGS)
        
        # Check that all predefined configs are listed
        for config_name in CONFIGS.keys():
            assert config_name in configs
            assert isinstance(configs[config_name], str)
            assert len(configs[config_name]) > 0
    
    def test_create_pipeline_options(self):
        config = ProcessingConfig(
            enable_ocr=True,
            table_processing="advanced",
            ocr_engine="easyocr",
            ocr_language="en",
            table_confidence_threshold=0.8,
            enable_cell_matching=True,
            enable_table_structure=True
        )
        
        pipeline_options = create_pipeline_options(config)
        
        # Check that pipeline options are created
        assert pipeline_options is not None
        assert hasattr(pipeline_options, 'do_ocr')
        assert hasattr(pipeline_options, 'do_table_structure')
        assert hasattr(pipeline_options, 'ocr_options')
        assert hasattr(pipeline_options, 'table_structure_options')
        
        # Check OCR configuration
        assert pipeline_options.do_ocr is True
        assert pipeline_options.ocr_options.lang == ["en"]
        
        # Check table structure configuration
        assert pipeline_options.do_table_structure is True
        assert pipeline_options.table_structure_options.do_cell_matching is True
    
    def test_create_pipeline_options_no_ocr(self):
        config = ProcessingConfig(
            enable_ocr=False,
            table_processing="basic",
            enable_table_structure=False,
            enable_cell_matching=False
        )
        
        pipeline_options = create_pipeline_options(config)
        
        assert pipeline_options.do_ocr is False
        assert pipeline_options.do_table_structure is False


class TestPredefinedConfigs:
    
    def test_basic_config(self):
        config = CONFIGS["basic"]
        
        assert config.enable_ocr is False
        assert config.table_processing == "basic"
        assert config.enable_table_structure is False
        assert config.enable_cell_matching is False
    
    def test_standard_config(self):
        config = CONFIGS["standard"]
        
        assert config.enable_ocr is True
        assert config.table_processing == "advanced"
        assert config.ocr_engine == "easyocr"
        assert config.ocr_language == "en"
    
    def test_ocr_heavy_config(self):
        config = CONFIGS["ocr_heavy"]
        
        assert config.enable_ocr is True
        assert config.table_processing == "advanced"
        assert config.ocr_engine == "tesseract"
        assert config.ocr_language == "en"
        assert config.table_confidence_threshold == 0.9
    
    def test_table_focused_config(self):
        config = CONFIGS["table_focused"]
        
        assert config.enable_ocr is True
        assert config.table_processing == "tableformer"
        assert config.ocr_engine == "easyocr"
        assert config.ocr_language == "en"
        assert config.table_confidence_threshold == 0.8
        assert config.enable_cell_matching is True
    
    def test_high_quality_config(self):
        config = CONFIGS["high_quality"]
        
        assert config.enable_ocr is True
        assert config.table_processing == "tableformer"
        assert config.ocr_engine == "easyocr"
        assert config.ocr_language == "en"
        assert config.table_confidence_threshold == 0.9
        assert config.enable_cell_matching is True


if __name__ == "__main__":
    pytest.main([__file__])
