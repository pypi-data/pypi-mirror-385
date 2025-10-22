import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from rag_knowledge_preparation import convert_document_to_markdown


class TestDifferentFormats:
    
    def test_markdown_format(self):
        test_file = Path("tests/test_data/test_document.md")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# Test Markdown"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_document_to_markdown(test_file, processing_preset="basic")
            assert result == "# Test Markdown"
            mock_converter.assert_called_once()
    
    def test_html_format(self):
        test_file = Path("tests/test_data/test_document.html")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# Test HTML"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_document_to_markdown(test_file, processing_preset="basic")
            assert result == "# Test HTML"
            mock_converter.assert_called_once()
    
    def test_csv_format(self):
        test_file = Path("tests/test_data/test_document.csv")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "| Name | Age |"
            mock_result = Mock()
            mock_result.document = mock_doc
            mock_converter.return_value.convert.return_value = mock_result
            
            result = convert_document_to_markdown(test_file, processing_preset="basic")
            assert result == "| Name | Age |"
            mock_converter.assert_called_once()
    
    def test_unsupported_format(self):
        test_file = Path("tests/test_data/test_document.txt")
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_converter.return_value.convert.side_effect = Exception("File format not allowed: test_document.txt")
            
            with pytest.raises(Exception, match="File format not allowed"):
                convert_document_to_markdown(test_file, processing_preset="basic")


if __name__ == "__main__":
    pytest.main([__file__])
