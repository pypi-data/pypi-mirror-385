"""Device selection utilities for cross-platform compatibility."""

import logging

import torch

logger = logging.getLogger(__name__)


def get_optimal_device() -> torch.device:
    """
    Automatically select the optimal device based on available hardware.

    Returns:
        torch.device: Optimal device ("cuda", "mps", or "cpu")
    """
    if torch.cuda.is_available():
        device = "cuda"
        logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
    elif torch.backends.mps.is_available():
        device = "mps"
        logger.info("Using MPS (Apple Silicon GPU) device")
    else:
        device = "cpu"
        logger.info("Using CPU device (inference will be slower)")

    return torch.device(device)


def get_torch_dtype(device: torch.device) -> torch.dtype:
    """
    Get the appropriate torch dtype for the given device.

    Args:
        device: Target device

    Returns:
        torch.dtype: Recommended dtype for the device
    """
    if "cuda" in device.type:
        # Use float16 for CUDA to save VRAM
        return torch.float16
    elif "mps" in device.type:
        # MPS has better support for float32
        return torch.float32
    else:
        # CPU uses float32
        return torch.float32
