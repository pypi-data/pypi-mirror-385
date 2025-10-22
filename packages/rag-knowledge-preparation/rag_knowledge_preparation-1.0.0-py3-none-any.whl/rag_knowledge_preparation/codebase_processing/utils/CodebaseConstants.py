CODE_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rb', '.php', '.cs', '.cpp', '.c'}
DOC_EXTENSIONS = {'.md', '.rst', '.adoc'}
CONFIG_EXTENSIONS = {'.yml', '.yaml', '.json', '.ini', '.cfg', '.toml', '.env'}
SCRIPT_EXTENSIONS = {'.sh', '.ps1', '.cmd', '.bat'}

TEST_DIRS = {'test', 'tests', '__tests__'}
DOC_DIRS = {'docs', 'doc', 'documentation'}
CONFIG_DIRS = {'config', 'conf', 'settings'}
SCRIPT_DIRS = {'scripts', 'script', 'bin', 'tools', 'utils'}

TREE_SITTER_LANGUAGES = [
    ('python', 'tree_sitter_python'),
    ('javascript', 'tree_sitter_javascript'),
    ('typescript', 'tree_sitter_typescript'),
]

DEFAULT_IGNORE_PATTERNS = [
    ".*",
    "__pycache__",
    "node_modules",
    "*.pyc",
    "venv",
    ".venv",
]

MAX_SUMMARY_WORDS = 30
MAX_CONTENT_LENGTH = 2000
MAX_DISPLAY_ITEMS = 10
MAX_DEPENDENCY_ITEMS = 5

DEFAULT_MAX_FILE_SIZE_MB = 1.0
COMPREHENSIVE_MAX_FILE_SIZE_MB = 5.0

ENCODING_CONFIDENCE_THRESHOLD = 0.7
