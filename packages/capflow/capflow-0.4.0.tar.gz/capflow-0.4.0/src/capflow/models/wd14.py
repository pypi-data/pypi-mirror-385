"""WD14 tagger models for anime/illustration image tagging."""

import csv
import logging
from typing import Any, Literal, Optional

import cv2
import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download

from ..utils.device import get_optimal_device
from ..utils.image import resize_with_padding

logger = logging.getLogger(__name__)

MODEL_NAMES = Literal["wd-eva02-large-tagger-v3", "wd-vit-large-tagger-v3"]

MODEL_REPO_MAP = {
    "wd-eva02-large-tagger-v3": "SmilingWolf/wd-eva02-large-tagger-v3",
    "wd-vit-large-tagger-v3": "SmilingWolf/wd-vit-large-tagger-v3",
}


class WD14:
    """
    WD14 (Waifu Diffusion 14) tagger for anime/illustration images.

    Supports danbooru-style tagging with ratings, characters, and general tags.
    Uses ONNX Runtime for efficient inference without timm dependency.
    """

    def __init__(
        self,
        model_name: MODEL_NAMES = "wd-eva02-large-tagger-v3",
        device: Optional[str] = None,
        general_threshold: float = 0.35,
        character_threshold: float = 0.75,
        target_size: int = 448,
        auto_resize: bool = True,
    ):
        """
        Initialize WD14 tagger.

        Args:
            model_name: Model name
            device: Target device ("cuda", "mps", "cpu"). Auto-detected if None.
            general_threshold: Threshold for general tags
            character_threshold: Threshold for character tags
            target_size: Target size for image preprocessing (default: 448, trained resolution)
            auto_resize: Automatically resize images larger than target_size (default: True)
        """
        self.model_name = model_name
        self.repo_id = MODEL_REPO_MAP[model_name]
        self.device = device or get_optimal_device()
        self.general_threshold = general_threshold
        self.character_threshold = character_threshold
        self.target_size = target_size
        self.auto_resize = auto_resize

        self.ort_session = None
        self.tags_df = None
        self.rating_tags = None
        self.general_tags = None
        self.character_tags = None

        logger.info(
            f"Initialized WD14 (model={model_name}, device={self.device}, "
            f"target_size={target_size}, auto_resize={auto_resize})"
        )

    def _load_model(self):
        """Lazy load the ONNX model and tag labels."""
        if self.ort_session is not None:
            return

        logger.info(f"Loading WD14 ONNX model: {self.model_name}")

        # Download ONNX model file
        model_path = hf_hub_download(
            repo_id=self.repo_id,
            filename="model.onnx",
        )

        # Download CSV file
        csv_path = hf_hub_download(
            repo_id=self.repo_id,
            filename="selected_tags.csv",
        )

        # Load tags CSV with standard library
        self.rating_tags = []
        self.general_tags = []
        self.character_tags = []

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tag_name = row["name"]
                category = int(row["category"])

                if category == 9:  # Rating tags
                    self.rating_tags.append(tag_name)
                elif category == 0:  # General tags
                    self.general_tags.append(tag_name)
                elif category == 4:  # Character tags
                    self.character_tags.append(tag_name)

        # Setup ONNX Runtime providers based on device
        providers = []
        if self.device == "cuda":
            providers.append("CUDAExecutionProvider")
        elif self.device == "mps":
            # MPS not supported by ONNX Runtime, fallback to CPU
            logger.warning("MPS not supported by ONNX Runtime, using CPU")
        providers.append("CPUExecutionProvider")

        # Load ONNX model
        self.ort_session = ort.InferenceSession(
            model_path,
            providers=providers,
        )

        logger.info("ONNX model loaded successfully")
        logger.info(
            f"Tags loaded: {len(self.rating_tags)} ratings, "
            f"{len(self.general_tags)} general, {len(self.character_tags)} characters"
        )

    def _prepare_image(self, image: np.ndarray) -> np.ndarray:
        """
        Prepare numpy array image for processing (kohya-ss style).

        Automatically resizes images larger than target_size if auto_resize is enabled.
        Preserves aspect ratio and adds white padding to create square images.

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)

        Returns:
            numpy array in RGB format, padded to square, as float32
        """
        if not isinstance(image, np.ndarray):
            raise TypeError(f"Image must be numpy.ndarray (OpenCV format), got {type(image)}")

        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(f"Image must be HxWx3 array, got shape {image.shape}")

        # Auto-resize if enabled and image is larger than target size
        if self.auto_resize:
            h, w = image.shape[:2]
            if max(h, w) > self.target_size:
                logger.debug(f"Resizing image from {w}x{h} to {self.target_size}x{self.target_size}")
                image = resize_with_padding(image, self.target_size, pad_color=(255, 255, 255))

        # Convert BGR (OpenCV) to RGB
        image = image[:, :, ::-1].copy()

        # Pad to square with white padding (if not already square)
        h, w = image.shape[:2]
        if h != w:
            size = max(h, w)
            pad_x = size - w
            pad_y = size - h
            pad_l = pad_x // 2
            pad_t = pad_y // 2
            image = np.pad(
                image,
                ((pad_t, pad_y - pad_t), (pad_l, pad_x - pad_l), (0, 0)),
                mode="constant",
                constant_values=255,
            )

        # Resize to target size if larger
        if image.shape[0] != self.target_size:
            target_size_tuple = (self.target_size, self.target_size)
            if image.shape[0] > self.target_size:
                image = cv2.resize(src=image, dsize=target_size_tuple, interpolation=cv2.INTER_AREA)
            else:
                image = cv2.resize(src=image, dsize=target_size_tuple, interpolation=cv2.INTER_LINEAR)

        # Convert to float32
        image = image.astype(np.float32)

        return image

    def predict(
        self,
        image: np.ndarray,
    ) -> dict[str, Any]:
        """
        Run prediction and return raw probabilities.

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)

        Returns:
            dict with ratings, general_probs, and character_probs
        """
        self._load_model()
        assert self.ort_session is not None
        assert isinstance(self.rating_tags, list)
        assert isinstance(self.general_tags, list)
        assert isinstance(self.character_tags, list)

        # Prepare image (convert BGR to RGB, pad, resize)
        processed_image: np.ndarray = self._prepare_image(image)

        # Add batch dimension
        input_array: np.ndarray = np.expand_dims(processed_image, axis=0)

        # Get input name
        input_name = self.ort_session.get_inputs()[0].name

        # Run ONNX inference
        probs = self.ort_session.run(None, {input_name: input_array})[0]
        assert isinstance(probs, np.ndarray)  # 型チェッカーへのヒント

        # Apply sigmoid (ONNX model outputs logits)
        probs = 1 / (1 + np.exp(-probs))
        probs = probs[0]  # Remove batch dimension

        # Split into tag categories
        rating_probs = probs[: len(self.rating_tags)]
        general_probs = probs[len(self.rating_tags) : len(self.rating_tags) + len(self.general_tags)]
        character_probs = probs[
            len(self.rating_tags) + len(self.general_tags) : len(self.rating_tags)
            + len(self.general_tags)
            + len(self.character_tags)
        ]

        # Create rating dict
        ratings = {tag: float(prob) for tag, prob in zip(self.rating_tags, rating_probs)}

        return {
            "ratings": ratings,
            "general_probs": general_probs,
            "character_probs": character_probs,
        }

    def generate_tags(
        self,
        image: np.ndarray,
        general_threshold: Optional[float] = None,
        character_threshold: Optional[float] = None,
        **kwargs,
    ) -> list[str]:
        """
        Generate tags for the given image.

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)
            general_threshold: Threshold for general tags (uses default if None)
            character_threshold: Threshold for character tags (uses default if None)
            **kwargs: Additional arguments

        Returns:
            list[str]: List of tags above threshold
        """
        assert self.general_tags is not None
        assert self.character_tags is not None

        general_threshold = general_threshold or self.general_threshold
        character_threshold = character_threshold or self.character_threshold

        result = self.predict(image)

        tags = []

        # Add general tags
        for tag, prob in zip(self.general_tags, result["general_probs"]):
            if prob >= general_threshold:
                tags.append(tag)

        # Add character tags
        for tag, prob in zip(self.character_tags, result["character_probs"]):
            if prob >= character_threshold:
                tags.append(tag)

        return tags

    def generate_caption(
        self,
        image: np.ndarray,
        **kwargs,
    ) -> str:
        """
        Generate a caption from tags (comma-separated).

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)
            **kwargs: Additional arguments passed to generate_tags

        Returns:
            str: Comma-separated tags
        """
        tags = self.generate_tags(image, **kwargs)
        return ", ".join(tags)

    def generate_tags_with_scores(
        self,
        image: np.ndarray,
        general_threshold: Optional[float] = None,
        character_threshold: Optional[float] = None,
    ) -> dict[str, float]:
        """
        Generate tags with confidence scores.

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)
            general_threshold: Threshold for general tags
            character_threshold: Threshold for character tags

        Returns:
            dict[str, float]: Tag names mapped to confidence scores
        """
        assert self.general_tags is not None
        assert self.character_tags is not None

        general_threshold = general_threshold or self.general_threshold
        character_threshold = character_threshold or self.character_threshold

        result = self.predict(image)

        tags_with_scores = {}

        # Add general tags
        for tag, prob in zip(self.general_tags, result["general_probs"]):
            if prob >= general_threshold:
                tags_with_scores[tag] = float(prob)

        # Add character tags
        for tag, prob in zip(self.character_tags, result["character_probs"]):
            if prob >= character_threshold:
                tags_with_scores[tag] = float(prob)

        return tags_with_scores

    def get_rating(
        self,
        image: np.ndarray,
    ) -> tuple[str, float]:
        """
        Get the most likely rating for the image.

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)

        Returns:
            tuple[str, float]: (rating_name, confidence)
        """
        result = self.predict(image)
        ratings = result["ratings"]

        # Find highest rating
        best_rating = max(ratings.items(), key=lambda x: x[1])

        return best_rating

    def __repr__(self) -> str:
        return f"WD14(model_name='{self.model_name}', device='{self.device}')"
