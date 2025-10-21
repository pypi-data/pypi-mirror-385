"""Florence2 model wrapper for image captioning and visual understanding."""

import logging
import warnings
from typing import Literal, Optional

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoProcessor, PreTrainedModel

from ..utils.device import get_optimal_device, get_torch_dtype
from ..utils.image import resize_with_padding

logger = logging.getLogger(__name__)

# Suppress flash_attn warnings on MPS
warnings.filterwarnings("ignore", message=".*flash_attn.*")


CaptionTask = Literal["caption", "detailed_caption", "more_detailed_caption"]
MODEL_NAMES = Literal["base", "large"]

TASK_PROMPTS = {
    "caption": "<CAPTION>",
    "detailed_caption": "<DETAILED_CAPTION>",
    "more_detailed_caption": "<MORE_DETAILED_CAPTION>",
}


class Florence2:
    """
    Florence2 vision-language tagger for image captioning.

    Supports multiple caption detail levels and cross-platform inference
    (CUDA, MPS, CPU).
    """

    def __init__(
        self,
        model_name: MODEL_NAMES = "base",
        device: Optional[str] = None,
        target_size: int = 768,
        auto_resize: bool = True,
    ):
        """
        Initialize Florence2 model.

        Args:
            model: Model size ("base" or "large")
            device: Target device ("cuda", "mps", "cpu"). Auto-detected if None.
            target_size: Target size for image preprocessing (default: 768, trained resolution)
            auto_resize: Automatically resize images larger than target_size (default: True)
        """
        self.model_name = f"microsoft/Florence-2-{model_name}"
        self.device = torch.device(device) if device else get_optimal_device()
        self.torch_dtype = get_torch_dtype(self.device)
        self.target_size = target_size
        self.auto_resize = auto_resize
        self.model: PreTrainedModel | None = None
        self.processor: AutoProcessor | None = None

        logger.info(
            f"Initialized Florence2 (model={model_name}, device={self.device}, "
            f"dtype={self.torch_dtype}, target_size={target_size}, auto_resize={auto_resize})"
        )

    def _load_model(self):
        """Lazy load the model and processor."""
        if self.model is not None and self.processor is not None:
            return

        logger.info(f"Loading Florence2 model: {self.model_name}")

        # Load processor
        self.processor = AutoProcessor.from_pretrained(
            self.model_name,
            trust_remote_code=True,
        )

        # Load model
        # Use eager attention implementation to avoid SDPA compatibility issues
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=self.torch_dtype,
            trust_remote_code=True,
            attn_implementation="eager",
        ).to(self.device)

        logger.info("Model loaded successfully")
        logger.debug(f"Model type: {type(self.model)}")
        logger.debug(f"Processor type: {type(self.processor)}")

    def _prepare_image(self, image: np.ndarray) -> np.ndarray:
        """
        Prepare numpy array image for processing.

        Automatically resizes images larger than target_size if auto_resize is enabled.
        Preserves aspect ratio and adds padding to create square images.

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)

        Returns:
            numpy array in RGB format (HxWx3)
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
                image = resize_with_padding(image, self.target_size)

        # Convert BGR (OpenCV) to RGB
        return image[:, :, ::-1].copy()

    def generate_caption(
        self,
        image: np.ndarray,
        task: CaptionTask = "detailed_caption",
        max_new_tokens: int = 1024,
        num_beams: int = 3,
        do_sample: bool = False,
        temperature: float = 1.0,
        repetition_penalty: float = 1.0,
    ) -> str:
        """
        Generate a caption for the given image.

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)
            task: Caption detail level
            max_new_tokens: Maximum tokens to generate
            num_beams: Number of beams for beam search
            do_sample: Whether to use sampling
            temperature: Sampling temperature (lower = more conservative)
            repetition_penalty: Penalty for repeating tokens

        Returns:
            str: Generated caption
        """
        self._load_model()

        assert self.model is not None
        assert self.processor is not None

        # Prepare image (convert BGR to RGB)
        rgb_image = self._prepare_image(image)

        # Get task prompt
        if task not in TASK_PROMPTS:
            raise ValueError(f"Invalid task: {task}. Must be one of {list(TASK_PROMPTS.keys())}")
        prompt = TASK_PROMPTS[task]

        # Get image size (width, height)
        height, width = rgb_image.shape[:2]

        # Prepare inputs
        inputs = self.processor(
            text=prompt,
            images=rgb_image,
            return_tensors="pt",
        ).to(self.device, self.torch_dtype)

        # Generate
        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=max_new_tokens,
                num_beams=num_beams,
                do_sample=do_sample,
                temperature=temperature if do_sample else 1.0,
                repetition_penalty=repetition_penalty,
                use_cache=False,  # Disable KV cache to avoid compatibility issues
            )

        # Decode
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

        # Parse the result
        parsed_answer = self.processor.post_process_generation(
            generated_text,
            task=prompt,
            image_size=(width, height),
        )

        # Extract caption text
        caption = parsed_answer.get(prompt, "")

        return caption

    def __repr__(self) -> str:
        return f"Florence2(model_name='{self.model_name}', device='{self.device}')"
