"""
Vision Document Tool - Main interface for document OCR and parsing

Provides a unified API for AI agents to extract structured data from documents.
Uses DeepSeek-OCR with automatic inference mode selection.
Supports both images and PDF files.
"""

from typing import Dict, Union, Any, Optional, List
from pathlib import Path
import logging

from .infer import DeepSeekOCRInference
from .parsers.classifier import classify_document
from .parsers.invoice import InvoiceParser
from .parsers.contract import ContractParser
from .utils.pdf_processor import pdf_to_images, is_pdf_file, PDFProcessingError

logger = logging.getLogger(__name__)


class VisionDocumentTool:
    """
    Unified tool interface for document understanding.

    Compatible with LangChain, LlamaIndex, and other AI agent frameworks.
    """

    def __init__(
        self,
        inference_mode: str = "auto",
        device: str = "auto"
    ):
        """
        Initialize the Vision Document Tool.

        Args:
            inference_mode: "auto" | "tiny" | "small" | "base" | "large" | "gundam"
                - auto: Automatically select based on available GPU memory
                - tiny: 512x512 resolution (CPU compatible)
                - small: 640x640 resolution
                - base: 1024x1024 resolution
                - large: 1280x1280 resolution
                - gundam: Dynamic resolution with cropping
            device: "auto" | "cuda" | "mps" | "cpu"
        """
        self.engine = DeepSeekOCRInference(inference_mode, device)

        # Initialize parsers
        self.parsers = {
            "invoice": InvoiceParser(),
            "contract": ContractParser(),
        }

        logger.info("VisionDocumentTool initialized")

    def run(
        self,
        image_path: Union[str, Path],
        document_type: str = "auto",
        extract_fields: bool = True,
        pdf_dpi: int = 144,
        pdf_start_page: Optional[int] = None,
        pdf_end_page: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for document processing.

        Supports both image files (.jpg, .png, etc.) and PDF files.
        For PDFs, each page is processed separately and results are combined.

        Args:
            image_path: Path to the document image or PDF file
            document_type: "auto" | "invoice" | "contract" | "resume" | "general"
            extract_fields: Whether to extract structured fields
            pdf_dpi: DPI for PDF rendering (default: 144, same as DeepSeek-OCR official)
            pdf_start_page: First page to process for PDFs (0-indexed), None for first page
            pdf_end_page: Last page to process for PDFs (0-indexed), None for last page

        Returns:
            dict: {
                "markdown": str,           # Markdown representation (multi-page PDFs joined with separators)
                "fields": dict,             # Extracted structured fields (merged from all pages)
                "confidence": float,        # Average confidence score
                "document_type": str,       # Detected or specified type
                "metadata": dict,           # Inference metadata
                "pages": int                # Number of pages processed (1 for images, N for PDFs)
            }

        Raises:
            PDFProcessingError: If PDF processing fails
            ImageProcessingError: If image processing fails
        """
        image_path = Path(image_path)
        logger.info(f"Processing document: {image_path}")

        # Check if input is a PDF file
        if is_pdf_file(image_path):
            return self._process_pdf(
                image_path,
                document_type=document_type,
                extract_fields=extract_fields,
                dpi=pdf_dpi,
                start_page=pdf_start_page,
                end_page=pdf_end_page
            )
        else:
            return self._process_image(
                image_path,
                document_type=document_type,
                extract_fields=extract_fields
            )

    def _process_image(
        self,
        image_path: Path,
        document_type: str = "auto",
        extract_fields: bool = True
    ) -> Dict[str, Any]:
        """Process a single image file"""
        # 1. Run OCR inference
        result = self.engine.infer(image_path)
        markdown = result["markdown"]

        # 2. Classify document type if needed
        if document_type == "auto":
            document_type = classify_document(markdown)
            logger.info(f"Detected document type: {document_type}")

        # 3. Extract structured fields
        fields = {}
        confidence = 1.0

        if extract_fields and document_type in self.parsers:
            parser = self.parsers[document_type]
            fields = parser.parse(markdown)
            confidence = parser.get_confidence()
            logger.info(f"Extracted {len(fields)} fields")

        return {
            "markdown": markdown,
            "fields": fields,
            "confidence": confidence,
            "document_type": document_type,
            "metadata": result["metadata"],
            "pages": 1
        }

    def _process_pdf(
        self,
        pdf_path: Path,
        document_type: str = "auto",
        extract_fields: bool = True,
        dpi: int = 144,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a PDF file by converting pages to images and processing each

        Based on DeepSeek-OCR official PDF processing:
        https://github.com/deepseek-ai/DeepSeek-OCR/blob/master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py
        """
        logger.info(f"Processing PDF: {pdf_path} (DPI: {dpi})")

        # Convert PDF to images
        try:
            images = pdf_to_images(
                pdf_path,
                dpi=dpi,
                start_page=start_page,
                end_page=end_page
            )
        except PDFProcessingError as e:
            logger.error(f"PDF processing failed: {e}")
            raise

        logger.info(f"Processing {len(images)} pages from PDF")

        # Process each page
        page_results = []
        for page_num, image in enumerate(images):
            logger.debug(f"Processing page {page_num + 1}/{len(images)}")

            # Run OCR on this page's image
            result = self.engine.infer(image)
            page_results.append(result)

        # Combine results from all pages
        # Join markdown with page separators (same as DeepSeek-OCR official)
        page_separator = "\n\n<--- Page Split --->\n\n"
        combined_markdown = page_separator.join([r["markdown"] for r in page_results])

        # Classify document type from first page (or combined text)
        if document_type == "auto":
            document_type = classify_document(page_results[0]["markdown"])
            logger.info(f"Detected document type: {document_type}")

        # Extract fields from combined markdown
        fields = {}
        confidence = 1.0

        if extract_fields and document_type in self.parsers:
            parser = self.parsers[document_type]
            # For multi-page PDFs, parse the combined markdown
            fields = parser.parse(combined_markdown)
            confidence = parser.get_confidence()
            logger.info(f"Extracted {len(fields)} fields from {len(images)} pages")

        # Combine metadata (use average inference time, first page's device info)
        combined_metadata = page_results[0]["metadata"].copy()
        avg_inference_time = sum(r["metadata"]["inference_time_ms"] for r in page_results) / len(page_results)
        combined_metadata["inference_time_ms"] = int(avg_inference_time)
        combined_metadata["total_inference_time_ms"] = sum(r["metadata"]["inference_time_ms"] for r in page_results)

        return {
            "markdown": combined_markdown,
            "fields": fields,
            "confidence": confidence,
            "document_type": document_type,
            "metadata": combined_metadata,
            "pages": len(images)
        }

    def __call__(self, image_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Allow tool to be called directly"""
        return self.run(image_path, **kwargs)
