from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import concurrent.futures
import threading

from ..core.CodebaseConfig import CodebaseProcessingConfig, MetadataConfig
from ..utils.FileUtils import walk_files, read_file_content, process_file_metadata
from ..utils.CodebaseConstants import MAX_DISPLAY_ITEMS, MAX_DEPENDENCY_ITEMS
from ..analysis.CodeAnalyzer import (
    get_language_from_extension, classify_file_by_purpose, 
    extract_code_structure, estimate_token_count
)
from ..analysis.CodeSummarizer import generate_code_summary, generate_readme_summary
from ..analysis.DependencyAnalyzer import analyze_file_dependencies


def export_to_markdown(target_path: Path, output_file: Path, config: CodebaseProcessingConfig) -> None:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {target_path.name} Codebase\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        overview = _build_project_overview(target_path, config)
        if overview:
            f.write("## Project Overview\n\n")
            f.write(f"{overview}\n\n")

        if target_path.is_file():
            f.write(f"## {target_path.name}\n\n")
            _process_file(target_path, target_path, f, config)
        else:
            f.write("## Directory Structure\n\n")
            _write_structure(target_path, f, config)
            f.write("\n## File Contents\n\n")
            _process_files(target_path, f, config)


def analyze_structure(target_path: Path, config: CodebaseProcessingConfig) -> Dict[str, Any]:
    overview = {'total_files': 0, 'total_lines': 0, 'total_tokens': 0, 
                'file_types': {}, 'languages': {}, 'file_purposes': {}}
    
    for file_path in walk_files(target_path, config):
        overview['total_files'] += 1
        content = read_file_content(file_path)
        if content.startswith("[Error"):
            continue
        
        overview['total_lines'] += len(content.split('\n'))
        overview['total_tokens'] += estimate_token_count(content)
        
        ext = file_path.suffix.lower()
        lang = get_language_from_extension(file_path)
        purpose = classify_file_by_purpose(file_path, content)
        
        overview['file_types'][ext] = overview['file_types'].get(ext, 0) + 1
        overview['languages'][lang] = overview['languages'].get(lang, 0) + 1
        overview['file_purposes'][purpose] = overview['file_purposes'].get(purpose, 0) + 1
    
    return overview

def get_overview(target_path: Path, config: CodebaseProcessingConfig) -> Dict[str, Any]:
    return {
        'path': str(target_path),
        'name': target_path.name,
        'is_file': target_path.is_file(),
        'is_directory': target_path.is_dir()
    }


def _write_structure(target_path: Path, f, config: CodebaseProcessingConfig) -> None:
    for item in sorted(target_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if item.name.startswith('.') and not config.include_hidden_files:
            continue
        if item.is_file():
            purpose = classify_file_by_purpose(item, None)
            f.write(f"- `{item.name}` ({purpose})\n")
        else:
            f.write(f"- `{item.name}/` (directory)\n")


def _build_project_overview(target_path: Path, config: CodebaseProcessingConfig) -> Optional[str]:
    if not target_path.is_dir():
        return None

    readme_path = _find_readme_file(target_path)
    if not readme_path:
        return None

    summary = _generate_readme_summary(readme_path, config)
    if summary:
        return summary.strip()
    return None


def _find_readme_file(target_path: Path) -> Optional[Path]:
    potential_names = [
        "README.md",
        "README.MD",
        "readme.md",
        "README",
        "readme",
    ]

    for name in potential_names:
        candidate = target_path / name
        if candidate.exists() and candidate.is_file():
            return candidate

    for file_path in target_path.iterdir():
        if file_path.is_file() and file_path.name.lower().startswith("readme"):
            return file_path

    return None


def _generate_readme_summary(readme_path: Path, config: CodebaseProcessingConfig) -> Optional[str]:
    content = read_file_content(readme_path)
    if content.startswith("[Error"):
        return None

    if config.enable_ai_summary and config.gemini_api_key:
        try:
            return generate_readme_summary(content, readme_path, config.gemini_api_key, config.gemini_model, max_words=220)
        except Exception:
            pass

    MAX_OVERVIEW_LENGTH = 1200
    cleaned = content.strip()
    if len(cleaned) > MAX_OVERVIEW_LENGTH:
        return cleaned[:MAX_OVERVIEW_LENGTH].rstrip() + "..."
    return cleaned

def _process_file(file_path: Path, root_path: Path, f, config: CodebaseProcessingConfig) -> None:
    content = read_file_content(file_path)
    if content.startswith("[Error"):
        f.write(f"**Error**: {content}\n\n")
        return
    
    language = get_language_from_extension(file_path)
    purpose = classify_file_by_purpose(file_path, content)
    
    summary = f"{language} file"
    if config.enable_ai_summary and config.gemini_api_key:
        summary = generate_code_summary(content, file_path, language, 
                                       config.gemini_api_key, config.gemini_model)
    
    dependencies = analyze_file_dependencies(content, file_path, language)
    metadata = process_file_metadata(file_path, root_path, content, language, summary, dependencies)
    
    _write_metadata(f, metadata, language, purpose, content, config)
    _write_dependencies(f, dependencies, config)
    _write_structure_info(f, file_path, language, content, config)
    
    f.write("### Content\n\n")
    f.write(f"```{language}\n{content}\n```\n\n")


def _write_metadata(f, metadata: Dict[str, Any], language: str, purpose: str, content: str, config: CodebaseProcessingConfig) -> None:
    f.write("### Metadata\n\n")
    meta_config = config.metadata_config or MetadataConfig()
    
    if meta_config.include_file_path:
        f.write(f"- **File**: `{metadata['relative_path']}`\n")
    if meta_config.include_language:
        f.write(f"- **Language**: `{language}`\n")
    if meta_config.include_purpose:
        f.write(f"- **Purpose**: `{purpose}`\n")
    if meta_config.include_file_size:
        f.write(f"- **Size**: {len(content)} characters\n")
    if meta_config.include_line_count:
        f.write(f"- **Lines**: {len(content.splitlines())}\n")
    if meta_config.include_token_count:
        f.write(f"- **Tokens**: ~{estimate_token_count(content)}\n")
    if meta_config.include_summary:
        f.write(f"- **Summary**: {metadata.get('summary', 'N/A')}\n")
    
    if meta_config.include_modification_date:
        try:
            import os
            mod_time = os.path.getmtime(metadata['file_path'])
            f.write(f"- **Modified**: {datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')}\n")
        except:
            pass
    
    if meta_config.include_git_info:
        git_info = _get_git_info(metadata['file_path'])
        if git_info:
            f.write(f"- **Last Commit**: {git_info.get('hash', 'N/A')[:8]}\n")
            f.write(f"- **Author**: {git_info.get('author', 'N/A')}\n")
            f.write(f"- **Date**: {git_info.get('date', 'N/A')}\n")
    
    f.write("\n")

def _get_git_info(file_path):
    """Get git information for a file."""
    try:
        import subprocess
        import os
        
        git_root = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=file_path.parent,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        rel_path = os.path.relpath(file_path, git_root)
        
        commit_info = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=format:%H|%an|%ad', '--date=short', rel_path],
            cwd=git_root,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        if commit_info:
            hash_part, author, date = commit_info.split('|', 2)
            return {
                'hash': hash_part,
                'author': author,
                'date': date
            }
    except:
        pass
    
    return None

def _write_dependencies(f, dependencies: Dict[str, Any], config: CodebaseProcessingConfig) -> None:
    meta_config = config.metadata_config or MetadataConfig()
    if not meta_config.include_dependencies:
        return
    
    has_deps = dependencies and any(deps for deps in dependencies.values())
    if not has_deps:
        return
        
    f.write("### Dependencies\n\n")
    for dep_type, deps in dependencies.items():
        if deps:
            items = deps[:MAX_DEPENDENCY_ITEMS]
            f.write(f"- **{dep_type.replace('_', ' ').title()}**: {', '.join(items)}")
            if len(deps) > MAX_DEPENDENCY_ITEMS:
                f.write(f" (and {len(deps) - MAX_DEPENDENCY_ITEMS} more)")
            f.write("\n")
    f.write("\n")

def _write_structure_info(f, file_path: Path, language: str, content: str, config: CodebaseProcessingConfig) -> None:
    meta_config = config.metadata_config or MetadataConfig()
    if not config.enable_structure_analysis or not meta_config.include_structure:
        return
        
    structure = extract_code_structure(file_path, language, content)
    if not structure or not any(values for values in structure.values()):
        return
    
    f.write("### Structure\n\n")
    for key, values in structure.items():
        if values:
            items = values[:MAX_DISPLAY_ITEMS]
            f.write(f"- **{key.title()}**: {', '.join(items)}")
            if len(values) > MAX_DISPLAY_ITEMS:
                f.write(f" (and {len(values) - MAX_DISPLAY_ITEMS} more)")
            f.write("\n")
    f.write("\n")


_ai_cache = None
_lock = threading.Lock()

def _get_ai_summarizer(config):
    global _ai_cache
    if not config.enable_ai_summary or not config.gemini_api_key:
        return None
    
    with _lock:
        if _ai_cache is None:
            from ..analysis.CodeSummarizer import CodeSummarizer
            _ai_cache = CodeSummarizer(config.gemini_api_key, config.gemini_model)
        return _ai_cache

def _process_file_ai(file_path: Path, root_path: Path, config: CodebaseProcessingConfig) -> Dict[str, Any]:
    content = read_file_content(file_path)
    if content.startswith("[Error"):
        return {"error": content, "file_path": file_path}
    
    language = get_language_from_extension(file_path)
    purpose = classify_file_by_purpose(file_path, content)
    dependencies = analyze_file_dependencies(content, file_path, language)
    
    summarizer = _get_ai_summarizer(config)
    if summarizer:
        try:
            summary = summarizer.generate_summary(content, file_path, language)
        except Exception as e:
            summary = f"{language} file"
    else:
        summary = f"{language} file"
    
    metadata = process_file_metadata(file_path, root_path, content, language, summary, dependencies)
    
    return {
        "file_path": file_path,
        "content": content,
        "language": language,
        "purpose": purpose,
        "dependencies": dependencies,
        "metadata": metadata
    }

def _process_files(target_path: Path, f, config: CodebaseProcessingConfig) -> None:
    files = list(walk_files(target_path, config))
    
    if not config.enable_ai_summary:
        print(f"Processing {len(files)} files WITHOUT AI...")
        for file_path in files:
            f.write(f"## {file_path.relative_to(target_path)}\n\n")
            _process_file(file_path, target_path, f, config)
        print(f"All files processed without AI.")
        return
    
    print(f"Processing {len(files)} files with AI...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(16, len(files))) as executor:
        future_to_file = {
            executor.submit(_process_file_ai, file_path, target_path, config): file_path
            for file_path in files
        }
        
        results = {}
        for future in concurrent.futures.as_completed(future_to_file):
            result = future.result()
            results[result["file_path"]] = result
    
    print(f"All files processed. Writing to markdown...")
    
    for file_path in files:
        f.write(f"## {file_path.relative_to(target_path)}\n\n")
        
        result = results.get(file_path, {})
        if "error" in result:
            f.write(f"**Error**: {result['error']}\n\n")
        else:
            _write_metadata(f, result["metadata"], result["language"], result["purpose"], result["content"], config)
            _write_dependencies(f, result["dependencies"], config)
            _write_structure_info(f, result["file_path"], result["language"], result["content"], config)
            f.write("### Content\n\n")
            f.write(f"```{result['language']}\n{result['content']}\n```\n\n")
