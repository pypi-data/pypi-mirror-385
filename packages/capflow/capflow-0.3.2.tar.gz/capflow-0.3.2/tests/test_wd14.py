"""Tests for WD14 tagger with ONNX Runtime."""

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
def wd14_model():
    """Initialize WD14 model."""
    return cf.WD14()


def test_wd14_initialization():
    """Test WD14 model initialization."""
    wd14 = cf.WD14()
    assert wd14.model_name == "wd-eva02-large-tagger-v3"
    assert wd14.target_size == 448
    assert wd14.auto_resize is True


def test_wd14_generate_tags(wd14_model, sample_image):
    """Test basic tag generation."""
    tags = wd14_model.generate_tags(sample_image)

    assert isinstance(tags, list)
    assert len(tags) > 0
    assert all(isinstance(tag, str) for tag in tags)

    print(f"\nGenerated {len(tags)} tags")
    print(f"First 10 tags: {tags[:10]}")


def test_wd14_generate_caption(wd14_model, sample_image):
    """Test caption generation (comma-separated tags)."""
    caption = wd14_model.generate_caption(sample_image)

    assert isinstance(caption, str)
    assert len(caption) > 0
    assert "," in caption

    print(f"\nGenerated caption: {caption[:100]}...")


def test_wd14_generate_tags_with_scores(wd14_model, sample_image):
    """Test tag generation with confidence scores."""
    tags_with_scores = wd14_model.generate_tags_with_scores(sample_image)

    assert isinstance(tags_with_scores, dict)
    assert len(tags_with_scores) > 0

    for tag, score in tags_with_scores.items():
        assert isinstance(tag, str)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    # Print top 10 tags with scores
    sorted_tags = sorted(tags_with_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\nTop 10 tags with scores:")
    for tag, score in sorted_tags:
        print(f"  {tag}: {score:.3f}")


def test_wd14_get_rating(wd14_model, sample_image):
    """Test rating prediction."""
    rating, confidence = wd14_model.get_rating(sample_image)

    assert isinstance(rating, str)
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0

    print(f"\nRating: {rating} ({confidence:.3f})")


def test_wd14_custom_thresholds(wd14_model, sample_image):
    """Test custom threshold values."""
    # High threshold = fewer tags
    tags_high = wd14_model.generate_tags(
        sample_image,
        general_threshold=0.7,
        character_threshold=0.9
    )

    # Low threshold = more tags
    tags_low = wd14_model.generate_tags(
        sample_image,
        general_threshold=0.2,
        character_threshold=0.5
    )

    assert len(tags_low) > len(tags_high)
    print(f"\nHigh threshold: {len(tags_high)} tags")
    print(f"Low threshold: {len(tags_low)} tags")


def test_wd14_auto_resize(sample_image):
    """Test auto-resize functionality."""
    # Disable auto-resize
    wd14_no_resize = cf.WD14(auto_resize=False)
    tags_no_resize = wd14_no_resize.generate_tags(sample_image)

    # Enable auto-resize (default)
    wd14_with_resize = cf.WD14(auto_resize=True)
    tags_with_resize = wd14_with_resize.generate_tags(sample_image)

    # Both should generate tags
    assert len(tags_no_resize) > 0
    assert len(tags_with_resize) > 0

    print(f"\nNo resize: {len(tags_no_resize)} tags")
    print(f"With resize: {len(tags_with_resize)} tags")


def test_wd14_model_selection():
    """Test different model selection."""
    # EVA02 model (default)
    wd14_eva = cf.WD14(model_name="wd-eva02-large-tagger-v3")
    assert wd14_eva.repo_id == "SmilingWolf/wd-eva02-large-tagger-v3"

    # ViT model
    wd14_vit = cf.WD14(model_name="wd-vit-large-tagger-v3")
    assert wd14_vit.repo_id == "SmilingWolf/wd-vit-large-tagger-v3"


def test_wd14_predict_raw(wd14_model, sample_image):
    """Test raw prediction output."""
    result = wd14_model.predict(sample_image)

    assert "ratings" in result
    assert "general_probs" in result
    assert "character_probs" in result

    # Check ratings dict
    ratings = result["ratings"]
    assert isinstance(ratings, dict)
    assert len(ratings) > 0

    # Check probabilities are numpy arrays or lists
    general_probs = result["general_probs"]
    character_probs = result["character_probs"]
    assert len(general_probs) > 0
    assert len(character_probs) > 0

    print(f"\nRatings: {ratings}")
    print(f"General tags count: {len(general_probs)}")
    print(f"Character tags count: {len(character_probs)}")
