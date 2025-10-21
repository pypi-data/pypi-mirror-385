"""Utility modules for DeepSeek Visor Agent"""

from .error_handler import (
    OCRError,
    OOMError,
    ModelLoadError,
    ImageProcessingError,
    auto_fallback_decorator
)

from .pdf_processor import (
    PDFProcessingError,
    pdf_to_images,
    is_pdf_file
)

__all__ = [
    "OCRError",
    "OOMError",
    "ModelLoadError",
    "ImageProcessingError",
    "auto_fallback_decorator",
    "PDFProcessingError",
    "pdf_to_images",
    "is_pdf_file"
]
