"""
DeepSeek Visor Agent - Standard Vision Tool for AI Agents

A production-ready wrapper for DeepSeek-OCR that provides:
- Auto device detection (CUDA/MPS/CPU)
- Automatic model fallback (Gundam -> Base -> Tiny)
- Structured output (Markdown + extracted fields)
- LangChain/LlamaIndex compatible interface
"""

__version__ = "0.1.0"
__author__ = "Jack Chen"
__license__ = "Apache-2.0"

from .tool import VisionDocumentTool
from .device_manager import DeviceManager

__all__ = ["VisionDocumentTool", "DeviceManager"]
