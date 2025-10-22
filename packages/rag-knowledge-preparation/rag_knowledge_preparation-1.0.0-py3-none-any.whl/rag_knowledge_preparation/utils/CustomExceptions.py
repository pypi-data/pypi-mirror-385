class RAGKnowledgePreparationError(Exception):
    pass


class DocumentNotFoundError(RAGKnowledgePreparationError):
    pass


class ConfigurationError(RAGKnowledgePreparationError):
    pass


class ConversionError(RAGKnowledgePreparationError):
    pass


class UnsupportedFormatError(RAGKnowledgePreparationError):
    pass
