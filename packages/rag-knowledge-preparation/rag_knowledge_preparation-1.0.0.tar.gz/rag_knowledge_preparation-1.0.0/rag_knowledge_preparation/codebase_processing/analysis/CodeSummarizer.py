import os
from typing import Optional
from pathlib import Path

from ..utils.CodebaseConstants import MAX_SUMMARY_WORDS, MAX_CONTENT_LENGTH

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class CodeSummarizer:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                if not hasattr(genai, '_configured_key') or genai._configured_key != self.api_key:
                    genai.configure(api_key=self.api_key)
                    genai._configured_key = self.api_key
                self.model = genai.GenerativeModel(model_name)
            except Exception:
                self.model = None
    
    def generate_summary(self, content: str, file_path: Path, language: str) -> str:
        if not self.model:
            return self._fallback_summary(content, language)
        
        try:
            code_snippet = self._extract_key_code(content)
            
            prompt = f"""{language} file: {file_path.name}
Code snippet:
{code_snippet}

Summary (max {MAX_SUMMARY_WORDS} words):"""
            
            response = self.model.generate_content(prompt)
            return self._clean_summary(response.text, MAX_SUMMARY_WORDS)
        except Exception:
            return self._fallback_summary(content, language)

    def generate_readme_overview(self, content: str, file_path: Path, max_words: int = 220) -> Optional[str]:
        if not self.model:
            return None

        try:
            trimmed_content = content[:MAX_CONTENT_LENGTH * 2]
            prompt = f"""You are an expert technical writer. Summarize the following project README for stakeholders.

README name: {file_path.name}
README content (truncated):
{trimmed_content}

Write a concise narrative (no bullet lists) of up to {max_words} words that covers:
- the project's purpose and primary capabilities
- the architecture or component layout and key technologies used
- important setup, usage, or operational considerations

Keep the tone factual and highlight the most important details."""

            response = self.model.generate_content(prompt)
            return self._clean_summary(response.text, max_words)
        except Exception:
            return None
    
    def _extract_key_code(self, content: str) -> str:
        """Extract most important parts of code for analysis"""
        lines = content.split('\n')
        key_lines = []
        
        key_lines.extend(lines[:10])
        
        for line in lines:
            stripped = line.strip()
            if (stripped.startswith('class ') or 
                stripped.startswith('def ') or 
                stripped.startswith('function ') or
                stripped.startswith('export ') or
                stripped.startswith('const ') or
                stripped.startswith('interface ')):
                key_lines.append(line)
        
        result = '\n'.join(key_lines)
        return result[:800]
    
    def _clean_summary(self, summary: str, max_words: int = MAX_SUMMARY_WORDS) -> str:
        summary = summary.strip().replace('**', '').replace('*', '').replace('```', '').replace('`', '')
        words = summary.split()
        if max_words and len(words) > max_words:
            summary = ' '.join(words[:max_words]) + '...'
        return summary or "Code file with implementation details"
    
    def _fallback_summary(self, content: str, language: str) -> str:
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) < 5:
            return f"Small {language} file with {len(lines)} lines"
        elif 'def ' in content or 'function ' in content:
            return f"{language} file containing functions and logic"
        elif 'class ' in content:
            return f"{language} file with class definitions"
        elif 'import ' in content or 'require ' in content:
            return f"{language} file with imports and dependencies"
        else:
            return f"{language} code file with {len(lines)} lines of implementation"


_global_summarizer = None
_global_summarizer_config = None
_summary_cache = {}
_readme_summary_cache = {}

def generate_code_summary(content: str, file_path: Path, language: str, api_key: Optional[str] = None, model_name: str = "gemini-pro") -> str:
    global _global_summarizer, _global_summarizer_config
    
    import hashlib
    content_hash = hashlib.md5(content[:1000].encode()).hexdigest()
    cache_key = f"{file_path.name}_{language}_{content_hash[:8]}"
    
    if cache_key in _summary_cache:
        return _summary_cache[cache_key]
    
    current_config = (api_key, model_name)
    
    if _global_summarizer is None or _global_summarizer_config != current_config:
        _global_summarizer = CodeSummarizer(api_key, model_name)
        _global_summarizer_config = current_config
    
    summary = _global_summarizer.generate_summary(content, file_path, language)
    
    if len(_summary_cache) < 100:
        _summary_cache[cache_key] = summary
    
    return summary


def generate_readme_summary(content: str, file_path: Path, api_key: Optional[str] = None, model_name: str = "gemini-pro", max_words: int = 220) -> Optional[str]:
    global _global_summarizer, _global_summarizer_config, _readme_summary_cache

    import hashlib
    content_hash = hashlib.md5(content[:2000].encode()).hexdigest()
    cache_key = f"readme_{file_path.name}_{content_hash[:8]}_{max_words}"

    if cache_key in _readme_summary_cache:
        return _readme_summary_cache[cache_key]

    current_config = (api_key, model_name)

    if _global_summarizer is None or _global_summarizer_config != current_config:
        _global_summarizer = CodeSummarizer(api_key, model_name)
        _global_summarizer_config = current_config

    summary = _global_summarizer.generate_readme_overview(content, file_path, max_words)

    if summary and len(_readme_summary_cache) < 100:
        _readme_summary_cache[cache_key] = summary

    return summary
