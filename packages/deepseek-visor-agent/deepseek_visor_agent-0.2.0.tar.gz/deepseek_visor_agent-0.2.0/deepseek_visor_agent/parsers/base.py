"""
Base Parser - Abstract class for document parsers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseParser(ABC):
    """Abstract base class for document field parsers"""

    @abstractmethod
    def parse(self, markdown: str) -> Dict[str, Any]:
        """
        Extract structured fields from markdown output.

        Args:
            markdown: OCR output in markdown format

        Returns:
            dict: Extracted fields specific to document type
        """
        pass

    @abstractmethod
    def get_fields_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for the extracted fields.

        Returns:
            dict: JSON schema describing expected fields
        """
        pass

    def get_confidence(self) -> float:
        """
        Get confidence score for the last parse operation.

        Returns:
            float: Confidence score between 0 and 1
        """
        return 1.0  # Default implementation
