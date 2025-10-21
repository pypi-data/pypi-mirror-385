"""
PDF processing utilities using PyMuPDF (fitz)

Based on DeepSeek-OCR official implementation:
https://github.com/deepseek-ai/DeepSeek-OCR/blob/master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py
"""

import io
import logging
from pathlib import Path
from typing import List, Optional, Union

from PIL import Image

logger = logging.getLogger(__name__)


class PDFProcessingError(Exception):
    """PDF processing related errors"""
    pass


def pdf_to_images(
    pdf_path: Union[str, Path],
    dpi: int = 144,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
) -> List[Image.Image]:
    """
    Convert PDF pages to PIL images using PyMuPDF (official DeepSeek-OCR method)

    Args:
        pdf_path: Path to PDF file
        dpi: Resolution for rendering (default: 144, same as DeepSeek-OCR official)
        start_page: First page to process (0-indexed), None for first page
        end_page: Last page to process (0-indexed), None for last page

    Returns:
        List of PIL Image objects, one per page

    Raises:
        PDFProcessingError: If PDF cannot be opened or processed

    Example:
        >>> images = pdf_to_images("contract.pdf", dpi=144)
        >>> print(f"Converted {len(images)} pages")
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise PDFProcessingError(
            "PyMuPDF is not installed. Install with: pip install PyMuPDF>=1.23.0"
        )

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise PDFProcessingError(f"PDF file not found: {pdf_path}")

    if not pdf_path.suffix.lower() == '.pdf':
        raise PDFProcessingError(f"File is not a PDF: {pdf_path}")

    try:
        # Open PDF document
        pdf_document = fitz.open(str(pdf_path))

        # Calculate zoom factor from DPI (72 is the default PDF DPI)
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)

        # Determine page range
        total_pages = pdf_document.page_count
        start = start_page if start_page is not None else 0
        end = end_page + 1 if end_page is not None else total_pages

        # Validate page range
        if start < 0 or start >= total_pages:
            raise PDFProcessingError(
                f"start_page {start} out of range (PDF has {total_pages} pages)"
            )
        if end > total_pages:
            raise PDFProcessingError(
                f"end_page {end_page} out of range (PDF has {total_pages} pages)"
            )

        logger.info(
            f"Converting PDF pages {start} to {end-1} (total: {total_pages} pages) "
            f"at {dpi} DPI"
        )

        images = []

        for page_num in range(start, end):
            page = pdf_document[page_num]

            # Render page to pixmap (image)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)

            # Remove PIL image size limit (same as official code)
            Image.MAX_IMAGE_PIXELS = None

            # Convert pixmap to PIL Image
            img_data = pixmap.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            images.append(img)
            logger.debug(f"Converted page {page_num}: {img.size}")

        pdf_document.close()
        logger.info(f"Successfully converted {len(images)} pages")

        return images

    except fitz.FileDataError as e:
        raise PDFProcessingError(f"Invalid or corrupted PDF file: {e}")
    except Exception as e:
        raise PDFProcessingError(f"Failed to process PDF: {e}")


def is_pdf_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a PDF based on file extension

    Args:
        file_path: Path to file

    Returns:
        True if file has .pdf extension (case-insensitive)
    """
    return Path(file_path).suffix.lower() == '.pdf'
