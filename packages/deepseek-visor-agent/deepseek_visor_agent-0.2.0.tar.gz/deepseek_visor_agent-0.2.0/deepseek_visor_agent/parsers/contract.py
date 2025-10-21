"""
Contract Parser - Extract structured data from contract documents
"""

import re
from typing import Dict, Any, List
from .base import BaseParser


class ContractParser(BaseParser):
    """Parser for extracting contract fields from markdown"""

    def parse(self, markdown: str) -> Dict[str, Any]:
        """
        Extract contract fields from markdown.

        Args:
            markdown: OCR output in markdown format

        Returns:
            dict: Extracted fields including parties, effective_date, terms, contract_type
        """
        fields = {
            "parties": self._extract_parties(markdown),
            "effective_date": self._extract_effective_date(markdown),
            "contract_type": self._extract_contract_type(markdown),
            "term_duration": self._extract_term_duration(markdown),
            "governing_law": self._extract_governing_law(markdown),
        }

        return fields

    def _extract_parties(self, text: str) -> List[str]:
        """Extract contract parties"""
        parties = []

        # Pattern 1: "between X and Y" - more flexible ending
        between_pattern = r"(?:between|among)\s+([^,\.]+?)\s+(?:and|&)\s+([^,\.]+?)(?:\s+(?:collectively|hereinafter)|[,\.]|$)"
        match = re.search(between_pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            parties.append(match.group(1).strip())
            parties.append(match.group(2).strip())
            return parties

        # Pattern 2: Explicit "Party A:" and "Party B:"
        party_patterns = [
            r"Party\s+[AB][:\s]+([^\n]+)",
            r"(?:First|Second)\s+Party[:\s]+([^\n]+)",
        ]

        for pattern in party_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                party = match.group(1).strip()
                # Clean up common trailing patterns
                party = re.sub(r'\s*\([^)]*\)\s*$', '', party)  # Remove trailing parentheses
                if party and len(party) > 2:
                    parties.append(party)

        return list(set(parties))  # Remove duplicates

    def _extract_effective_date(self, text: str) -> str:
        """Extract effective date from contract"""
        patterns = [
            r"(?:Effective\s+Date|Commencement\s+Date)[:\s]+(\d{4}-\d{2}-\d{2})",
            r"(?:Effective\s+Date|Commencement\s+Date)[:\s]+(\d{1,2}/\d{1,2}/\d{4})",
            r"(?:Effective\s+Date|Commencement\s+Date)[:\s]+(\d{1,2}\s+\w+\s+\d{4})",
            r"effective\s+(?:as\s+of|from)\s+(\d{1,2}\s+\w+\s+\d{4})",
            r"dated?\s+(?:this\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+day\s+of\s+\w+,?\s+\d{4})",
            r"(?:shall\s+commence\s+on|commences?\s+on)\s+(\w+\s+\d{1,2},?\s+\d{4})",  # "January 15, 2024"
            r"(?:shall\s+commence\s+on|commences?\s+on)\s+(\d{1,2}\s+\w+\s+\d{4})",  # "15 January 2024"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_contract_type(self, text: str) -> str:
        """Extract contract type"""
        # Look for common contract type keywords
        contract_types = {
            "employment": r"employment\s+(?:contract|agreement)",
            "service": r"service\s+(?:contract|agreement)",
            "lease": r"lease\s+agreement",
            "nda": r"non-disclosure\s+agreement|confidentiality\s+agreement",
            "purchase": r"purchase\s+(?:contract|agreement|order)",
            "license": r"license\s+agreement",
            "partnership": r"partnership\s+agreement",
        }

        for contract_type, pattern in contract_types.items():
            if re.search(pattern, text, re.IGNORECASE):
                return contract_type

        # Fallback: look for "AGREEMENT" or "CONTRACT" in first few lines
        lines = text.split('\n')[:5]
        for line in lines:
            line = line.strip().lower()
            if 'agreement' in line or 'contract' in line:
                return line  # Return the full line as contract type

        return "unknown"

    def _extract_term_duration(self, text: str) -> str:
        """Extract contract term/duration"""
        patterns = [
            r"(?:term|duration)[:\s]+(\d+\s+(?:year|month|day)s?)",
            r"(?:for\s+a\s+period\s+of)\s+(\d+\s+(?:year|month|day)s?)",
            r"(?:term|duration)[:\s]+([^\n]+?(?:year|month|day)s?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_governing_law(self, text: str) -> str:
        """Extract governing law/jurisdiction"""
        patterns = [
            r"(?:governed\s+by|subject\s+to)(?:\s+and\s+construed\s+in\s+accordance\s+with)?\s+(?:the\s+)?laws?\s+of\s+(?:the\s+State\s+of\s+)?([^,\.\n]+)",
            r"(?:Governing\s+Law|Jurisdiction)[:\s]+([^,\.\n]+)",
            r"laws?\s+of\s+(?:the\s+State\s+of\s+)?([A-Z][a-zA-Z\s]+?)(?:\.|,|\n|$)",  # Fallback
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result = match.group(1).strip()
                # Clean up common trailing words
                result = re.sub(r'\s*(?:and|or|the|of)\s*$', '', result, flags=re.IGNORECASE)
                return result.strip()

        return ""

    def get_fields_schema(self) -> Dict[str, Any]:
        """Get JSON schema for contract fields"""
        return {
            "type": "object",
            "properties": {
                "parties": {
                    "type": "array",
                    "description": "Contract parties (companies/individuals)"
                },
                "effective_date": {
                    "type": "string",
                    "description": "Contract effective date"
                },
                "contract_type": {
                    "type": "string",
                    "description": "Type of contract (employment, service, NDA, etc.)"
                },
                "term_duration": {
                    "type": "string",
                    "description": "Contract term or duration"
                },
                "governing_law": {
                    "type": "string",
                    "description": "Governing law or jurisdiction"
                }
            }
        }
