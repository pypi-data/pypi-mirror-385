import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, Mock

from rag_knowledge_preparation import (
    export_codebase_to_markdown,
    analyze_codebase_structure,
)


class TestPerformanceOptimization:
    
    def test_large_file_handling(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            large_content = "def test_function():\n    return 'test'\n" * 1000
            large_file = temp_path / "large_file.py"
            large_file.write_text(large_content)
            configs = [
                ("minimal", 0.001),
                ("standard", 1.0),
                ("comprehensive", 5.0)
            ]
            
            for config_name, expected_limit in configs:
                result = analyze_codebase_structure(temp_path, processing_preset=config_name)
                assert result['total_files'] == 1
                assert result['total_lines'] > 0
    
    def test_memory_efficiency(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            for i in range(50):
                file_path = temp_path / f"file_{i}.py"
                file_path.write_text(f"def function_{i}():\n    return {i}\n")
            start_time = time.time()
            result = analyze_codebase_structure(temp_path, processing_preset="minimal")
            end_time = time.time()
            
            assert result['total_files'] == 50
            assert end_time - start_time < 10
    
    def test_ignore_patterns_performance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            (temp_path / ".git").mkdir()
            (temp_path / ".git" / "config").write_text("git config")
            (temp_path / "__pycache__").mkdir()
            (temp_path / "__pycache__" / "test.pyc").write_text("compiled python")
            (temp_path / "node_modules").mkdir()
            (temp_path / "node_modules" / "package").write_text("node package")
            (temp_path / "main.py").write_text("print('hello')")
            (temp_path / "utils.py").write_text("def helper(): pass")
            
            result = analyze_codebase_structure(temp_path, processing_preset="minimal")
            assert result['total_files'] == 2
    
    def test_concurrent_processing_simulation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            (temp_path / "src").mkdir()
            (temp_path / "tests").mkdir()
            (temp_path / "docs").mkdir()
            
            (temp_path / "src" / "main.py").write_text("""
import os
from pathlib import Path

def main():
    print("Hello World")

if __name__ == "__main__":
    main()
""")
            
            (temp_path / "src" / "utils.py").write_text("""
def helper_function():
    return "helper"

class HelperClass:
    def method(self):
        return "method"
""")
            
            (temp_path / "tests" / "test_main.py").write_text("""
import unittest
from src.main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        self.assertIsNone(main())
""")
            
            (temp_path / "docs" / "README.md").write_text("# Project Documentation")
            
            start_time = time.time()
            result = analyze_codebase_structure(temp_path, processing_preset="standard")
            end_time = time.time()
            
            assert result['total_files'] == 4
            assert result['total_lines'] > 0
            assert end_time - start_time < 5
    
    def test_token_count_estimation_performance(self):
        from rag_knowledge_preparation.codebase_processing.analysis.CodeAnalyzer import estimate_token_count
        
        test_cases = [
            "Short text",
            "This is a longer text with multiple words and sentences. " * 10,
            "Very long text " * 1000,
        ]
        
        for text in test_cases:
            start_time = time.time()
            token_count = estimate_token_count(text)
            end_time = time.time()
            
            assert isinstance(token_count, int)
            assert token_count > 0
            assert end_time - start_time < 1
    
    def test_dependency_analysis_performance(self):
        from rag_knowledge_preparation.codebase_processing.analysis.DependencyAnalyzer import analyze_file_dependencies
        
        test_cases = [
            ("import os\nprint('hello')", "python"),
            ("import os\nimport sys\nfrom pathlib import Path\nimport requests\n" * 100, "python"),
            ("const fs = require('fs');\nconst path = require('path');\n" * 50, "javascript"),
        ]
        
        for code, language in test_cases:
            start_time = time.time()
            result = analyze_file_dependencies(code, Path("test"), language)
            end_time = time.time()
            
            assert isinstance(result, dict)
            assert end_time - start_time < 1  # Should be fast
    
    def test_structure_analysis_performance(self):
        from rag_knowledge_preparation.codebase_processing.analysis.CodeAnalyzer import extract_code_structure
        
        test_cases = [
            ("def simple():\n    pass", "python"),
            ("""
class ComplexClass:
    def __init__(self):
        self.value = 0
    
    def method1(self):
        return self.value
    
    def method2(self, x, y):
        return x + y

def standalone_function():
    return "test"

CONSTANT = "value"
""", "python"),
        ]
        
        for code, language in test_cases:
            start_time = time.time()
            result = extract_code_structure(Path("test"), language, code)
            end_time = time.time()
            
            assert isinstance(result, dict)
            assert end_time - start_time < 1  # Should be fast


class TestMemoryUsage:
    
    def test_large_codebase_processing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            for i in range(100):
                file_path = temp_path / f"module_{i}.py"
                file_path.write_text(f"""
def function_{i}():
    return {i}

class Class{i}:
    def method(self):
        return {i}
""")
            
            result = analyze_codebase_structure(temp_path, processing_preset="minimal")
            
            assert result['total_files'] == 100
            assert result['total_lines'] > 0
    
    def test_file_size_limits(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            large_content = "x = 1\n" * 100000  # Very large file
            large_file = temp_path / "large_file.py"
            large_file.write_text(large_content)
            
            result = analyze_codebase_structure(temp_path, processing_preset="minimal")
            
            assert result['total_files'] == 1


if __name__ == "__main__":
    pytest.main([__file__])
