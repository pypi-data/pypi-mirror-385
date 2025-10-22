import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from rag_knowledge_preparation import (
    convert_documents_batch,
    convert_folder_to_markdown
)
from rag_knowledge_preparation.utils.CustomExceptions import (
    DocumentNotFoundError,
    ConfigurationError,
    ConversionError
)


class TestBatchProcessing:
    def test_convert_documents_batch_list(self):
        document_list = [
            "tests/test_data/test_document.md",
            "tests/test_data/test_document.html"
        ]
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc1 = Mock()
            mock_doc1.export_to_markdown.return_value = "# Document 1"
            mock_result1 = Mock()
            mock_result1.document = mock_doc1
            
            mock_doc2 = Mock()
            mock_doc2.export_to_markdown.return_value = "# Document 2"
            mock_result2 = Mock()
            mock_result2.document = mock_doc2
            
            mock_converter.return_value.convert_all.return_value = [mock_result1, mock_result2]
            
            results = convert_documents_batch(document_list, processing_preset="basic")
            
            assert len(results) == 2
            assert "tests/test_data/test_document.md" in results
            assert "tests/test_data/test_document.html" in results
            assert results["tests/test_data/test_document.md"] == "# Document 1"
            assert results["tests/test_data/test_document.html"] == "# Document 2"
            mock_converter.assert_called_once()
    
    def test_convert_documents_batch_single_file(self):
        single_file = "tests/test_data/test_document.md"
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# Single Document"
            mock_result = Mock()
            mock_result.document = mock_doc
            
            mock_converter.return_value.convert_all.return_value = [mock_result]
            
            results = convert_documents_batch(single_file, processing_preset="basic")
            
            assert len(results) == 1
            assert single_file in results
            assert results[single_file] == "# Single Document"
            mock_converter.assert_called_once()
    
    def test_convert_documents_batch_file_not_found(self):
        non_existent_files = ["non_existent_file.pdf"]
        
        with pytest.raises(DocumentNotFoundError):
            convert_documents_batch(non_existent_files, processing_preset="basic")
    
    def test_convert_documents_batch_invalid_preset(self):
        document_list = ["tests/test_data/test_document.md"]
        
        with pytest.raises(ConfigurationError):
            convert_documents_batch(document_list, processing_preset="invalid_preset")
    
    def test_convert_documents_batch_conversion_error(self):
        document_list = ["tests/test_data/test_document.md"]
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_converter.return_value.convert_all.side_effect = Exception("Conversion failed")
            
            with pytest.raises(ConversionError, match="Failed to convert documents in batch"):
                convert_documents_batch(document_list, processing_preset="basic")
    
    def test_convert_folder_to_markdown(self):
        folder_path = "tests/test_data"
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter._find_supported_documents') as mock_find:
            mock_find.return_value = [
                Path("tests/test_data/test_document.md"),
                Path("tests/test_data/test_document.html")
            ]
            
            with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
                mock_doc1 = Mock()
                mock_doc1.export_to_markdown.return_value = "# Folder Document 1"
                mock_result1 = Mock()
                mock_result1.document = mock_doc1
                
                mock_doc2 = Mock()
                mock_doc2.export_to_markdown.return_value = "# Folder Document 2"
                mock_result2 = Mock()
                mock_result2.document = mock_doc2
                
                mock_converter.return_value.convert_all.return_value = [mock_result1, mock_result2]
                
                results = convert_folder_to_markdown(folder_path, processing_preset="basic")
                
                assert len(results) == 2
                assert "tests/test_data/test_document.md" in results
                assert "tests/test_data/test_document.html" in results
                assert results["tests/test_data/test_document.md"] == "# Folder Document 1"
                assert results["tests/test_data/test_document.html"] == "# Folder Document 2"
                mock_converter.assert_called_once()
    
    def test_convert_folder_to_markdown_folder_not_found(self):
        non_existent_folder = "non_existent_folder"
        
        with pytest.raises(DocumentNotFoundError, match="Folder not found"):
            convert_folder_to_markdown(non_existent_folder, processing_preset="basic")
    
    def test_convert_folder_to_markdown_not_directory(self):
        file_path = "tests/test_data/test_document.md"
        
        with pytest.raises(DocumentNotFoundError, match="Path is not a directory"):
            convert_folder_to_markdown(file_path, processing_preset="basic")
    
    def test_convert_documents_batch_with_custom_config(self):
        document_list = ["tests/test_data/test_document.md"]
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_doc = Mock()
            mock_doc.export_to_markdown.return_value = "# Custom Config Document"
            mock_result = Mock()
            mock_result.document = mock_doc
            
            mock_converter.return_value.convert_all.return_value = [mock_result]
            
            results = convert_documents_batch(
                document_list,
                processing_preset="standard",
                ocr_language="en",
                table_confidence_threshold=0.9
            )
            
            assert len(results) == 1
            assert results[document_list[0]] == "# Custom Config Document"
            mock_converter.assert_called_once()
    
    def test_convert_documents_batch_empty_list(self):
        empty_list = []
        
        with patch('rag_knowledge_preparation.document_processing.DocumentConverter.DocumentConverter') as mock_converter:
            mock_converter.return_value.convert_all.return_value = []
            
            results = convert_documents_batch(empty_list, processing_preset="basic")
            
            assert len(results) == 0
            assert results == {}
            mock_converter.assert_called_once()


class TestFindSupportedDocuments:
    
    def test_find_supported_documents(self):
        from rag_knowledge_preparation.document_processing.DocumentConverter import _find_supported_documents
        
        test_dir = Path("tests/test_data")
        
        if test_dir.exists():
            supported_files = _find_supported_documents(test_dir)
            
            assert len(supported_files) >= 3
            
            supported_extensions = {'.md', '.html', '.csv', '.txt', '.pdf', '.docx', '.pptx', '.xlsx'}
            for file_path in supported_files:
                assert file_path.suffix.lower() in supported_extensions
    
    def test_find_supported_documents_empty_folder(self):
        from rag_knowledge_preparation.document_processing.DocumentConverter import _find_supported_documents
        
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            supported_files = _find_supported_documents(temp_path)
            assert len(supported_files) == 0


if __name__ == "__main__":
    pytest.main([__file__])
