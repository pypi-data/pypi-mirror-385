"""Tests for Florence2 model."""

import cv2
import pytest

import capflow as cf


@pytest.fixture
def sample_image():
    """Load sample test image."""
    image = cv2.imread("tests/images/panther-stadium-statue.jpg")
    assert image is not None, "Test image not found"
    return image


@pytest.fixture
def florence2_model():
    """Initialize Florence2 model (base)."""
    return cf.Florence2()


def test_florence2_initialization():
    """Test Florence2 model initialization."""
    florence2 = cf.Florence2()
    assert florence2.model_name == "microsoft/Florence-2-base"
    assert florence2.target_size == 768
    assert florence2.auto_resize is True


def test_florence2_generate_caption(florence2_model, sample_image):
    """Test basic caption generation."""
    caption = florence2_model.generate_caption(sample_image)

    assert isinstance(caption, str)
    assert len(caption) > 0

    print(f"\nGenerated caption: {caption}")


def test_florence2_caption_tasks(florence2_model, sample_image):
    """Test different caption detail levels."""
    # Test all three task types
    tasks = ["caption", "detailed_caption", "more_detailed_caption"]
    captions = {}

    for task in tasks:
        caption = florence2_model.generate_caption(sample_image, task=task)
        captions[task] = caption

        assert isinstance(caption, str)
        assert len(caption) > 0

        print(f"\n{task}: {caption}")

    # More detailed captions should generally be longer
    # (not always guaranteed, but usually true)
    print(f"\nCaption lengths: {[(t, len(c)) for t, c in captions.items()]}")


def test_florence2_generation_parameters(florence2_model, sample_image):
    """Test generation parameter variations."""
    # Test with different num_beams
    caption_beam3 = florence2_model.generate_caption(
        sample_image,
        task="detailed_caption",
        num_beams=3
    )
    caption_beam5 = florence2_model.generate_caption(
        sample_image,
        task="detailed_caption",
        num_beams=5
    )

    assert isinstance(caption_beam3, str)
    assert isinstance(caption_beam5, str)
    assert len(caption_beam3) > 0
    assert len(caption_beam5) > 0

    print(f"\nBeam 3: {caption_beam3}")
    print(f"Beam 5: {caption_beam5}")

    # Test with sampling
    caption_sampling = florence2_model.generate_caption(
        sample_image,
        task="detailed_caption",
        do_sample=True,
        temperature=0.9
    )

    assert isinstance(caption_sampling, str)
    assert len(caption_sampling) > 0

    print(f"\nWith sampling: {caption_sampling}")


def test_florence2_repetition_penalty(florence2_model, sample_image):
    """Test repetition penalty parameter."""
    # Low repetition penalty (may repeat more)
    caption_low_penalty = florence2_model.generate_caption(
        sample_image,
        task="detailed_caption",
        repetition_penalty=1.0
    )

    # High repetition penalty (should repeat less)
    caption_high_penalty = florence2_model.generate_caption(
        sample_image,
        task="detailed_caption",
        repetition_penalty=1.5
    )

    assert isinstance(caption_low_penalty, str)
    assert isinstance(caption_high_penalty, str)
    assert len(caption_low_penalty) > 0
    assert len(caption_high_penalty) > 0

    print(f"\nRepetition penalty 1.0: {caption_low_penalty}")
    print(f"Repetition penalty 1.5: {caption_high_penalty}")


def test_florence2_max_new_tokens(florence2_model, sample_image):
    """Test max_new_tokens parameter."""
    # Short caption
    caption_short = florence2_model.generate_caption(
        sample_image,
        task="detailed_caption",
        max_new_tokens=50
    )

    # Long caption
    caption_long = florence2_model.generate_caption(
        sample_image,
        task="more_detailed_caption",
        max_new_tokens=200
    )

    assert isinstance(caption_short, str)
    assert isinstance(caption_long, str)
    assert len(caption_short) > 0
    assert len(caption_long) > 0

    print(f"\nShort (50 tokens): {caption_short}")
    print(f"Long (200 tokens): {caption_long}")


def test_florence2_auto_resize(sample_image):
    """Test auto-resize functionality."""
    # Disable auto-resize
    florence2_no_resize = cf.Florence2(auto_resize=False)
    caption_no_resize = florence2_no_resize.generate_caption(sample_image)

    # Enable auto-resize (default)
    florence2_with_resize = cf.Florence2(auto_resize=True)
    caption_with_resize = florence2_with_resize.generate_caption(sample_image)

    # Both should generate captions
    assert len(caption_no_resize) > 0
    assert len(caption_with_resize) > 0

    print(f"\nNo resize: {caption_no_resize}")
    print(f"With resize: {caption_with_resize}")


def test_florence2_custom_target_size(sample_image):
    """Test custom target size."""
    # Custom target size
    florence2_custom = cf.Florence2(target_size=512)
    caption = florence2_custom.generate_caption(sample_image)

    assert isinstance(caption, str)
    assert len(caption) > 0

    print(f"\nCustom target size (512): {caption}")


def test_florence2_model_selection():
    """Test different model size selection."""
    # Base model
    florence2_base = cf.Florence2(model_name="base")
    assert florence2_base.model_name == "microsoft/Florence-2-base"

    # Large model
    florence2_large = cf.Florence2(model_name="large")
    assert florence2_large.model_name == "microsoft/Florence-2-large"


def test_florence2_invalid_task(florence2_model, sample_image):
    """Test error handling for invalid task."""
    with pytest.raises(ValueError, match="Invalid task"):
        florence2_model.generate_caption(sample_image, task="invalid_task")
