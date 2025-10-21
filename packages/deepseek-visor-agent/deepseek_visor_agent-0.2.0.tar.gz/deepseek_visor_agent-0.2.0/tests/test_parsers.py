"""Tests for parser modules"""

import pytest
from deepseek_visor_agent.parsers import BaseParser
from deepseek_visor_agent.parsers.invoice import InvoiceParser
from deepseek_visor_agent.parsers.contract import ContractParser
from deepseek_visor_agent.parsers.classifier import classify_document


def test_base_parser_interface():
    """Test BaseParser is abstract"""
    with pytest.raises(TypeError):
        BaseParser()


class TestInvoiceParser:
    """Comprehensive tests for InvoiceParser"""

    def test_basic_invoice_parsing(self):
        """Test basic invoice data extraction"""
        parser = InvoiceParser()

        markdown = """
        # Invoice

        Date: 2024-01-15
        Vendor: Acme Corp

        Total: $199.00
        """

        fields = parser.parse(markdown)

        assert fields["total"] == "$199.00"
        assert fields["date"] == "2024-01-15"
        assert fields["vendor"] == "Acme Corp"

    def test_total_extraction_formats(self):
        """Test different total amount formats"""
        parser = InvoiceParser()

        test_cases = [
            ("Total: $199.00", "$199.00"),
            ("Grand Total: $1,234.56", "$1234.56"),  # Commas removed
            ("Amount Due: $99", "$99"),
            ("Total: €199.00", "$199.00"),  # Euro sign
            ("Total: £50.25", "$50.25"),  # Pound sign
            ("Total: ¥1000", "$1000"),  # Yen sign
            ("USD 199.00", "$199.00"),
            ("EUR 150", "$150"),
            ("$99.99", "$99.99"),  # Standalone amount
        ]

        for text, expected in test_cases:
            total = parser._extract_total(text)
            assert total == expected, f"Failed for: {text}"

    def test_date_extraction_formats(self):
        """Test different date formats"""
        parser = InvoiceParser()

        test_cases = [
            ("Date: 2024-01-15", "2024-01-15"),
            ("Date: 01/15/2024", "01/15/2024"),
            ("Date: 01-15-2024", "01-15-2024"),
            ("Date: 15 Jan 2024", "15 Jan 2024"),
            ("Date: 15 January 2024", "15 January 2024"),
            ("Invoice Date: 2024-12-31", "2024-12-31"),
            ("2024-01-15", "2024-01-15"),  # Standalone
            ("12/25/2024", "12/25/2024"),  # Standalone
        ]

        for text, expected in test_cases:
            date = parser._extract_date(text)
            assert date == expected, f"Failed for: {text}"

    def test_vendor_extraction(self):
        """Test vendor name extraction"""
        parser = InvoiceParser()

        test_cases = [
            ("Vendor: Acme Corp", "Acme Corp"),
            ("From: Tech Solutions Inc.", "Tech Solutions"),  # Inc. removed
            ("Company: Global Ltd.", "Global"),  # Ltd. removed
            ("Bill From: Services LLC", "Services"),  # LLC removed
            ("Billed By: Consulting Corporation", "Consulting"),  # Corporation removed
        ]

        for text, expected in test_cases:
            vendor = parser._extract_vendor(text)
            assert vendor == expected, f"Failed for: {text}"

    def test_vendor_fallback_extraction(self):
        """Test vendor extraction from first meaningful line"""
        parser = InvoiceParser()

        # No explicit vendor field, should extract from first meaningful line
        markdown = """
        Invoice #12345

        Acme Corporation
        123 Main Street

        Date: 2024-01-15
        Total: $199.00
        """

        vendor = parser._extract_vendor(markdown)
        assert vendor == "Acme Corporation"

    def test_empty_fields(self):
        """Test parser handles missing data gracefully"""
        parser = InvoiceParser()

        markdown = "Random text without invoice data"
        fields = parser.parse(markdown)

        assert fields["total"] == ""
        assert fields["date"] == ""
        assert fields["vendor"] == ""
        assert fields["items"] == []

    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        parser = InvoiceParser()

        # Complete invoice
        complete_markdown = """
        Vendor: Acme Corp
        Date: 2024-01-15
        Total: $199.00
        """
        parser.parse(complete_markdown)
        assert parser.get_confidence() == 1.0  # All 3 required fields present

        # Incomplete invoice (missing vendor)
        incomplete_markdown = """
        Date: 2024-01-15
        Total: $199.00
        """
        parser.parse(incomplete_markdown)
        confidence = parser.get_confidence()
        assert 0.6 < confidence < 0.7  # 2/3 fields = 0.67

        # No fields
        parser.parse("Some random text")
        assert parser.get_confidence() == 0.0

    def test_fields_schema(self):
        """Test JSON schema generation"""
        parser = InvoiceParser()
        schema = parser.get_fields_schema()

        assert schema["type"] == "object"
        assert "total" in schema["properties"]
        assert "date" in schema["properties"]
        assert "vendor" in schema["properties"]
        assert "items" in schema["properties"]

    def test_multi_currency_support(self):
        """Test parsing invoices with different currencies"""
        parser = InvoiceParser()

        currencies = ["$", "€", "£", "¥"]
        for symbol in currencies:
            markdown = f"Total: {symbol}100.00"
            fields = parser.parse(markdown)
            # All should normalize to $ format
            assert fields["total"].startswith("$")

    def test_complex_invoice_example(self):
        """Test parsing a realistic complex invoice"""
        parser = InvoiceParser()

        markdown = """
        # INVOICE

        ABC Technology Solutions Inc.
        456 Tech Avenue, Suite 100
        San Francisco, CA 94105

        Invoice #: INV-2024-001
        Invoice Date: 2024-01-15

        Bill To:
        XYZ Corporation

        | Item | Quantity | Price | Amount |
        |------|----------|-------|---------|
        | Consulting | 10 hrs | $150 | $1,500 |
        | Development | 20 hrs | $200 | $4,000 |

        Subtotal: $5,500.00
        Tax (10%): $550.00
        Grand Total: $6,050.00

        Payment Due: 2024-02-15
        """

        fields = parser.parse(markdown)

        # Vendor should have Inc. removed by the regex
        assert "ABC Technology Solutions" in fields["vendor"]
        assert fields["date"] == "2024-01-15"
        # Should extract Grand Total, not Subtotal
        assert "$6,050" in fields["total"] or "$6050" in fields["total"]


class TestContractParser:
    """Comprehensive tests for ContractParser"""

    def test_basic_contract_parsing(self):
        """Test basic contract data extraction"""
        parser = ContractParser()

        markdown = """
        # Service Agreement

        This agreement is between Acme Corp and Tech Solutions
        Effective Date: 2024-01-15
        Term: 12 months
        Governed by the laws of California
        """

        fields = parser.parse(markdown)

        assert len(fields["parties"]) == 2
        assert "Acme Corp" in fields["parties"]
        assert "Tech Solutions" in fields["parties"]
        assert fields["effective_date"] == "2024-01-15"
        assert fields["contract_type"] == "service"
        assert "12 months" in fields["term_duration"]
        assert "California" in fields["governing_law"]

    def test_parties_extraction_patterns(self):
        """Test different party extraction patterns"""
        parser = ContractParser()

        test_cases = [
            ("between Company A and Company B", ["Company A", "Company B"]),
            ("between Alice Smith & Bob Jones", ["Alice Smith", "Bob Jones"]),
            ("Party A: Corporation One\nParty B: Corporation Two",
             ["Corporation One", "Corporation Two"]),
            ("First Party: ABC Inc\nSecond Party: XYZ Ltd", ["ABC Inc", "XYZ Ltd"]),
        ]

        for text, expected_parties in test_cases:
            parties = parser._extract_parties(text)
            assert len(parties) >= 2, f"Failed for: {text}"
            for expected in expected_parties:
                assert any(expected in party for party in parties), \
                    f"Expected '{expected}' not found in {parties}"

    def test_effective_date_formats(self):
        """Test different effective date formats"""
        parser = ContractParser()

        test_cases = [
            ("Effective Date: 2024-01-15", "2024-01-15"),
            ("Effective Date: 01/15/2024", "01/15/2024"),
            ("Commencement Date: 15 January 2024", "15 January 2024"),
            ("effective as of 1 March 2024", "1 March 2024"),
            ("dated this 15th day of January, 2024", "15th day of January, 2024"),
        ]

        for text, expected in test_cases:
            date = parser._extract_effective_date(text)
            assert expected in date, f"Failed for: {text}, got: {date}"

    def test_contract_type_detection(self):
        """Test contract type identification"""
        parser = ContractParser()

        test_cases = [
            ("Employment Contract", "employment"),
            ("Service Agreement between...", "service"),
            ("Lease Agreement for property", "lease"),
            ("Non-Disclosure Agreement", "nda"),
            ("Confidentiality Agreement", "nda"),
            ("Purchase Order #12345", "purchase"),
            ("License Agreement for software", "license"),
            ("Partnership Agreement", "partnership"),
        ]

        for text, expected_type in test_cases:
            contract_type = parser._extract_contract_type(text)
            assert contract_type == expected_type, \
                f"Failed for: {text}, got: {contract_type}"

    def test_term_duration_extraction(self):
        """Test contract term/duration extraction"""
        parser = ContractParser()

        test_cases = [
            ("Term: 12 months", "12 months"),
            ("Duration: 2 years", "2 years"),
            ("for a period of 90 days", "90 days"),
            ("Term: 1 year from the effective date", "1 year"),
        ]

        for text, expected in test_cases:
            duration = parser._extract_term_duration(text)
            assert expected in duration, f"Failed for: {text}"

    def test_governing_law_extraction(self):
        """Test governing law extraction"""
        parser = ContractParser()

        test_cases = [
            ("governed by the laws of California", "California"),
            ("subject to laws of New York", "New York"),
            ("Governing Law: Delaware", "Delaware"),
            ("Jurisdiction: United Kingdom", "United Kingdom"),
        ]

        for text, expected in test_cases:
            law = parser._extract_governing_law(text)
            assert expected in law, f"Failed for: {text}"

    def test_empty_fields(self):
        """Test parser handles missing data gracefully"""
        parser = ContractParser()

        markdown = "Random text without contract data"
        fields = parser.parse(markdown)

        assert fields["parties"] == []
        assert fields["effective_date"] == ""
        assert fields["term_duration"] == ""
        assert fields["governing_law"] == ""

    def test_complex_contract_example(self):
        """Test parsing a realistic complex contract"""
        parser = ContractParser()

        markdown = """
        # SOFTWARE LICENSE AGREEMENT

        This License Agreement ("Agreement") is entered into as of
        the 15th day of January, 2024, between:

        Party A: TechCorp International Inc., a Delaware corporation
        Party B: SoftwareSolutions LLC, a California limited liability company

        WHEREAS, the parties wish to enter into a software licensing arrangement.

        1. EFFECTIVE DATE
        This Agreement shall commence on January 15, 2024.

        2. TERM
        The initial term of this Agreement shall be for a period of 3 years.

        3. GOVERNING LAW
        This Agreement shall be governed by and construed in accordance with
        the laws of the State of California.
        """

        fields = parser.parse(markdown)

        assert len(fields["parties"]) >= 2
        assert "TechCorp" in str(fields["parties"])
        assert "SoftwareSolutions" in str(fields["parties"])
        assert "2024" in fields["effective_date"]
        assert fields["contract_type"] == "license"
        assert "3 years" in fields["term_duration"]
        assert "California" in fields["governing_law"]

    def test_fields_schema(self):
        """Test JSON schema generation"""
        parser = ContractParser()
        schema = parser.get_fields_schema()

        assert schema["type"] == "object"
        assert "parties" in schema["properties"]
        assert "effective_date" in schema["properties"]
        assert "contract_type" in schema["properties"]
        assert "term_duration" in schema["properties"]
        assert "governing_law" in schema["properties"]


class TestDocumentClassifier:
    """Comprehensive tests for document classifier"""

    def test_invoice_classification(self):
        """Test invoice document classification"""
        test_cases = [
            "Invoice #12345\nTotal: $199.00",
            "INVOICE\nDate: 2024-01-15\nAmount Due: $500",
            "Bill To: Customer\nTotal Amount: $1,000",
        ]

        for text in test_cases:
            assert classify_document(text) == "invoice", f"Failed for: {text[:50]}"

    def test_contract_classification(self):
        """Test contract document classification"""
        test_cases = [
            "Agreement between Party A and Party B",  # Has "between...and"
            "This Agreement is entered into",  # Has "agreement"
            "Employment Agreement\nEffective Date: 2024-01-01\nParty A:",  # Multiple keywords
            "Service Level Agreement (SLA)\nParties hereby agree",  # Multiple keywords
        ]

        for text in test_cases:
            result = classify_document(text)
            assert result == "contract", f"Failed for: {text[:50]}, got: {result}"

    def test_resume_classification(self):
        """Test resume document classification"""
        test_cases = [
            "RESUME\nJohn Doe\nEducation:\nExperience:",
            "Curriculum Vitae\nSkills:",
            "Work Experience:\n2020-2024: Software Engineer",
        ]

        for text in test_cases:
            assert classify_document(text) == "resume", f"Failed for: {text[:50]}"

    def test_general_classification(self):
        """Test general document classification (fallback)"""
        test_cases = [
            "This is a random document",
            "Lorem ipsum dolor sit amet",
            "Meeting notes from 2024-01-15",
        ]

        for text in test_cases:
            result = classify_document(text)
            assert result == "general", f"Failed for: {text[:50]}, got: {result}"

    def test_mixed_keywords(self):
        """Test classification with mixed keywords"""
        # Invoice keywords should have higher weight
        invoice_heavy = "Invoice #123 for services\nTotal: $500\nVendor: ACME"
        assert classify_document(invoice_heavy) == "invoice"

        # Contract keywords should win
        contract_heavy = "Service Agreement\nParties: A and B\nEffective Date: 2024-01-01\nAmount mentioned: $500"
        assert classify_document(contract_heavy) == "contract"

    def test_case_insensitive(self):
        """Test classification is case-insensitive"""
        test_cases = [
            ("INVOICE #123\nTotal: $100", "invoice"),
            ("Agreement between parties\nEffective Date: 2024-01-01", "contract"),
            ("CURRICULUM VITAE\nEducation:\nExperience:\n2020-2024", "resume"),
        ]

        for text, expected in test_cases:
            result = classify_document(text)
            assert result == expected, f"Failed for: {text[:30]}, expected: {expected}, got: {result}"
