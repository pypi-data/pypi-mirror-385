"""Image preprocessing utilities for resizing and padding."""

import cv2
import numpy as np


def resize_with_padding(
    image: np.ndarray,
    target_size: int,
    pad_color: tuple[int, int, int] = (0, 0, 0),
) -> np.ndarray:
    """
    Resize image to target size while preserving aspect ratio, adding padding.

    Args:
        image: Input image as numpy array (HxWx3, BGR format from OpenCV)
        target_size: Target size for both width and height (square output)
        pad_color: RGB color for padding (default: black)

    Returns:
        Resized and padded square image (target_size x target_size x 3)

    Example:
        >>> import cv2
        >>> image = cv2.imread("photo.jpg")  # 1920x1080
        >>> resized = resize_with_padding(image, 768)
        >>> resized.shape
        (768, 768, 3)
    """
    if not isinstance(image, np.ndarray):
        raise TypeError(f"Image must be numpy.ndarray, got {type(image)}")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"Image must be HxWx3 array, got shape {image.shape}")

    h, w = image.shape[:2]

    # Calculate scaling factor
    scale = target_size / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)

    # Resize image
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Calculate padding
    pad_w = target_size - new_w
    pad_h = target_size - new_h

    # Add padding to make it square
    top = pad_h // 2
    bottom = pad_h - top
    left = pad_w // 2
    right = pad_w - left

    # OpenCV uses BGR, so reverse the pad_color if provided as RGB
    padded = cv2.copyMakeBorder(
        resized,
        top,
        bottom,
        left,
        right,
        cv2.BORDER_CONSTANT,
        value=pad_color,
    )

    return padded


def resize_keep_aspect(
    image: np.ndarray,
    max_size: int,
) -> np.ndarray:
    """
    Resize image to fit within max_size while preserving aspect ratio (no padding).

    Args:
        image: Input image as numpy array (HxWx3, BGR format from OpenCV)
        max_size: Maximum size for the longest edge

    Returns:
        Resized image with longest edge <= max_size

    Example:
        >>> import cv2
        >>> image = cv2.imread("photo.jpg")  # 4000x3000
        >>> resized = resize_keep_aspect(image, 2048)
        >>> max(resized.shape[:2])
        2048
    """
    if not isinstance(image, np.ndarray):
        raise TypeError(f"Image must be numpy.ndarray, got {type(image)}")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"Image must be HxWx3 array, got shape {image.shape}")

    h, w = image.shape[:2]

    # If already smaller than max_size, return as-is
    if max(h, w) <= max_size:
        return image

    # Calculate scaling factor
    scale = max_size / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)

    # Resize image
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    return resized
