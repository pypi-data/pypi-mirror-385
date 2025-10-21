"""
Document Classifier - Identify document type from markdown content
"""

import re
from typing import Literal

DocumentType = Literal["invoice", "contract", "resume", "general"]


def classify_document(markdown: str) -> DocumentType:
    """
    Classify document type based on content analysis.

    Args:
        markdown: OCR output in markdown format

    Returns:
        str: Document type ("invoice" | "contract" | "resume" | "general")
    """
    text_lower = markdown.lower()

    # Invoice indicators
    invoice_keywords = ["invoice", "receipt", "total", "amount due", "payment", "bill", "subtotal", "tax", "vendor"]
    invoice_score = sum(2 if kw in text_lower else 0 for kw in invoice_keywords)

    # Check for currency symbols (strong invoice indicator)
    if re.search(r'\$\s*\d+|\d+\.\d{2}|€\s*\d+|£\s*\d+', markdown):
        invoice_score += 3

    # Check for invoice number pattern
    if re.search(r'invoice\s*(?:number|#|no\.?)[:\s]*[\w-]+', text_lower):
        invoice_score += 3

    # Contract indicators
    contract_keywords = ["agreement", "contract", "party", "parties", "whereas", "terms and conditions",
                         "effective date", "governing law", "jurisdiction", "hereby", "hereinafter"]
    contract_score = sum(2 if kw in text_lower else 0 for kw in contract_keywords)

    # Strong contract patterns
    if re.search(r'(?:this|the)\s+agreement|between.+and|party\s+[ab]', text_lower):
        contract_score += 4

    # Resume/CV indicators
    resume_keywords = ["experience", "education", "skills", "resume", "cv", "curriculum vitae",
                       "employment history", "qualifications", "objective", "references"]
    resume_score = sum(2 if kw in text_lower else 0 for kw in resume_keywords)

    # Check for date ranges (common in resumes)
    if re.search(r'\d{4}\s*-\s*(?:\d{4}|present)', text_lower):
        resume_score += 2

    # Determine document type based on scores
    scores = {
        "invoice": invoice_score,
        "contract": contract_score,
        "resume": resume_score
    }

    max_score = max(scores.values())
    if max_score >= 3:  # Minimum confidence threshold
        return max(scores, key=scores.get)

    return "general"
