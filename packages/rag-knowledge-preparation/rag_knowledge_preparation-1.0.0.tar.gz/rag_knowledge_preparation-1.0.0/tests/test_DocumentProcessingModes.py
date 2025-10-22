import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from rag_knowledge_preparation import (
    convert_document_to_markdown,
    convert_scanned_document_to_markdown,
    convert_document_with_table_processing,
    convert_document_with_maximum_quality,
    list_document_configs
)


class TestProcessingModes:
    
    def test_list_available_configs(self):
        configs = list_document_configs()
        
        assert isinstance(configs, dict)
        assert "basic" in configs
        assert "standard" in configs
        assert "ocr_heavy" in configs
        assert "table_focused" in configs
        assert "high_quality" in configs
        
        for description in configs.values():
            assert isinstance(description, str)
    
    def test_basic_mode(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# Basic Mode"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_document_to_markdown(test_file, processing_preset="basic")
            assert result == "# Basic Mode"
            mock_converter.assert_called_once()
    
    def test_standard_mode(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# Standard Mode"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_document_to_markdown(test_file, processing_preset="standard")
            assert result == "# Standard Mode"
            mock_converter.assert_called_once()
    
    def test_ocr_heavy_mode(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# OCR Heavy Mode"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_document_to_markdown(test_file, processing_preset="ocr_heavy")
            assert result == "# OCR Heavy Mode"
            mock_converter.assert_called_once()
    
    def test_table_focused_mode(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# Table Focused Mode"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_document_to_markdown(test_file, processing_preset="table_focused")
            assert result == "# Table Focused Mode"
            mock_converter.assert_called_once()
    
    def test_high_quality_mode(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# High Quality Mode"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_document_to_markdown(test_file, processing_preset="high_quality")
            assert result == "# High Quality Mode"
            mock_converter.assert_called_once()
    
    def test_convert_scanned_document_to_markdown(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# Scanned Document"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_scanned_document_to_markdown(test_file)
            assert result == "# Scanned Document"
            mock_converter.assert_called_once()
    
    def test_convert_document_with_table_processing(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# Table Processing"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_document_with_table_processing(test_file)
            assert result == "# Table Processing"
            mock_converter.assert_called_once()
    
    def test_convert_document_with_maximum_quality(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# Maximum Quality"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_document_with_maximum_quality(test_file)
            assert result == "# Maximum Quality"
            mock_converter.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
