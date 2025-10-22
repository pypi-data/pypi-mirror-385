from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import tiktoken
import pygments
import tree_sitter
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

from ..utils.CodebaseConstants import (
    CODE_EXTENSIONS, DOC_EXTENSIONS, CONFIG_EXTENSIONS, SCRIPT_EXTENSIONS,
    TEST_DIRS, DOC_DIRS, CONFIG_DIRS, SCRIPT_DIRS, TREE_SITTER_LANGUAGES
)


class TreeSitterParser:
    def __init__(self):
        self.parsers = {}
        for lang_name, module_name in TREE_SITTER_LANGUAGES:
            try:
                language = tree_sitter.Language(module_name, lang_name)
                self.parsers[lang_name] = tree_sitter.Parser(language)
            except Exception:
                pass
    
    def parse_code_structure(self, content: str, language: str) -> Dict[str, Any]:
        structure = {
            'imports': [],
            'dependencies': [],
            'classes': [],
            'functions': [],
            'constants': [],
            'exports': []
        }
        
        if language not in self.parsers:
            return structure
        
        try:
            tree = self.parsers[language].parse(bytes(content, 'utf8'))
            self._extract_structure_from_tree(tree, structure, language)
        except Exception:
            pass
        
        return structure
    
    def _extract_structure_from_tree(self, tree, structure: Dict[str, Any], language: str) -> None:
        def traverse(node):
            self._process_node_by_language(node, structure, language)
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        
        for key in structure:
            structure[key] = list(dict.fromkeys(structure[key]))
    
    def _process_node_by_language(self, node, structure: Dict[str, Any], language: str) -> None:
        language_mappings = {
            'python': {
                'import_types': ['import_statement', 'import_from_statement'],
                'class_type': 'class_definition',
                'function_type': 'function_definition',
                'constant_type': 'assignment',
                'export_type': None
            },
            'javascript': {
                'import_types': ['import_statement'],
                'class_type': 'class_declaration',
                'function_type': 'function_declaration',
                'constant_type': None,
                'export_type': 'export_statement'
            },
            'typescript': {
                'import_types': ['import_statement'],
                'class_type': 'class_declaration',
                'function_type': 'function_declaration',
                'constant_type': None,
                'export_type': 'export_statement'
            }
        }
        
        mapping = language_mappings.get(language, {})
        if not mapping:
            return
        
        if node.type in mapping.get('import_types', []):
            self._extract_imports(node, structure, language)
        elif node.type in [mapping.get('class_type'), mapping.get('function_type')]:
            target_type = 'classes' if node.type == mapping.get('class_type') else 'functions'
            self._extract_class_or_function(node, structure, target_type)
        elif node.type == mapping.get('constant_type'):
            self._extract_constants(node, structure)
        elif node.type == mapping.get('export_type'):
            self._extract_exports(node, structure)
    
    def _extract_imports(self, node, structure, language):
        if language == 'python':
            self._extract_python_imports(node, structure)
        else:
            self._extract_js_imports(node, structure)
    
    def _extract_python_imports(self, node, structure):
        if node.type == 'import_statement':
            for child in node.children:
                if child.type == 'dotted_name':
                    self._add_module_dependency(child.text.decode(), structure, '.')
        elif node.type == 'import_from_statement':
            module = self._find_dotted_name(node)
            if module:
                self._add_module_dependency(module, structure, '.')
    
    def _extract_js_imports(self, node, structure):
        for child in node.children:
            if child.type == 'string':
                module = child.text.decode().strip('"\'')
                self._add_module_dependency(module, structure, '/')
    
    def _add_module_dependency(self, module: str, structure: Dict[str, Any], separator: str) -> None:
        structure['imports'].append(module)
        structure['dependencies'].append(module.split(separator)[0])
    
    def _find_dotted_name(self, node):
        for child in node.children:
            if child.type == 'dotted_name':
                return child.text.decode()
        return None
    
    def _extract_class_or_function(self, node, structure, target_type):
        self._extract_identifier(node, structure, target_type)
    
    def _extract_constants(self, node, structure):
        for child in node.children:
            if child.type == 'identifier' and child.text.decode().isupper():
                structure['constants'].append(child.text.decode())
    
    def _extract_exports(self, node, structure):
        self._extract_identifier(node, structure, 'exports')
    
    def _extract_identifier(self, node, structure: Dict[str, Any], target_type: str) -> None:
        for child in node.children:
            if child.type == 'identifier':
                structure[target_type].append(child.text.decode())
                break


# Global parser instance
_parser = TreeSitterParser()


def estimate_token_count(text: Union[str, List[str]]) -> int:
    if isinstance(text, list):
        text = "\n".join(text)
    
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return len(text.split())


def get_language_from_extension(file_path: Path) -> str:
    try:
        lexer = get_lexer_for_filename(str(file_path))
        return lexer.aliases[0] if lexer.aliases else 'text'
    except ClassNotFound:
        return 'text'


def classify_file_by_purpose(file_path: Path, content: Optional[str] = None) -> str:
    name = file_path.name.lower()
    suffix = file_path.suffix.lower()
    parts = [p.lower() for p in file_path.parts]

    dir_classifications = [
        (TEST_DIRS, 'Tests'),
        (DOC_DIRS, 'Documentation'),
        (CONFIG_DIRS, 'Configuration'),
        (SCRIPT_DIRS, 'Utilities')
    ]
    
    for dirs, category in dir_classifications:
        if any(seg in parts for seg in dirs):
            return category
    
    # Check file extension first
    ext_classifications = [
        (DOC_EXTENSIONS, 'Documentation'),
        (CONFIG_EXTENSIONS, 'Configuration'),
        (SCRIPT_EXTENSIONS, 'Utilities'),
        (CODE_EXTENSIONS, 'Business Logic')
    ]
    
    for exts, category in ext_classifications:
        if suffix in exts:
            # Special case: if it's a script file but starts with test_, it's still a test
            if category == 'Utilities' and name.startswith('test_'):
                return 'Tests'
            # Special case: if it's a code file but starts with test_, it's still a test
            if category == 'Business Logic' and (name.startswith('test_') or name.startswith('test')):
                return 'Tests'
            return category
    
    # Check for test files by name pattern (only for non-script files)
    if name.startswith('test_') or name.startswith('test'):
        return 'Tests'
    
    return 'Utilities'


def extract_code_structure(file_path: Path, language: str, content: str) -> Dict[str, Any]:
    return _parser.parse_code_structure(content, language)
