"""Custom exceptions for docufill."""


class SystemDependencyError(RuntimeError):
    """Raised when a required system dependency (tesseract, poppler) is missing."""


class ExtractionError(RuntimeError):
    """Raised when document data extraction fails completely."""
