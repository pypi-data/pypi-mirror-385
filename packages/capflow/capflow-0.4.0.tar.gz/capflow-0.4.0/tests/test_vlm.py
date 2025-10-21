"""Tests for VLM (Vision Language Model)."""

import cv2
import pytest

import capflow as cf


@pytest.fixture
def sample_image_array(sample_image):
    """Load sample test image as numpy array."""
    image = cv2.imread(str(sample_image))
    assert image is not None, "Test image not found"
    return image


@pytest.fixture
def vlm_model(openai_api_key):
    """Initialize VLM model with API key."""
    return cf.VLM(api_key=openai_api_key)


def test_vlm_initialization(openai_api_key):
    """Test VLM model initialization."""
    vlm = cf.VLM(api_key=openai_api_key)
    assert vlm.model_name == "gpt-5-mini"
    assert vlm.max_size == 2048
    assert vlm.auto_resize is True
    assert vlm.api_key == openai_api_key


def test_vlm_initialization_no_api_key(monkeypatch):
    """Test VLM initialization without API key raises error."""
    # Clear environment variable temporarily
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OpenAI API key not found"):
        cf.VLM(api_key=None)


def test_vlm_generate_caption_sync(vlm_model, sample_image_array):
    """Test synchronous caption generation."""
    caption = vlm_model.generate_caption_sync(sample_image_array)

    assert isinstance(caption, str)
    assert len(caption) > 0

    print(f"\nGenerated caption (sync): {caption}")


@pytest.mark.asyncio
async def test_vlm_generate_caption_async(vlm_model, sample_image_array):
    """Test asynchronous caption generation."""
    caption = await vlm_model.generate_caption(sample_image_array)

    assert isinstance(caption, str)
    assert len(caption) > 0

    print(f"\nGenerated caption (async): {caption}")


def test_vlm_generate_caption_with_context(vlm_model, sample_image_array):
    """Test caption generation with context."""
    context = "Florence2: A statue of a panther\nWD14 Tags: statue, outdoors, building"

    caption = vlm_model.generate_caption_sync(
        sample_image_array,
        context=context
    )

    assert isinstance(caption, str)
    assert len(caption) > 0

    print(f"\nGenerated caption with context: {caption}")


def test_vlm_generate_caption_custom_prompt(vlm_model, sample_image_array):
    """Test caption generation with custom user prompt."""
    custom_prompt = "Describe this image in 3 words."

    caption = vlm_model.generate_caption_sync(
        sample_image_array,
        user_prompt=custom_prompt
    )

    assert isinstance(caption, str)
    assert len(caption) > 0

    print(f"\nGenerated caption with custom prompt: {caption}")


def test_vlm_refine_caption_sync(vlm_model, sample_image_array):
    """Test synchronous caption refinement (Florence2 + WD14 reconciliation)."""
    # Simulate Florence2 and WD14 output
    context = (
        "Florence2: The image shows a statue of a panther perched atop a pedestal.\n"
        "WD14 Tags: statue, solo, outdoors, building, sky"
    )

    refined_caption = vlm_model.refine_caption_sync(
        sample_image_array,
        context=context
    )

    assert isinstance(refined_caption, str)
    assert len(refined_caption) > 0
    # Should start with medium type
    assert any(refined_caption.lower().startswith(prefix) for prefix in [
        "a photograph", "a digital art", "an illustration", "a 3d render"
    ])

    print(f"\nRefined caption (sync): {refined_caption}")


@pytest.mark.asyncio
async def test_vlm_refine_caption_async(vlm_model, sample_image_array):
    """Test asynchronous caption refinement."""
    context = (
        "Florence2: A statue in front of a building.\n"
        "WD14 Tags: statue, solo, outdoors"
    )

    refined_caption = await vlm_model.refine_caption(
        sample_image_array,
        context=context
    )

    assert isinstance(refined_caption, str)
    assert len(refined_caption) > 0

    print(f"\nRefined caption (async): {refined_caption}")


def test_vlm_auto_resize(openai_api_key, sample_image_array):
    """Test auto-resize functionality."""
    # Disable auto-resize
    vlm_no_resize = cf.VLM(api_key=openai_api_key, auto_resize=False)
    caption_no_resize = vlm_no_resize.generate_caption_sync(sample_image_array)

    # Enable auto-resize (default)
    vlm_with_resize = cf.VLM(api_key=openai_api_key, auto_resize=True)
    caption_with_resize = vlm_with_resize.generate_caption_sync(sample_image_array)

    # Both should generate captions
    assert len(caption_no_resize) > 0
    assert len(caption_with_resize) > 0

    print(f"\nNo resize: {caption_no_resize[:100]}...")
    print(f"With resize: {caption_with_resize[:100]}...")


def test_vlm_custom_max_size(openai_api_key, sample_image_array):
    """Test custom max_size parameter."""
    vlm_custom = cf.VLM(api_key=openai_api_key, max_size=1024)
    caption = vlm_custom.generate_caption_sync(sample_image_array)

    assert isinstance(caption, str)
    assert len(caption) > 0

    print(f"\nCustom max size (1024): {caption[:100]}...")


def test_vlm_custom_system_prompt(openai_api_key, sample_image_array):
    """Test custom system prompt."""
    custom_system_prompt = (
        "You are a concise image descriptor. "
        "Describe images in exactly one sentence."
    )

    vlm_custom = cf.VLM(
        api_key=openai_api_key,
        system_prompt=custom_system_prompt
    )
    caption = vlm_custom.generate_caption_sync(sample_image_array)

    assert isinstance(caption, str)
    assert len(caption) > 0

    print(f"\nCustom system prompt: {caption}")


def test_vlm_model_selection(openai_api_key):
    """Test different model selection."""
    # Default model
    vlm_default = cf.VLM(api_key=openai_api_key)
    assert vlm_default.model_name == "gpt-5-mini"

    # Custom model
    vlm_custom = cf.VLM(api_key=openai_api_key, model_name="gpt-4o")
    assert vlm_custom.model_name == "gpt-4o"
