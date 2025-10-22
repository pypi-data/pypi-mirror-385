import pytest
from rag_knowledge_preparation.utils.CustomExceptions import (
    RAGKnowledgePreparationError,
    DocumentNotFoundError,
    ConfigurationError,
    ConversionError,
    UnsupportedFormatError
)


class TestCustomExceptions:
    
    def test_rag_knowledge_preparation_error(self):
        error = RAGKnowledgePreparationError("Test error")
        
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
        assert isinstance(error, RAGKnowledgePreparationError)
    
    def test_document_not_found_error(self):
        error = DocumentNotFoundError("File not found")
        
        assert isinstance(error, RAGKnowledgePreparationError)
        assert isinstance(error, DocumentNotFoundError)
        assert str(error) == "File not found"
    
    def test_configuration_error(self):
        error = ConfigurationError("Invalid configuration")
        
        assert isinstance(error, RAGKnowledgePreparationError)
        assert isinstance(error, ConfigurationError)
        assert str(error) == "Invalid configuration"
    
    def test_conversion_error(self):
        error = ConversionError("Conversion failed")
        
        assert isinstance(error, RAGKnowledgePreparationError)
        assert isinstance(error, ConversionError)
        assert str(error) == "Conversion failed"
    
    def test_unsupported_format_error(self):
        error = UnsupportedFormatError("Format not supported")
        
        assert isinstance(error, RAGKnowledgePreparationError)
        assert isinstance(error, UnsupportedFormatError)
        assert str(error) == "Format not supported"
    
    def test_exception_inheritance(self):
        exceptions = [
            DocumentNotFoundError("test"),
            ConfigurationError("test"),
            ConversionError("test"),
            UnsupportedFormatError("test")
        ]
        
        for exception in exceptions:
            assert isinstance(exception, RAGKnowledgePreparationError)
            assert isinstance(exception, Exception)
    
    def test_exception_with_no_message(self):
        error = RAGKnowledgePreparationError()
        assert str(error) == ""
        
        error = DocumentNotFoundError()
        assert str(error) == ""
        
        error = ConfigurationError()
        assert str(error) == ""
        
        error = ConversionError()
        assert str(error) == ""
        
        error = UnsupportedFormatError()
        assert str(error) == ""


if __name__ == "__main__":
    pytest.main([__file__])
