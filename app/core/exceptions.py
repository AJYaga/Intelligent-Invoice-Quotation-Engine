class DocumentProcessingError(Exception):
    """Base exception for document-processing failures."""

class UnsupportedFileTypeError(DocumentProcessingError):
    """Raised when the uploaded file type is not supported."""

class InvalidDocumentError(DocumentProcessingError):
    """Raised when a document is corrupt or cannot be processed."""