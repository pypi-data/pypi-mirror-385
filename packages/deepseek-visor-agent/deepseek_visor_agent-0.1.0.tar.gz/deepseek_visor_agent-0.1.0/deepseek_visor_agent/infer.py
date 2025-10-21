"""
Inference Engine - Wrapper for DeepSeek-OCR model inference

IMPORTANT: DeepSeek-OCR is a SINGLE model that supports multiple inference modes.
This class loads the model once and adjusts inference parameters based on the selected mode.

Based on: https://huggingface.co/deepseek-ai/DeepSeek-OCR
"""

from typing import Dict, Union, Any
from pathlib import Path
import time
import logging
import torch

from .device_manager import DeviceManager, INFERENCE_MODES
from .utils.error_handler import auto_fallback_decorator, ModelLoadError

logger = logging.getLogger(__name__)

# Fixed model ID - DeepSeek-OCR has only one model
MODEL_ID = "deepseek-ai/DeepSeek-OCR"


class DeepSeekOCRInference:
    """DeepSeek-OCR inference engine with automatic device and mode management"""

    def __init__(self, inference_mode: str = "auto", device: str = "auto"):
        """
        Initialize the inference engine.

        Args:
            inference_mode: "auto" | "tiny" | "small" | "base" | "large" | "gundam"
            device: "auto" | "cuda" | "mps" | "cpu"
        """
        self.config = DeviceManager.detect_optimal_config()

        # Override auto-detected settings if specified
        if inference_mode != "auto":
            if inference_mode in INFERENCE_MODES:
                self.config["inference_mode"] = inference_mode
            else:
                logger.warning(
                    f"Unknown inference mode '{inference_mode}', using auto-detected "
                    f"mode '{self.config['inference_mode']}'"
                )

        if device != "auto":
            self.config["device"] = device

        logger.info(f"Initializing with config: {self.config}")

        self.model = None
        self.tokenizer = None

        # Lazy loading - model will be loaded on first inference call
        self._initialized = False

    def _load_model(self):
        """Load the DeepSeek-OCR model (single model for all modes)"""
        try:
            from transformers import AutoModel  # Use AutoModel not AutoModelForCausalLM

            logger.info(f"Loading DeepSeek-OCR model from {MODEL_ID}")
            logger.info("First-time download may take several minutes (~14GB)")

            load_kwargs = {
                "trust_remote_code": True,
                "use_safetensors": True,
            }

            if self.config["use_flash_attn"]:
                load_kwargs["_attn_implementation"] = "flash_attention_2"
                logger.info("Using FlashAttention 2 for faster inference")

            model = AutoModel.from_pretrained(MODEL_ID, **load_kwargs)

            # Move to device and set dtype
            if self.config["device"] == "cuda":
                model = model.cuda().to(torch.bfloat16)
            elif self.config["device"] == "mps":
                model = model.to("mps").to(torch.float32)  # MPS doesn't support bfloat16
            else:
                model = model.to(torch.float32)

            model = model.eval()
            logger.info("Model loaded successfully")

            return model

        except Exception as e:
            raise ModelLoadError(f"Failed to load model from {MODEL_ID}: {e}")

    def _load_tokenizer(self):
        """Load the tokenizer"""
        try:
            from transformers import AutoTokenizer

            logger.info(f"Loading tokenizer from {MODEL_ID}")
            return AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

        except Exception as e:
            raise ModelLoadError(f"Failed to load tokenizer from {MODEL_ID}: {e}")

    def _ensure_initialized(self):
        """Ensure model and tokenizer are loaded"""
        if not self._initialized:
            self.model = self._load_model()
            self.tokenizer = self._load_tokenizer()
            self._initialized = True

    def _get_mode_params(self) -> Dict[str, Any]:
        """Get inference parameters for current mode"""
        mode = self.config["inference_mode"]
        return DeviceManager.get_mode_params(mode)

    @auto_fallback_decorator
    def infer(
        self,
        image_path: Union[str, Path],
        prompt: str = "<image>\n<|grounding|>Convert the document to markdown.",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run OCR inference on an image.

        Args:
            image_path: Path to the image file
            prompt: Prompt template for the model
            **kwargs: Additional arguments passed to model.infer()

        Returns:
            dict: {
                "markdown": str,
                "raw_output": str,
                "metadata": {
                    "model": str (always "DeepSeek-OCR"),
                    "inference_mode": str,
                    "device": str,
                    "inference_time_ms": int
                }
            }
        """
        self._ensure_initialized()

        start_time = time.time()

        # Get inference parameters for current mode
        mode_params = self._get_mode_params()

        # Run inference with mode-specific parameters
        # Based on official API: model.infer(tokenizer, prompt, image_file, base_size, image_size, crop_mode, ...)
        logger.info(
            f"Running inference in {self.config['inference_mode']} mode "
            f"(base_size={mode_params['base_size']}, "
            f"image_size={mode_params['image_size']}, "
            f"crop_mode={mode_params['crop_mode']})"
        )

        # Convert Path to string for compatibility
        image_path_str = str(image_path)

        # Create a temporary output directory if needed
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            output = self.model.infer(
                self.tokenizer,
                prompt=prompt,
                image_file=image_path_str,
                base_size=mode_params["base_size"],
                image_size=mode_params["image_size"],
                crop_mode=mode_params["crop_mode"],
                output_path=temp_dir,  # Temporary directory for any output files
                save_results=False,  # Don't save to disk by default
                test_compress=False,  # Don't test compression
                **kwargs
            )

        inference_time = int((time.time() - start_time) * 1000)

        logger.info(f"Inference completed in {inference_time}ms")

        return {
            "markdown": output,
            "raw_output": output,
            "metadata": {
                "model": "DeepSeek-OCR",
                "inference_mode": self.config["inference_mode"],
                "device": self.config["device"],
                "inference_time_ms": inference_time
            }
        }
