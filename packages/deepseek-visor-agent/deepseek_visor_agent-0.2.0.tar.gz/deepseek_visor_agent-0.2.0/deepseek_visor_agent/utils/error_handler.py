"""
Error handling utilities with automatic fallback support

IMPORTANT: DeepSeek-OCR uses a single model with multiple inference modes.
Fallback changes inference parameters, NOT the model file.
"""

from functools import wraps
import logging
import torch

logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Base exception for OCR-related errors"""
    pass


class OOMError(OCRError):
    """Out of memory error"""
    pass


class ModelLoadError(OCRError):
    """Model loading error"""
    pass


class ImageProcessingError(OCRError):
    """Image processing error"""
    pass


def auto_fallback_decorator(func):
    """
    Automatic fallback decorator: Gundam → Large → Base → Small → Tiny

    If inference fails due to OOM or other errors, automatically
    falls back to a lower-resolution inference mode.

    IMPORTANT: This does NOT reload the model. It only changes the
    inference_mode config, which adjusts base_size/image_size/crop_mode parameters.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # All inference modes in descending order (highest to lowest resolution)
        modes = ["gundam", "large", "base", "small", "tiny"]
        current_mode = self.config.get("inference_mode", "tiny")

        # Start from current mode
        start_idx = modes.index(current_mode) if current_mode in modes else 0

        for mode in modes[start_idx:]:
            try:
                if mode != current_mode:
                    logger.warning(f"Falling back to {mode} inference mode...")
                    # Only change the inference mode, don't reload the model
                    self.config["inference_mode"] = mode

                return func(self, *args, **kwargs)

            except (RuntimeError, torch.cuda.OutOfMemoryError) as e:
                logger.error(f"{mode} inference mode failed: {e}")
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()  # Clear GPU memory
                continue

        raise OCRError(
            "All inference modes failed. Try using CPU mode or reducing image size. "
            "Available modes: tiny (512x512), small (640x640), base (1024x1024), "
            "large (1280x1280), gundam (dynamic with cropping)"
        )

    return wrapper
