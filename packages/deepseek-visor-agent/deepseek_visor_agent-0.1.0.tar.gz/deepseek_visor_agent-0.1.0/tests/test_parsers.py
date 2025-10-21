"""Tests for parser modules"""

import pytest
from deepseek_visor_agent.parsers import BaseParser
from deepseek_visor_agent.parsers.invoice import InvoiceParser
from deepseek_visor_agent.parsers.classifier import classify_document


def test_base_parser_interface():
    """Test BaseParser is abstract"""
    with pytest.raises(TypeError):
        BaseParser()


def test_invoice_parser():
    """Test invoice parser"""
    parser = InvoiceParser()

    # Test markdown with invoice data
    markdown = """
    # Invoice

    Date: 2024-01-15
    Vendor: Acme Corp

    Total: $199.00
    """

    fields = parser.parse(markdown)

    assert "total" in fields
    assert "date" in fields
    assert "vendor" in fields


def test_document_classifier():
    """Test document classification"""

    # Test invoice classification
    invoice_text = "Invoice #12345\nTotal: $199.00\nDate: 2024-01-15"
    assert classify_document(invoice_text) == "invoice"

    # Test contract classification
    contract_text = "Agreement between Party A and Party B\nEffective date: 2024-01-01"
    assert classify_document(contract_text) == "contract"

    # Test general classification
    general_text = "This is some random text without specific keywords"
    result = classify_document(general_text)
    assert result in ["invoice", "contract", "resume", "general"]
