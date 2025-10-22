import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from rag_knowledge_preparation import (
    export_codebase_to_markdown,
    analyze_codebase_structure,
    get_codebase_overview,
    CodebaseProcessingConfig,
    get_codebase_config,
    list_available_codebase_configs,
)
from rag_knowledge_preparation.utils.CustomExceptions import (
    DocumentNotFoundError,
    ConfigurationError,
    ConversionError
)


class TestCodebaseProcessing:
    def test_export_codebase_to_markdown_file_not_found(self):
        with pytest.raises(DocumentNotFoundError):
            export_codebase_to_markdown("non_existent_directory")
    
    def test_export_codebase_to_markdown_invalid_preset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.py"
            test_file.write_text("print('hello')")
            
            with pytest.raises(ConfigurationError):
                export_codebase_to_markdown(
                    temp_path, 
                    processing_preset="invalid_preset"
                )
    
    def test_export_codebase_to_markdown_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.py"
            test_file.write_text("print('hello world')")
            
            output_file = temp_path / "output.md"
            result = export_codebase_to_markdown(
                temp_path, 
                output_file=output_file,
                processing_preset="minimal"
            )
            
            assert result == str(output_file)
            assert output_file.exists()
            content = output_file.read_text()
            assert "test.py" in content
            assert "print('hello world')" in content

    def test_export_codebase_includes_readme_overview(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.py").write_text("print('hello world')")
            (temp_path / "README.md").write_text(
                "# Sample Project\n\n"
                "This project does amazing things. It includes a clean architecture with modular components,"  
                "deployment notes, and configuration tips."
            )

            output_file = temp_path / "output.md"
            export_codebase_to_markdown(
                temp_path,
                output_file=output_file,
                processing_preset="minimal"
            )

            content = output_file.read_text()
            assert "## Project Overview" in content
            assert "This project does amazing things." in content
            assert "clean architecture" in content

    def test_export_codebase_without_readme_has_no_overview(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.py").write_text("print('hello world')")

            output_file = temp_path / "output.md"
            export_codebase_to_markdown(
                temp_path,
                output_file=output_file,
                processing_preset="minimal"
            )

            content = output_file.read_text()
            assert "## Project Overview" not in content
    
    def test_analyze_codebase_structure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.py").write_text("def hello():\n    print('hello')")
            (temp_path / "test.js").write_text("function hello() {\n    console.log('hello');\n}")
            (temp_path / "README.md").write_text("# Test Project")
            
            result = analyze_codebase_structure(temp_path, processing_preset="minimal")
            
            assert result['total_files'] == 3
            assert result['total_lines'] > 0
            assert 'python' in result['languages']
            assert 'javascript' in result['languages']
            assert 'markdown' in result['languages']
    
    def test_get_codebase_overview(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            result = get_codebase_overview(temp_path, processing_preset="standard")
            
            assert result['path'] == str(temp_path)
            assert result['name'] == temp_path.name
            assert result['is_directory'] is True
            assert result['is_file'] is False
    
    def test_codebase_processing_config_validation(self):
        config = CodebaseProcessingConfig(max_file_size_mb=2.0)
        assert config.max_file_size_mb == 2.0
        with pytest.raises(ValueError):
            CodebaseProcessingConfig(max_file_size_mb=-1.0)
    
    def test_get_codebase_config(self):
        minimal_config = get_codebase_config("minimal")
        assert minimal_config.include_test_files is False
        
        standard_config = get_codebase_config("standard")
        assert standard_config.include_test_files is True
        
        comprehensive_config = get_codebase_config("comprehensive")
        assert comprehensive_config.max_file_size_mb == 5.0
        with pytest.raises(ValueError):
            get_codebase_config("invalid_config")
    
    def test_list_available_codebase_configs(self):
        configs = list_available_codebase_configs()
        
        assert "minimal" in configs
        assert "standard" in configs
        assert "comprehensive" in configs
        assert isinstance(configs["minimal"], str)
    
    @patch('rag_knowledge_preparation.codebase_processing.core.CodebaseConverter.export_to_markdown')
    def test_export_with_custom_config(self, mock_export):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.py"
            test_file.write_text("print('hello')")
            
            mock_export.return_value = None
            
            export_codebase_to_markdown(
                temp_path,
                processing_preset="standard",
                max_file_size_mb=2.0,
                include_test_files=False
            )
            
            mock_export.assert_called_once()
            call_args = mock_export.call_args
            config = call_args[0][2]
            
            assert config.max_file_size_mb == 2.0
            assert config.include_test_files is False
    
    def test_export_single_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.py"
            test_file.write_text("def hello():\n    return 'world'")
            
            output_file = temp_path / "output.md"
            result = export_codebase_to_markdown(
                test_file, 
                output_file=output_file,
                processing_preset="minimal"
            )
            
            assert result == str(output_file)
            assert output_file.exists()
            content = output_file.read_text()
            assert "test.py" in content
            assert "def hello():" in content


class TestCodebaseAnalysis:
    
    def test_dependency_analyzer(self):
        from rag_knowledge_preparation.codebase_processing.analysis.DependencyAnalyzer import analyze_file_dependencies
        
        python_code = """
import os
import sys
from pathlib import Path
import requests
from .local_module import helper
"""
        
        result = analyze_file_dependencies(python_code, Path("test.py"), "python")
        
        assert "imports" in result
        assert "external_packages" in result
        assert "internal_modules" in result
        assert "standard_library" in result
        
        assert "os" in result["standard_library"]
        assert "sys" in result["standard_library"]
        assert "pathlib" in result["standard_library"]
        assert "requests" in result["external_packages"]
        assert "local_module" in result["internal_modules"]
    
    def test_code_structure_extraction(self):
        from rag_knowledge_preparation.codebase_processing.analysis.CodeAnalyzer import extract_code_structure
        
        python_code = """
class TestClass:
    def __init__(self):
        self.value = 42
    
    def method(self):
        return self.value

def standalone_function():
    return "hello"

CONSTANT = "test"
"""
        
        result = extract_code_structure(Path("test.py"), "python", python_code)
        
        assert "classes" in result
        assert "functions" in result
        assert "constants" in result
        assert "imports" in result
    
    def test_language_detection(self):
        from rag_knowledge_preparation.codebase_processing.analysis.CodeAnalyzer import get_language_from_extension
        
        assert get_language_from_extension(Path("test.py")) == "python"
        assert get_language_from_extension(Path("test.js")) == "javascript"
        assert get_language_from_extension(Path("test.ts")) == "typescript"
        assert get_language_from_extension(Path("test.java")) == "java"
        assert get_language_from_extension(Path("test.go")) == "go"
    
    def test_file_purpose_classification(self):
        from rag_knowledge_preparation.codebase_processing.analysis.CodeAnalyzer import classify_file_by_purpose
        
        assert classify_file_by_purpose(Path("test.py")) == "Tests"
        assert classify_file_by_purpose(Path("README.md")) == "Documentation"
        assert classify_file_by_purpose(Path("config.yaml")) == "Configuration"
        assert classify_file_by_purpose(Path("test_script.sh")) == "Tests"
        assert classify_file_by_purpose(Path("test_file.py")) == "Tests"
        assert classify_file_by_purpose(Path("script.sh")) == "Utilities"
        assert classify_file_by_purpose(Path("main.py")) == "Business Logic"
    
    def test_token_count_estimation(self):
        from rag_knowledge_preparation.codebase_processing.analysis.CodeAnalyzer import estimate_token_count
        
        text = "This is a test string with multiple words."
        token_count = estimate_token_count(text)
        
        assert isinstance(token_count, int)
        assert token_count > 0
        
        text_list = ["Line 1", "Line 2", "Line 3"]
        token_count_list = estimate_token_count(text_list)
        
        assert isinstance(token_count_list, int)
        assert token_count_list > 0


class TestCodeSummarizer:
    
    @patch('rag_knowledge_preparation.codebase_processing.analysis.CodeSummarizer.GEMINI_AVAILABLE', False)
    def test_fallback_summary(self):
        """Test fallback summary when Gemini is not available."""
        from rag_knowledge_preparation.codebase_processing.analysis.CodeSummarizer import generate_code_summary
        
        python_code = """
def calculate_sum(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
"""
        
        summary = generate_code_summary(python_code, Path("test.py"), "python")
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "python" in summary.lower()
    
    @patch('rag_knowledge_preparation.codebase_processing.analysis.CodeSummarizer.GEMINI_AVAILABLE', True)
    @patch('rag_knowledge_preparation.codebase_processing.analysis.CodeSummarizer.genai')
    def test_ai_summary(self, mock_genai):
        """Test AI-powered summary generation."""
        from rag_knowledge_preparation.codebase_processing.analysis.CodeSummarizer import generate_code_summary
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "This is a Python file containing a calculator class with mathematical operations."
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = Mock()
        mock_genai._configured_key = None
        
        python_code = """
class Calculator:
    def add(self, a, b):
        return a + b
"""
        
        summary = generate_code_summary(python_code, Path("test.py"), "python", "test_api_key")
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        mock_genai.configure.assert_called_once_with(api_key="test_api_key")
        mock_genai.GenerativeModel.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
