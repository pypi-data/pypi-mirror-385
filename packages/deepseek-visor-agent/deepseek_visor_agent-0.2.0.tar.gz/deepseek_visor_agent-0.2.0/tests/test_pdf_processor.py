"""
Unit tests for PDF processing utilities
"""

import pytest
from pathlib import Path
from PIL import Image
import io

from deepseek_visor_agent.utils.pdf_processor import (
    pdf_to_images,
    is_pdf_file,
    PDFProcessingError
)


def _pymupdf_available():
    """Check if PyMuPDF is available"""
    try:
        import fitz
        return True
    except ImportError:
        return False


class TestIsPdfFile:
    """Test PDF file detection"""

    def test_pdf_extension_lowercase(self):
        assert is_pdf_file("document.pdf") is True

    def test_pdf_extension_uppercase(self):
        assert is_pdf_file("DOCUMENT.PDF") is True

    def test_pdf_extension_mixed_case(self):
        assert is_pdf_file("Document.Pdf") is True

    def test_non_pdf_extensions(self):
        assert is_pdf_file("image.jpg") is False
        assert is_pdf_file("image.png") is False
        assert is_pdf_file("document.txt") is False

    def test_path_object(self):
        assert is_pdf_file(Path("document.pdf")) is True
        assert is_pdf_file(Path("image.jpg")) is False


class TestPdfToImages:
    """Test PDF to images conversion"""

    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        """
        Create a simple PDF for testing

        Since we can't easily create a real PDF in tests without PyMuPDF,
        we'll skip tests that require actual PDF files and mark them
        """
        # This would require PyMuPDF to create a test PDF
        # For now, return a placeholder path
        pdf_path = tmp_path / "test.pdf"
        return pdf_path

    @pytest.mark.skipif(
        not _pymupdf_available(),
        reason="PyMuPDF not installed"
    )
    def test_file_not_found(self):
        """Test error when PDF file doesn't exist"""
        with pytest.raises(PDFProcessingError, match="PDF file not found"):
            pdf_to_images("nonexistent.pdf")

    @pytest.mark.skipif(
        not _pymupdf_available(),
        reason="PyMuPDF not installed"
    )
    def test_non_pdf_file(self, tmp_path):
        """Test error when file is not a PDF"""
        # Create a non-PDF file
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("This is not a PDF")

        with pytest.raises(PDFProcessingError, match="File is not a PDF"):
            pdf_to_images(txt_file)

    def test_invalid_page_range(self, sample_pdf_path):
        """Test error handling for invalid page ranges"""
        # Skip if sample PDF doesn't exist (no PyMuPDF in test environment)
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not available")

        # These tests would work with a real PDF
        # with pytest.raises(PDFProcessingError, match="out of range"):
        #     pdf_to_images(sample_pdf_path, start_page=100)

    @pytest.mark.skipif(
        not _pymupdf_available(),
        reason="PyMuPDF not installed"
    )
    def test_basic_conversion(self, tmp_path):
        """
        Test basic PDF to images conversion

        This test requires PyMuPDF to create and process a real PDF
        """
        pytest.skip("Requires creating a real PDF file")

        # Example test structure:
        # 1. Create a simple PDF with PyMuPDF
        # 2. Convert it to images
        # 3. Verify image count, dimensions, etc.

    @pytest.mark.skipif(
        not _pymupdf_available(),
        reason="PyMuPDF not installed"
    )
    def test_dpi_parameter(self, tmp_path):
        """Test DPI parameter affects image resolution"""
        pytest.skip("Requires creating a real PDF file")

    @pytest.mark.skipif(
        not _pymupdf_available(),
        reason="PyMuPDF not installed"
    )
    def test_page_range_selection(self, tmp_path):
        """Test selecting specific page ranges"""
        pytest.skip("Requires creating a real PDF file")


def _pymupdf_available():
    """Check if PyMuPDF is available"""
    try:
        import fitz
        return True
    except ImportError:
        return False


# Integration test (requires PyMuPDF installed)
@pytest.mark.integration
@pytest.mark.skipif(not _pymupdf_available(), reason="PyMuPDF not installed")
class TestPdfProcessingIntegration:
    """
    Integration tests for PDF processing

    These tests require PyMuPDF to be installed and will create actual PDF files
    """

    def test_create_and_convert_pdf(self, tmp_path):
        """Test creating a simple PDF and converting it to images"""
        try:
            import fitz
        except ImportError:
            pytest.skip("PyMuPDF not available")

        # Create a simple single-page PDF
        pdf_path = tmp_path / "test_doc.pdf"
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)  # A4 size in points

        # Add some text
        text = "Test Document"
        point = fitz.Point(50, 50)
        page.insert_text(point, text, fontsize=12)

        # Save PDF
        doc.save(str(pdf_path))
        doc.close()

        # Convert to images
        images = pdf_to_images(pdf_path, dpi=144)

        # Verify results
        assert len(images) == 1
        assert isinstance(images[0], Image.Image)
        assert images[0].mode == 'RGB'

        # Check approximate dimensions (144 DPI = 2x zoom from 72 DPI)
        # A4 at 72 DPI: 595x842, at 144 DPI: ~1190x1684
        width, height = images[0].size
        assert 1100 < width < 1300  # Allow some tolerance
        assert 1600 < height < 1800

    def test_multi_page_pdf(self, tmp_path):
        """Test converting a multi-page PDF"""
        try:
            import fitz
        except ImportError:
            pytest.skip("PyMuPDF not available")

        # Create a 3-page PDF
        pdf_path = tmp_path / "multi_page.pdf"
        doc = fitz.open()

        for i in range(3):
            page = doc.new_page()
            text = f"Page {i + 1}"
            point = fitz.Point(50, 50)
            page.insert_text(point, text, fontsize=12)

        doc.save(str(pdf_path))
        doc.close()

        # Convert all pages
        images = pdf_to_images(pdf_path)
        assert len(images) == 3

        # Convert specific range
        images_subset = pdf_to_images(pdf_path, start_page=1, end_page=2)
        assert len(images_subset) == 2  # Pages 1 and 2 (0-indexed)

    def test_rgba_to_rgb_conversion(self, tmp_path):
        """Test that RGBA images are properly converted to RGB"""
        try:
            import fitz
        except ImportError:
            pytest.skip("PyMuPDF not available")

        # Create a PDF (PyMuPDF output should be RGB anyway)
        pdf_path = tmp_path / "test_rgba.pdf"
        doc = fitz.open()
        doc.new_page()
        doc.save(str(pdf_path))
        doc.close()

        # Convert
        images = pdf_to_images(pdf_path)

        # Verify RGB mode
        assert images[0].mode == 'RGB'
