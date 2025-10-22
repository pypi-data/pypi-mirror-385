from pathlib import Path
from typing import Optional, Dict, Any, Generator
import chardet
import pathspec

from ..core.CodebaseConfig import CodebaseProcessingConfig
from .CodebaseConstants import DEFAULT_IGNORE_PATTERNS, ENCODING_CONFIDENCE_THRESHOLD


def should_ignore_file(file_path: Path, config: CodebaseProcessingConfig) -> bool:
    gitignore_path = _find_gitignore_file(file_path)
    
    if gitignore_path and gitignore_path.exists():
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception:
            patterns = DEFAULT_IGNORE_PATTERNS.copy()
    else:
        patterns = DEFAULT_IGNORE_PATTERNS.copy()
    
    if config.custom_ignore_patterns:
        patterns.extend(config.custom_ignore_patterns)
    
    spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
    if spec.match_file(str(file_path)):
        return True
    
    if file_path.name.startswith('.') and not config.include_hidden_files:
        return True
    
    try:
        if file_path.stat().st_size > config.max_file_size_mb * 1024 * 1024:
            return True
    except (OSError, FileNotFoundError):
        return True
    
    return False


def _find_gitignore_file(file_path: Path) -> Optional[Path]:
    current = file_path.parent if file_path.is_file() else file_path
    
    while current != current.parent:
        gitignore = current / '.gitignore'
        if gitignore.exists():
            return gitignore
        current = current.parent
    
    return None


def read_file_content(file_path: Path) -> str:
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        detected = chardet.detect(raw_data)
        encoding = detected.get('encoding', 'utf-8')
        
        if detected.get('confidence', 0) < ENCODING_CONFIDENCE_THRESHOLD:
            encoding = 'utf-8'
        
        return raw_data.decode(encoding)
    except Exception as e:
        return f"[Error reading file: {e}]"


def walk_files(target_path: Path, config: CodebaseProcessingConfig) -> Generator[Path, None, None]:
    if target_path.is_file():
        if not should_ignore_file(target_path, config):
            yield target_path
        return
    
    for file_path in target_path.rglob('*'):
        if file_path.is_file() and not should_ignore_file(file_path, config):
            yield file_path


def process_file_metadata(file_path: Path, root_path: Path, content: str, 
                         language: str = None, summary: str = None, 
                         dependencies: Dict[str, Any] = None) -> Dict[str, Any]:
    relative_path = str(file_path.relative_to(root_path)) if root_path.is_dir() else file_path.name
    
    metadata = {
        'relative_path': relative_path,
        'content': content,
        'file_path': file_path,
        'root_path': root_path,
    }
    
    if language is not None:
        metadata['language'] = language
    
    if summary is not None:
        metadata['summary'] = summary
    
    if dependencies is not None:
        metadata['dependencies'] = dependencies
    
    return metadata
