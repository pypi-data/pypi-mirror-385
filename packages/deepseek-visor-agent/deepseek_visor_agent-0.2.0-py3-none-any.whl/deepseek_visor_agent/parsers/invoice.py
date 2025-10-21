"""
Invoice Parser - Extract structured data from invoice documents
"""

import re
from typing import Dict, Any
from .base import BaseParser


class InvoiceParser(BaseParser):
    """Parser for extracting invoice fields from markdown"""

    def __init__(self):
        """Initialize parser"""
        self._last_fields = {}

    def parse(self, markdown: str) -> Dict[str, Any]:
        """
        Extract invoice fields from markdown.

        Args:
            markdown: OCR output in markdown format

        Returns:
            dict: Extracted fields including total, date, vendor, items
        """
        fields = {
            "total": self._extract_total(markdown),
            "date": self._extract_date(markdown),
            "vendor": self._extract_vendor(markdown),
            "items": self._extract_items(markdown)
        }

        # Store for confidence calculation
        self._last_fields = fields
        return fields

    def _extract_total(self, text: str) -> str:
        """Extract total amount from text"""
        # Patterns in order of priority - Grand Total first to avoid matching Subtotal
        patterns = [
            r"(?:Grand\s+Total)[:\s]+\$?\s*([\d,]+\.?\d*)",  # Grand Total: $199.00 (highest priority)
            r"(?:Amount\s+Due)[:\s]+\$?\s*([\d,]+\.?\d*)",  # Amount Due: $199.00
            r"(?<!Sub)(?:Total)[:\s]+\$?\s*([\d,]+\.?\d*)",  # Total: $199.00 (but not Subtotal)
            r"(?:Grand\s+Total)[:\s]+([€£¥])\s*([\d,]+\.?\d*)",  # Grand Total: €199.00
            r"(?:Amount\s+Due)[:\s]+([€£¥])\s*([\d,]+\.?\d*)",  # Amount Due: €199.00
            r"(?<!Sub)(?:Total)[:\s]+([€£¥])\s*([\d,]+\.?\d*)",  # Total: €199.00 (but not Subtotal)
            r"\$\s*([\d,]+\.\d{2})\s*(?:\n|$)",  # $199.00 at end of line
            r"(?:USD|EUR|GBP)\s*\$?\s*([\d,]+\.?\d*)",  # USD 199.00
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                amount = match.group(1) if len(match.groups()) == 1 else match.group(2)
                # Remove commas from amount
                amount = amount.replace(',', '')
                return f"${amount}"

        return ""

    def _extract_date(self, text: str) -> str:
        """Extract date from text"""
        # Patterns in order of priority
        patterns = [
            r"(?:Invoice\s+)?Date[:\s]+(\d{4}-\d{2}-\d{2})",  # Date: 2024-01-15
            r"(?:Invoice\s+)?Date[:\s]+(\d{1,2}/\d{1,2}/\d{4})",  # Date: 01/15/2024
            r"(?:Invoice\s+)?Date[:\s]+(\d{1,2}-\d{1,2}-\d{4})",  # Date: 01-15-2024
            r"(?:Invoice\s+)?Date[:\s]+(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})",  # Date: 15 Jan 2024
            r"(\d{4}-\d{2}-\d{2})",  # Standalone: 2024-01-15
            r"(\d{1,2}/\d{1,2}/\d{4})",  # Standalone: 01/15/2024
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return ""

    def _extract_vendor(self, text: str) -> str:
        """Extract vendor name from text"""
        # Try explicit patterns first
        vendor_patterns = [
            r"(?:Vendor|From|Company|Business)[:\s]+([^\n]+)",
            r"(?:Bill\s+From|Billed\s+By)[:\s]+([^\n]+)",
        ]

        for pattern in vendor_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vendor = match.group(1).strip()
                # Clean up common suffixes (Inc., LLC, Ltd., Corporation - NOT "Corp" alone)
                vendor = re.sub(r'\s*(?:Inc\.?|LLC|Ltd\.?|Corporation|Corp\.)$', '', vendor, flags=re.IGNORECASE)
                return vendor.strip()

        # Fallback: Find first meaningful line (not invoice/date/total)
        # Only use this if we're confident it's an invoice context
        lines = text.split('\n')
        skip_keywords = ['invoice', 'receipt', 'date', 'total', 'number', '#', 'qty', 'quantity', 'price', 'amount', 'random', 'text']

        # Only use fallback if there are invoice-like keywords in the text
        has_invoice_context = any(kw in text.lower() for kw in ['invoice', 'receipt', 'bill', 'payment'])
        if not has_invoice_context:
            return ""

        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            # Skip empty lines, headers, and lines with keywords
            if not line or len(line) < 3:
                continue
            if any(kw in line.lower() for kw in skip_keywords):
                continue
            # Skip lines that look like dates or amounts
            if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', line):
                continue
            if re.search(r'\$\s*[\d,]+', line):
                continue

            # This looks like a vendor name
            return line

        return ""

    def _extract_items(self, text: str) -> list:
        """Extract line items from text (placeholder implementation)"""
        # TODO: Implement line item extraction
        return []

    def get_confidence(self) -> float:
        """
        Calculate confidence score based on extracted fields.

        Returns:
            float: Confidence score between 0 and 1
        """
        if not hasattr(self, '_last_fields') or not self._last_fields:
            return 0.0

        # Count non-empty required fields
        required_fields = ["total", "date", "vendor"]
        filled_fields = sum(1 for field in required_fields if self._last_fields.get(field))

        # Calculate confidence: 0.33 per required field
        confidence = filled_fields / len(required_fields)

        return confidence

    def get_fields_schema(self) -> Dict[str, Any]:
        """Get JSON schema for invoice fields"""
        return {
            "type": "object",
            "properties": {
                "total": {"type": "string", "description": "Total amount"},
                "date": {"type": "string", "description": "Invoice date"},
                "vendor": {"type": "string", "description": "Vendor name"},
                "items": {"type": "array", "description": "Line items"}
            }
        }
