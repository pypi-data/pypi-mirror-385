import re
from pathlib import Path
from typing import List, Dict, Any

from ..utils.CodebaseConstants import CODE_EXTENSIONS


class DependencyAnalyzer:
    
    def __init__(self):
        self.dependency_patterns = {
            'python': [
                r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
                r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import',
                r'^from\s+\.([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import',
            ],
            'javascript': [
                r'import\s+.*?from\s+[\'"]([^"\']+)[\'"]',
                r'require\s*\(\s*[\'"]([^"\']+)[\'"]\s*\)',
                r'import\s+[\'"]([^"\']+)[\'"]',
            ],
            'typescript': [
                r'import\s+.*?from\s+[\'"]([^"\']+)[\'"]',
                r'require\s*\(\s*[\'"]([^"\']+)[\'"]\s*\)',
                r'import\s+[\'"]([^"\']+)[\'"]',
            ],
            'java': [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
            ],
            'go': [
                r'import\s+[\'"]([^"\']+)[\'"]',
                r'import\s+\(\s*[\'"]([^"\']+)[\'"]\s*\)',
            ],
        }
    
    def analyze_dependencies(self, content: str, file_path: Path, language: str) -> Dict[str, Any]:
        dependencies = {
            'imports': [],
            'external_packages': [],
            'internal_modules': [],
            'standard_library': [],
        }
        
        if language not in self.dependency_patterns:
            return dependencies
        
        imports = self._extract_imports(content, language)
        dependencies['imports'] = imports
        
        for import_name in imports:
            category = self._categorize_dependency(import_name, language)
            if category in dependencies:
                dependencies[category].append(import_name)
        
        for key in dependencies:
            dependencies[key] = list(dict.fromkeys(dependencies[key]))
        
        return dependencies
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        imports = []
        patterns = self.dependency_patterns.get(language, [])
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.extend(matches)
        
        return imports
    
    def _categorize_dependency(self, import_name: str, language: str) -> str:
        import_name = import_name.strip('\'"')
        
        stdlib_modules = {
            'python': {
                'os', 'sys', 'json', 'datetime', 'pathlib', 'typing', 'collections',
                'itertools', 'functools', 'operator', 'math', 'random', 'string',
                're', 'urllib', 'http', 'socket', 'threading', 'multiprocessing',
                'subprocess', 'shutil', 'tempfile', 'glob', 'fnmatch', 'csv',
                'xml', 'html', 'base64', 'hashlib', 'uuid', 'time', 'calendar'
            },
            'javascript': {
                'fs', 'path', 'http', 'https', 'url', 'querystring', 'crypto',
                'util', 'events', 'stream', 'buffer', 'os', 'child_process',
                'cluster', 'net', 'tls', 'dgram', 'dns', 'readline', 'repl'
            },
            'java': {
                'java.lang', 'java.util', 'java.io', 'java.net', 'java.math',
                'java.text', 'java.time', 'java.nio', 'java.security', 'java.sql'
            },
            'go': {
                'fmt', 'os', 'io', 'net', 'http', 'strings', 'strconv', 'time',
                'math', 'sort', 'sync', 'context', 'log', 'flag', 'path'
            }
        }
        
        external_indicators = {
            'python': ['numpy', 'pandas', 'requests', 'flask', 'django', 'fastapi', 'pytest'],
            'javascript': ['react', 'vue', 'angular', 'lodash', 'axios', 'express', 'moment'],
            'java': ['org.springframework', 'com.google', 'org.apache', 'io.github'],
            'go': ['github.com', 'golang.org', 'gopkg.in', 'go.uber.org']
        }
        
        stdlib = stdlib_modules.get(language, set())
        if import_name in stdlib or any(import_name.startswith(module + '.') for module in stdlib):
            return 'standard_library'
        
        indicators = external_indicators.get(language, [])
        if any(indicator in import_name.lower() for indicator in indicators):
            return 'external_packages'
        
        return 'internal_modules'


_analyzer = DependencyAnalyzer()


def analyze_file_dependencies(content: str, file_path: Path, language: str) -> Dict[str, Any]:
    """Analyze dependencies in a code file."""
    return _analyzer.analyze_dependencies(content, file_path, language)
