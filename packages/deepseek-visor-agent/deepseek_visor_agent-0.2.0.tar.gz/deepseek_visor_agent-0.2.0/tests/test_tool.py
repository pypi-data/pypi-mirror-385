"""Tests for VisionDocumentTool"""

import pytest
import os
from pathlib import Path
from deepseek_visor_agent import VisionDocumentTool


# Skip model tests in CI environment (no GPU, slow downloads)
skip_model_tests = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Model loading requires GPU and is too slow for CI"
)


@pytest.fixture
def tool():
    """Create tool instance for testing"""
    return VisionDocumentTool(device="cpu", inference_mode="tiny")


@skip_model_tests
def test_tool_initialization():
    """Test tool can be initialized"""
    tool = VisionDocumentTool()
    assert tool is not None
    assert tool.engine is not None
    assert len(tool.parsers) > 0


@skip_model_tests
def test_invoice_extraction(tool):
    """Test invoice field extraction"""
    # TODO: Add test fixtures
    pytest.skip("Requires test invoice image")


@skip_model_tests
def test_auto_classification(tool):
    """Test automatic document classification"""
    # TODO: Add test fixtures
    pytest.skip("Requires test document images")


@skip_model_tests
def test_error_handling(tool):
    """Test error handling with invalid input"""
    with pytest.raises(Exception):
        tool.run("nonexistent_file.jpg")


@skip_model_tests
@pytest.mark.parametrize("document_type", ["invoice", "contract", "general"])
def test_document_types(tool, document_type):
    """Test different document types"""
    # TODO: Add test fixtures
    pytest.skip(f"Requires test {document_type} image")
