"""
Vision Document Tool - Main interface for document OCR and parsing

Provides a unified API for AI agents to extract structured data from documents.
Uses DeepSeek-OCR with automatic inference mode selection.
"""

from typing import Dict, Union, Any, Optional
from pathlib import Path
import logging

from .infer import DeepSeekOCRInference
from .parsers.classifier import classify_document
from .parsers.invoice import InvoiceParser
from .parsers.contract import ContractParser

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
        extract_fields: bool = True
    ) -> Dict[str, Any]:
        """
        Main entry point for document processing.

        Args:
            image_path: Path to the document image
            document_type: "auto" | "invoice" | "contract" | "resume" | "general"
            extract_fields: Whether to extract structured fields

        Returns:
            dict: {
                "markdown": str,           # Markdown representation
                "fields": dict,             # Extracted structured fields
                "confidence": float,        # Confidence score
                "document_type": str,       # Detected or specified type
                "metadata": dict            # Inference metadata
            }
        """
        logger.info(f"Processing document: {image_path}")

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
            "metadata": result["metadata"]
        }

    def __call__(self, image_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Allow tool to be called directly"""
        return self.run(image_path, **kwargs)
