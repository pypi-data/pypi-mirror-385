"""Vision Language Model tagger using Pydantic-AI."""

import base64
import logging
import os
from typing import Optional

import cv2
import numpy as np
from pydantic_ai import Agent
from pydantic_ai.messages import ImageUrl
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from ..utils.image import resize_keep_aspect

logger = logging.getLogger(__name__)


class VLM:
    """
    Vision Language Model tagger for verification and reconciliation.

    Uses VLM (GPT-5-mini by default) to verify and reconcile outputs from
    Florence2 and WD14, converting tags to natural language descriptions.
    """

    def __init__(
        self,
        model_name: str = "gpt-5-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_size: int = 2048,
        auto_resize: bool = True,
    ):
        """
        Initialize Vision Language Model.

        Supports both OpenAI and OpenRouter models:
        - OpenAI models: gpt-5, gpt-5-mini (default), gpt-5-nano, gpt-4o
        - OpenRouter models: google/gemini-2.5-flash, anthropic/claude-3.5-sonnet, etc.

        Args:
            model_name: Model name (default: gpt-5-mini for OpenAI)
            api_key: API key (required, or set OPENAI_API_KEY/OPENROUTER_API_KEY env var)
            base_url: API base URL (default: None for OpenAI, set to "https://openrouter.ai/api/v1" for OpenRouter)
            system_prompt: System prompt for the model
            max_size: Maximum size for longest edge (default: 2048, OpenAI recommended)
            auto_resize: Automatically resize images larger than max_size (default: True)

        Examples:
            # OpenAI (pass API key explicitly)
            vlm = VLM(api_key="your-openai-key")
            vlm = VLM(model_name="gpt-5", api_key="your-openai-key")

            # OpenAI (from environment variable)
            import os
            vlm = VLM(api_key=os.getenv("OPENAI_API_KEY"))

            # OpenRouter
            vlm = VLM(
                model_name="google/gemini-2.5-flash",
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY")
            )
        """
        self.model_name = model_name
        self.base_url = base_url
        self.max_size = max_size
        self.auto_resize = auto_resize

        # Determine API key based on base_url
        if base_url and "openrouter" in base_url:
            # OpenRouter mode
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable or pass api_key parameter."
                )
        else:
            # OpenAI mode (default)
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter."
                )

        # Default system prompt
        self.system_prompt = system_prompt or (
            "You are an expert at creating precise image generation prompts. "
            "Your goal is to describe images concisely for AI image generators. "
            "Write in a comma-separated, tag-like style optimized for Stable Diffusion, Midjourney, FLUX, etc. "
            "Be specific and accurate based on what you see. "
            "Do not invent details. Keep descriptions concise but informative. "
            "Focus on: medium type, subject, composition, technical details, and atmosphere."
        )

        self.user_prompt = (
            "Create a detailed image generation prompt by analyzing the image and reconciling information from "
            "Florence2 caption and WD14 tags.\n\n"
            "REQUIRED FORMAT: Start with 'A [medium] of' where [medium] is: photograph, digital art, "
            "oil painting, watercolor, anime, illustration, 3D render, etc.\n\n"
            "YOUR TASK AS A VERIFICATION AND RECONCILIATION LAYER:\n"
            "1. EXAMINE THE IMAGE DIRECTLY - your visual analysis is the primary source of truth\n"
            "2. COMPARE Florence2 and WD14 information:\n"
            "   - WD14 tags with high confidence (>0.9) are likely accurate\n"
            "   - Tags like 'solo', '1girl', '1boy' indicate the number of main subjects\n"
            "   - Florence2 may hallucinate details not present in the image\n"
            "3. RESOLVE CONTRADICTIONS:\n"
            "   - If Florence2 says 'a few people walking around' but WD14 says 'solo' (confidence >0.9), "
            "verify by looking at the image yourself\n"
            "   - If WD14 says '1girl, solo' but Florence2 mentions multiple people, trust the high-confidence "
            "WD14 tags and your own observation\n"
            "   - Only include details you can actually see in the image\n"
            "4. BUILD THE FINAL DESCRIPTION:\n"
            "   - Start with verified subject information (number of people, main subject)\n"
            "   - Convert WD14 tags to natural English (e.g., '1girl, solo' → 'a solo girl' or 'a single girl alone')\n"
            "   - Add accurate details from both sources that match what you see\n"
            "   - Include composition, technical details, and atmosphere\n"
            "   - Add EXIF camera/lens data if available\n\n"
            "CRITICAL: Do not blindly copy Florence2's caption or WD14 tags verbatim. Verify each claim against the actual image. "
            "Convert WD14 tags into natural, flowing English. When WD14 has high-confidence tags that contradict Florence2, "
            "investigate and use the accurate information.\n\n"
            "Write as a flowing, comma-separated description suitable for AI image generation."
        )

        # Initialize OpenAI-compatible model
        if self.base_url:
            # Custom base URL (e.g., OpenRouter)
            provider = OpenAIProvider(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        else:
            # Default OpenAI
            provider = OpenAIProvider(
                api_key=self.api_key,
            )

        self.model = OpenAIChatModel(
            model_name=self.model_name,
            provider=provider,
        )

        # Create agent
        self.agent = Agent(
            model=self.model,
            system_prompt=self.system_prompt,
        )

        logger.info(
            f"Initialized VLM (model={model_name}, base_url={base_url or 'OpenAI'}, "
            f"max_size={max_size}, auto_resize={auto_resize})"
        )

    def _prepare_image_input(self, image: np.ndarray) -> str:
        """
        Prepare image input for the model.

        Automatically resizes images larger than max_size if auto_resize is enabled.
        Preserves aspect ratio (no padding).

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)

        Returns:
            base64 encoded image data URL string
        """
        if not isinstance(image, np.ndarray):
            raise TypeError(f"Image must be numpy.ndarray (OpenCV format), got {type(image)}")

        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(f"Image must be HxWx3 array, got shape {image.shape}")

        # Auto-resize if enabled and image is larger than max size
        if self.auto_resize:
            h, w = image.shape[:2]
            if max(h, w) > self.max_size:
                logger.debug(f"Resizing image from {w}x{h} to fit within {self.max_size}px")
                image = resize_keep_aspect(image, self.max_size)

        # Encode image to JPEG using OpenCV (already in BGR format)
        success, encoded_image = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 95])

        if not success:
            raise RuntimeError("Failed to encode image to JPEG")

        # Convert to base64
        image_bytes = encoded_image.tobytes()
        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        return f"data:image/jpeg;base64,{b64_image}"

    async def generate_caption(
        self,
        image: np.ndarray,
        context: Optional[str] = None,
        user_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate a detailed natural language caption for the image (async).

        This is the primary async method. For synchronous usage, use generate_caption_sync().

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)
            context: Additional context (e.g., tags from other models)
            user_prompt: Custom user prompt (overrides default)
            **kwargs: Additional arguments

        Returns:
            str: Generated caption

        Example:
            >>> import cv2
            >>> import capflow as cf
            >>> vlm = cf.VLM(api_key="...")
            >>> image = cv2.imread("image.jpg")
            >>> caption = await vlm.generate_caption(image)
        """
        # Prepare image input (encode to base64)
        image_input = self._prepare_image_input(image)

        # Build prompt
        if user_prompt:
            prompt = user_prompt
        else:
            prompt = "Describe this image in detail."

        # Add context if provided
        if context:
            prompt += f"\n\nAdditional context from other analysis:\n{context}"

        # Build message list (wrap base64 data URL in ImageUrl)
        messages = [prompt, ImageUrl(url=image_input)]

        # Run agent asynchronously
        try:
            result = await self.agent.run(messages)
            return result.output
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            raise

    def generate_caption_sync(
        self,
        image: np.ndarray,
        context: Optional[str] = None,
        user_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate a detailed natural language caption for the image (sync).

        Uses pydantic-ai's official run_sync() method for reliable synchronous execution.
        For async usage, prefer generate_caption().

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)
            context: Additional context (e.g., tags from other models)
            user_prompt: Custom user prompt (overrides default)
            **kwargs: Additional arguments

        Returns:
            str: Generated caption

        Example:
            >>> import cv2
            >>> import capflow as cf
            >>> vlm = cf.VLM(api_key="...")
            >>> image = cv2.imread("image.jpg")
            >>> caption = vlm.generate_caption_sync(image)
        """
        # Prepare image input (encode to base64)
        image_input = self._prepare_image_input(image)

        # Build prompt
        if user_prompt:
            prompt = user_prompt
        else:
            prompt = "Describe this image in detail."

        # Add context if provided
        if context:
            prompt += f"\n\nAdditional context from other analysis:\n{context}"

        # Build message list (wrap base64 data URL in ImageUrl)
        messages = [prompt, ImageUrl(url=image_input)]

        # Run agent synchronously using official run_sync()
        try:
            result = self.agent.run_sync(messages)
            return result.output
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            raise

    async def refine_caption(
        self,
        image: np.ndarray,
        context: str | None = None,
        **kwargs,
    ) -> str:
        """
        Refine an existing caption for the image (async).

        This is the primary async method. For synchronous usage, use refine_caption_sync().

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)
            context: Additional context (e.g., tags from other models)
            user_prompt: Custom user prompt (overrides default)
            **kwargs: Additional arguments

        Returns:
            str: Refined caption
        """

        return await self.generate_caption(
            image=image,
            context=context,
            user_prompt=self.user_prompt,
            **kwargs,
        )

    def refine_caption_sync(
        self,
        image: np.ndarray,
        context: str | None = None,
        **kwargs,
    ) -> str:
        """
        Refine an existing caption for the image (sync).

        Args:
            image: Image as numpy array (HxWx3, BGR format from OpenCV)
            context: Additional context (e.g., tags from other models)
            **kwargs: Additional arguments

        Returns:
            str: Refined caption
        """

        return self.generate_caption_sync(
            image=image,
            context=context,
            user_prompt=self.user_prompt,
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"VLM(model_name='{self.model_name}')"
