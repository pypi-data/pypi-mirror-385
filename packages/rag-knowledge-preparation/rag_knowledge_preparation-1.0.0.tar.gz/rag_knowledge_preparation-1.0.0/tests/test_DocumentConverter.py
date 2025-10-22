import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from rag_knowledge_preparation import (
    convert_document_to_markdown,
    convert_scanned_document_to_markdown,
    convert_document_with_table_processing,
    convert_document_with_maximum_quality
)
from rag_knowledge_preparation.utils.CustomExceptions import (
    DocumentNotFoundError,
    ConfigurationError
)


class TestDocumentConverter:
    def test_convert_document_to_markdown_file_not_found(self):
        with pytest.raises(DocumentNotFoundError):
            convert_document_to_markdown("non_existent_file.pdf")
    
    def test_convert_document_to_markdown_invalid_preset(self):
        test_file = Path("test_file.txt")
        test_file.touch()
        
        try:
            with pytest.raises(ConfigurationError):
                convert_document_to_markdown(
                    test_file, 
                    processing_preset="invalid_preset"
                )
        finally:
            test_file.unlink()
    
    @patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter')
    def test_convert_document_to_markdown_success(self, mock_converter):
        mock_doc = Mock()
        mock_doc.export_to_markdown.return_value = "# Test Markdown"
        mock_result = Mock()
        mock_result.document = mock_doc
        mock_converter.return_value.convert.return_value = mock_result
        
        test_file = Path("test_file.md")
        test_file.touch()
        
        try:
            result = convert_document_to_markdown(test_file)
            assert result == "# Test Markdown"
            mock_converter.assert_called_once()
        finally:
            test_file.unlink()
    
    @patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter')
    def test_convert_scanned_document_to_markdown(self, mock_converter):
        mock_doc = Mock()
        mock_doc.export_to_markdown.return_value = "# Scanned Document"
        mock_result = Mock()
        mock_result.document = mock_doc
        mock_converter.return_value.convert.return_value = mock_result
        
        test_file = Path("tests/test_data/test_document.md")
        
        result = convert_scanned_document_to_markdown(test_file)
        assert result == "# Scanned Document"
        mock_converter.assert_called_once()
    
    @patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter')
    def test_convert_document_with_table_processing(self, mock_converter):
        mock_doc = Mock()
        mock_doc.export_to_markdown.return_value = "# Table Processing"
        mock_result = Mock()
        mock_result.document = mock_doc
        mock_converter.return_value.convert.return_value = mock_result
        
        test_file = Path("tests/test_data/test_document.md")
        
        result = convert_document_with_table_processing(test_file)
        assert result == "# Table Processing"
        mock_converter.assert_called_once()
    
    @patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter')
    def test_convert_document_with_maximum_quality(self, mock_converter):
        mock_doc = Mock()
        mock_doc.export_to_markdown.return_value = "# Maximum Quality"
        mock_result = Mock()
        mock_result.document = mock_doc
        mock_converter.return_value.convert.return_value = mock_result
        
        test_file = Path("tests/test_data/test_document.md")
        
        result = convert_document_with_maximum_quality(test_file)
        assert result == "# Maximum Quality"
        mock_converter.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
