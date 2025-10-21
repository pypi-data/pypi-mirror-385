"""
Device Manager - Automatic device detection and inference mode selection

Detects optimal configuration based on available hardware and selects
the appropriate inference mode (Tiny/Small/Base/Large/Gundam) for DeepSeek-OCR.

IMPORTANT: DeepSeek-OCR is a SINGLE model with multiple inference modes,
not multiple model variants. The modes control resolution and cropping strategies.

Based on: https://huggingface.co/deepseek-ai/DeepSeek-OCR
"""

import torch
import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Inference mode configurations for DeepSeek-OCR
# Reference: https://huggingface.co/deepseek-ai/DeepSeek-OCR
INFERENCE_MODES = {
    "tiny": {
        "base_size": 512,
        "image_size": 512,
        "crop_mode": False,
        "min_vram_gb": 4,
        "description": "Lowest resolution (512x512), CPU compatible"
    },
    "small": {
        "base_size": 640,
        "image_size": 640,
        "crop_mode": False,
        "min_vram_gb": 8,
        "description": "Small resolution (640x640), entry-level GPU"
    },
    "base": {
        "base_size": 1024,
        "image_size": 1024,
        "crop_mode": False,
        "min_vram_gb": 16,
        "description": "Standard resolution (1024x1024), mid-range GPU"
    },
    "large": {
        "base_size": 1280,
        "image_size": 1280,
        "crop_mode": False,
        "min_vram_gb": 24,
        "description": "High resolution (1280x1280), high-end GPU"
    },
    "gundam": {
        "base_size": 1024,
        "image_size": 640,
        "crop_mode": True,
        "min_vram_gb": 48,
        "description": "Dynamic resolution with cropping (n×640×640 + 1×1024×1024)"
    }
}


class DeviceManager:
    """Automatic device detection and optimal inference mode selection"""

    @staticmethod
    def detect_optimal_config() -> Dict[str, Any]:
        """
        Detect the optimal configuration based on available hardware.

        Returns:
            dict: Configuration with keys:
                - device: "cuda" | "mps" | "cpu"
                - inference_mode: "tiny" | "small" | "base" | "large" | "gundam"
                - use_flash_attn: bool
                - max_memory_gb: float
        """
        config = {
            "device": "cpu",
            "inference_mode": "tiny",
            "use_flash_attn": False,
            "max_memory_gb": 0
        }

        # 1. Check for CUDA
        if torch.cuda.is_available():
            config["device"] = "cuda"
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            config["max_memory_gb"] = gpu_memory

            # Select inference mode based on GPU memory
            config["inference_mode"] = DeviceManager._select_inference_mode(gpu_memory)

            logger.info(
                f"CUDA detected: {torch.cuda.get_device_name(0)} "
                f"({gpu_memory:.1f}GB) - Using {config['inference_mode']} mode"
            )

            # Check for FlashAttention
            try:
                import flash_attn
                config["use_flash_attn"] = True
                logger.info("FlashAttention detected and enabled")
            except ImportError:
                logger.warning("FlashAttention not available, using standard attention")

        # 2. Check for Apple Silicon MPS
        elif torch.backends.mps.is_available():
            config["device"] = "mps"
            config["inference_mode"] = "small"  # MPS recommended to use Small mode
            config["max_memory_gb"] = psutil.virtual_memory().available / 1e9
            logger.info(
                f"Apple MPS detected, using {config['inference_mode']} mode "
                f"(Available memory: {config['max_memory_gb']:.1f}GB)"
            )

        # 3. CPU fallback
        else:
            config["max_memory_gb"] = psutil.virtual_memory().available / 1e9
            logger.info(
                f"No GPU detected, using CPU with {config['inference_mode']} mode "
                f"(Available memory: {config['max_memory_gb']:.1f}GB)"
            )

        return config

    @staticmethod
    def _select_inference_mode(gpu_memory_gb: float) -> str:
        """
        Select optimal inference mode based on available GPU memory.

        Args:
            gpu_memory_gb: Available GPU memory in GB

        Returns:
            str: Inference mode name
        """
        # Check from highest to lowest requirement
        for mode in ["gundam", "large", "base", "small", "tiny"]:
            if gpu_memory_gb >= INFERENCE_MODES[mode]["min_vram_gb"]:
                return mode

        # Fallback to tiny if memory is very low
        return "tiny"

    @staticmethod
    def get_mode_params(mode: str) -> Dict[str, Any]:
        """
        Get inference parameters for a specific mode.

        Args:
            mode: Inference mode name

        Returns:
            dict: Inference parameters (base_size, image_size, crop_mode)
        """
        if mode not in INFERENCE_MODES:
            logger.warning(f"Unknown mode '{mode}', falling back to 'tiny'")
            mode = "tiny"

        return INFERENCE_MODES[mode]

    @staticmethod
    def get_device_info() -> str:
        """Get human-readable device information"""
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            return f"CUDA: {gpu_name} ({gpu_memory:.1f}GB)"
        elif torch.backends.mps.is_available():
            return "Apple Silicon MPS"
        else:
            return "CPU"

    @staticmethod
    def list_available_modes() -> Dict[str, Dict[str, Any]]:
        """List all available inference modes and their requirements"""
        return INFERENCE_MODES.copy()
