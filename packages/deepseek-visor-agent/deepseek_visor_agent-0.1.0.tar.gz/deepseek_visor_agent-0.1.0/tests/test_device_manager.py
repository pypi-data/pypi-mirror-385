"""Tests for DeviceManager"""

import pytest
from deepseek_visor_agent import DeviceManager


def test_device_detection():
    """Test device detection returns valid config"""
    config = DeviceManager.detect_optimal_config()

    assert "device" in config
    assert config["device"] in ["cuda", "mps", "cpu"]
    assert "inference_mode" in config
    assert config["inference_mode"] in ["gundam", "large", "base", "small", "tiny"]
    assert "use_flash_attn" in config
    assert "max_memory_gb" in config
    assert isinstance(config["max_memory_gb"], (int, float))


def test_device_info():
    """Test device info string generation"""
    info = DeviceManager.get_device_info()
    assert isinstance(info, str)
    assert len(info) > 0
