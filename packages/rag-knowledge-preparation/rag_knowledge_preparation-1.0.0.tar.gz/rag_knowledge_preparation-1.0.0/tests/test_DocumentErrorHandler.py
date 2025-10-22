import pytest
from pathlib import Path
from unittest.mock import patch

from rag_knowledge_preparation import convert_document_to_markdown
from rag_knowledge_preparation.utils.CustomExceptions import (
    DocumentNotFoundError,
    ConfigurationError
)


class TestErrorHandling:
    
    def test_file_not_found_error(self):
        with pytest.raises(DocumentNotFoundError):
            convert_document_to_markdown("non_existent_file.pdf")
    
    def test_invalid_processing_preset(self):
        # Create a temporary file for testing
        test_file = Path("tests/test_data/test_document.md")
        
        with pytest.raises(ConfigurationError):
            convert_document_to_markdown(
                test_file, 
                processing_preset="invalid_preset"
            )
    
    def test_invalid_configuration_override(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with pytest.raises(ConfigurationError):
            convert_document_to_markdown(
                test_file,
                processing_preset="standard",
                invalid_option="test"
            )
    
    def test_unsupported_file_format(self):
        test_file = Path("tests/test_data/test_document.txt")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_converter.return_value.convert.side_effect = Exception("File format not allowed: test_document.txt")
            
            with pytest.raises(Exception, match="File format not allowed"):
                convert_document_to_markdown(test_file, processing_preset="basic")
    
    def test_conversion_failure(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_converter.return_value.convert.side_effect = Exception("Conversion failed")
            
            with pytest.raises(Exception, match="Conversion failed"):
                convert_document_to_markdown(test_file, processing_preset="basic")
    
    def test_invalid_ocr_engine(self):
        test_file = Path("tests/test_data/test_document.md")
        
        try:
            result = convert_document_to_markdown(
                test_file,
                processing_preset="standard",
                ocr_engine="invalid_engine"
            )
            assert isinstance(result, str)
        except Exception as e:
            assert isinstance(e, Exception)
    
    def test_invalid_table_confidence_threshold(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with pytest.raises(ConfigurationError):
            convert_document_to_markdown(
                test_file,
                processing_preset="standard",
                table_confidence_threshold=1.5
            )
    
    def test_invalid_table_processing_mode(self):
        test_file = Path("tests/test_data/test_document.md")
        
        try:
            result = convert_document_to_markdown(
                test_file,
                processing_preset="standard",
                table_processing="invalid_mode"
            )
            assert isinstance(result, str)
        except Exception as e:
            assert isinstance(e, Exception)


if __name__ == "__main__":
    pytest.main([__file__])
