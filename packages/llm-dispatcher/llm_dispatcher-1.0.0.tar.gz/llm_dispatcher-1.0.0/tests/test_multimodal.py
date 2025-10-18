"""
Tests for multimodal functionality.

This module contains comprehensive tests for the multimodal analysis,
image processing, audio processing, and media validation capabilities.
"""

import pytest
import base64
import io
from unittest.mock import Mock, patch
from PIL import Image
import numpy as np

from llm_dispatcher.multimodal import (
    ImageProcessor,
    ImageFormat,
    ImageQuality,
    ImageMetadata,
    AudioProcessor,
    AudioFormat,
    AudioQuality,
    AudioMetadata,
    MultimodalAnalyzer,
    AnalysisType,
    ComplexityLevel,
    MediaValidator,
    MediaType,
    ValidationSeverity,
    ValidationIssue,
    ValidationResult,
)


class TestImageProcessor:
    """Test image processing functionality."""

    def test_image_processor_initialization(self):
        """Test image processor initialization."""
        processor = ImageProcessor(max_size_mb=5, quality_threshold=80)
        assert processor.max_size_mb == 5
        assert processor.quality_threshold == 80

    def test_validate_image_valid(self):
        """Test image validation with valid image."""
        # Create a simple test image
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        processor = ImageProcessor()
        is_valid, message = processor.validate_image(img_data)

        assert is_valid
        assert "valid" in message

    def test_validate_image_too_large(self):
        """Test image validation with oversized image."""
        processor = ImageProcessor(max_size_mb=0.001)  # Very small limit

        # Create a larger image
        img = Image.new("RGB", (1000, 1000), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        is_valid, message = processor.validate_image(img_data)

        assert not is_valid
        assert "too large" in message

    def test_validate_image_invalid_format(self):
        """Test image validation with invalid format."""
        processor = ImageProcessor()

        # Invalid image data
        invalid_data = b"not an image"

        is_valid, message = processor.validate_image(invalid_data)

        assert not is_valid
        assert "invalid" in message.lower()

    def test_process_image(self):
        """Test image processing."""
        # Create a test image
        img = Image.new("RGB", (100, 100), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        processor = ImageProcessor()
        processed_data, metadata = processor.process_image(
            img_data,
            target_format=ImageFormat.JPEG,
            quality=ImageQuality.HIGH,
            resize=(50, 50),
        )

        assert isinstance(processed_data, bytes)
        assert isinstance(metadata, ImageMetadata)
        assert metadata.width == 50
        assert metadata.height == 50
        assert metadata.format == "JPEG"

    def test_extract_image_features(self):
        """Test image feature extraction."""
        # Create a test image
        img = Image.new("RGB", (200, 150), color="green")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        processor = ImageProcessor()
        features = processor.extract_image_features(img_data)

        assert "dimensions" in features
        assert "aspect_ratio" in features
        assert "brightness" in features
        assert "contrast" in features
        assert features["dimensions"] == [200, 150]
        assert features["aspect_ratio"] == 200 / 150

    def test_batch_process_images(self):
        """Test batch image processing."""
        # Create multiple test images
        images = []
        for color in ["red", "green", "blue"]:
            img = Image.new("RGB", (100, 100), color=color)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            images.append(img_bytes.getvalue())

        processor = ImageProcessor()
        results = processor.batch_process_images(images)

        assert len(results) == 3
        for processed_data, metadata in results:
            assert isinstance(processed_data, bytes)
            assert isinstance(metadata, ImageMetadata)


class TestAudioProcessor:
    """Test audio processing functionality."""

    def test_audio_processor_initialization(self):
        """Test audio processor initialization."""
        processor = AudioProcessor(max_size_mb=10, max_duration_seconds=60)
        assert processor.max_size_mb == 10
        assert processor.max_duration_seconds == 60

    def test_validate_audio_no_libraries(self):
        """Test audio validation without audio libraries."""
        with patch(
            "llm_dispatcher.multimodal.audio_processor.AUDIO_LIBS_AVAILABLE", False
        ):
            processor = AudioProcessor()

            # Mock audio data
            audio_data = b"fake audio data"

            is_valid, message = processor.validate_audio(audio_data)

            assert is_valid  # Should pass basic validation
            assert "libraries not available" in message

    def test_validate_audio_too_large(self):
        """Test audio validation with oversized audio."""
        processor = AudioProcessor(max_size_mb=0.001)  # Very small limit

        # Create large fake audio data
        large_data = b"x" * (1024 * 1024)  # 1MB

        is_valid, message = processor.validate_audio(large_data)

        assert not is_valid
        assert "too large" in message

    def test_get_audio_info(self):
        """Test getting audio information."""
        processor = AudioProcessor()

        # Mock audio data
        audio_data = b"fake audio data"

        info = processor.get_audio_info(audio_data)

        assert "size_bytes" in info
        assert info["size_bytes"] == len(audio_data)

    def test_extract_audio_features_no_libraries(self):
        """Test audio feature extraction without libraries."""
        with patch(
            "llm_dispatcher.multimodal.audio_processor.AUDIO_LIBS_AVAILABLE", False
        ):
            processor = AudioProcessor()

            audio_data = b"fake audio data"
            features = processor.extract_audio_features(audio_data)

            assert isinstance(features, dict)
            assert len(features) == 0  # Should return empty dict


class TestMediaValidator:
    """Test media validation functionality."""

    def test_media_validator_initialization(self):
        """Test media validator initialization."""
        validator = MediaValidator(
            max_image_size_mb=5, max_audio_size_mb=10, security_strict=True
        )

        assert validator.max_image_size_mb == 5
        assert validator.max_audio_size_mb == 10
        assert validator.security_strict is True

    def test_detect_media_type(self):
        """Test media type detection."""
        validator = MediaValidator()

        # Test JPEG
        jpeg_data = b"\xff\xd8\xff\xe0"
        assert validator._detect_media_type(jpeg_data) == MediaType.IMAGE

        # Test PNG
        png_data = b"\x89PNG\r\n\x1a\n"
        assert validator._detect_media_type(png_data) == MediaType.IMAGE

        # Test WAV
        wav_data = b"RIFF\x00\x00\x00\x00WAVE"
        assert validator._detect_media_type(wav_data) == MediaType.AUDIO

        # Test unknown
        unknown_data = b"unknown format"
        assert validator._detect_media_type(unknown_data) == MediaType.UNKNOWN

    def test_perform_security_checks(self):
        """Test security checks."""
        validator = MediaValidator()

        # Test malicious signature detection
        malicious_data = b"\x4d\x5a" + b"fake executable"
        issues = validator._perform_security_checks(malicious_data)

        assert len(issues) > 0
        assert any(issue.severity == ValidationSeverity.CRITICAL for issue in issues)
        assert any("Malicious file signature" in issue.message for issue in issues)

    def test_validate_media_image(self):
        """Test media validation for image."""
        validator = MediaValidator()

        # Create a test image
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        result = validator.validate_media(img_data)

        assert isinstance(result.is_valid, bool)
        assert result.media_type == MediaType.IMAGE
        assert result.size_bytes == len(img_data)
        assert isinstance(result.security_score, float)
        assert 0 <= result.security_score <= 1

    def test_validate_media_invalid(self):
        """Test media validation with invalid data."""
        validator = MediaValidator()

        invalid_data = b"invalid media data"
        result = validator.validate_media(invalid_data)

        assert isinstance(result.is_valid, bool)
        assert result.media_type == MediaType.UNKNOWN
        assert len(result.issues) > 0

    def test_calculate_security_score(self):
        """Test security score calculation."""
        validator = MediaValidator()

        # Test with no issues
        issues = []
        data = b"normal data"
        score = validator._calculate_security_score(issues, data)
        assert score == 1.0

        # Test with warning
        issues = [
            ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Test warning",
                code="TEST_WARNING",
            )
        ]
        score = validator._calculate_security_score(issues, data)
        assert 0 < score < 1.0

    def test_batch_validate(self):
        """Test batch validation."""
        validator = MediaValidator()

        # Create test data
        img = Image.new("RGB", (50, 50), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        media_list = [img_data, b"invalid data"]
        results = validator.batch_validate(media_list)

        assert len(results) == 2
        assert all(isinstance(result, ValidationResult) for result in results)


class TestMultimodalAnalyzer:
    """Test multimodal analysis functionality."""

    def test_multimodal_analyzer_initialization(self):
        """Test multimodal analyzer initialization."""
        analyzer = MultimodalAnalyzer(
            enable_advanced_analysis=True, cache_analysis_results=True
        )

        assert analyzer.enable_advanced_analysis is True
        assert analyzer.cache_analysis_results is True
        assert analyzer.max_concurrent_analysis == 5

    def test_analyze_multimodal_content_empty(self):
        """Test multimodal analysis with empty data."""
        analyzer = MultimodalAnalyzer()

        result = analyzer.analyze_multimodal_content({})

        assert result.analysis_type == AnalysisType.COMPREHENSIVE
        assert result.media_analysis == {}
        assert result.content_analysis is None
        assert result.task_recommendation is None
        assert result.feature_vectors == {}

    def test_analyze_multimodal_content_image(self):
        """Test multimodal analysis with image."""
        analyzer = MultimodalAnalyzer()

        # Create a test image
        img = Image.new("RGB", (100, 100), color="green")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        media_data = {"image1": img_data}
        result = analyzer.analyze_multimodal_content(media_data)

        assert result.analysis_type == AnalysisType.COMPREHENSIVE
        assert "image1" in result.media_analysis
        assert result.content_analysis is not None
        assert result.task_recommendation is not None

    def test_determine_complexity_level(self):
        """Test complexity level determination."""
        analyzer = MultimodalAnalyzer()

        # Test simple case
        media_analysis = {
            "img1": {"valid": True, "features": {"complexity_score": 0.2}}
        }
        complexity = analyzer._determine_complexity_level(media_analysis, None)
        assert complexity == ComplexityLevel.SIMPLE

        # Test complex case
        media_analysis = {
            "img1": {"valid": True, "features": {"complexity_score": 0.8}},
            "img2": {"valid": True, "features": {"complexity_score": 0.9}},
        }
        complexity = analyzer._determine_complexity_level(media_analysis, None)
        assert complexity == ComplexityLevel.MODERATE

    def test_select_optimal_providers(self):
        """Test provider selection."""
        analyzer = MultimodalAnalyzer()

        # Test image-only
        media_analysis = {"img1": {"valid": True, "type": "image"}}
        providers = analyzer._select_optimal_providers(
            media_analysis, ComplexityLevel.SIMPLE
        )
        assert len(providers) > 0
        assert "openai" in providers

        # Test multimodal
        media_analysis = {
            "img1": {"valid": True, "type": "image"},
            "audio1": {"valid": True, "type": "audio"},
        }
        providers = analyzer._select_optimal_providers(
            media_analysis, ComplexityLevel.MODERATE
        )
        assert len(providers) > 0

    def test_extract_feature_vectors(self):
        """Test feature vector extraction."""
        analyzer = MultimodalAnalyzer()

        media_analysis = {
            "img1": {
                "valid": True,
                "type": "image",
                "features": {
                    "dimensions": [100, 100],
                    "aspect_ratio": 1.0,
                    "brightness": 0.5,
                    "contrast": 0.5,
                    "sharpness": 0.5,
                    "complexity_score": 0.5,
                },
            }
        }

        vectors = analyzer._extract_feature_vectors(media_analysis)

        assert "img1" in vectors
        assert isinstance(vectors["img1"], list)
        assert len(vectors["img1"]) > 0

    def test_generate_cache_key(self):
        """Test cache key generation."""
        analyzer = MultimodalAnalyzer()

        media_data = {"img1": b"test data"}
        cache_key = analyzer._generate_cache_key(
            media_data, AnalysisType.COMPREHENSIVE, "test task"
        )

        assert isinstance(cache_key, str)
        assert len(cache_key) == 64  # SHA256 hex length

        # Test cache key consistency
        cache_key2 = analyzer._generate_cache_key(
            media_data, AnalysisType.COMPREHENSIVE, "test task"
        )
        assert cache_key == cache_key2

    def test_clear_cache(self):
        """Test cache clearing."""
        analyzer = MultimodalAnalyzer()

        # Add something to cache
        analyzer.analysis_cache["test"] = "data"
        assert len(analyzer.analysis_cache) > 0

        analyzer.clear_cache()
        assert len(analyzer.analysis_cache) == 0

    def test_get_cache_stats(self):
        """Test cache statistics."""
        analyzer = MultimodalAnalyzer()

        stats = analyzer.get_cache_stats()

        assert "cache_size" in stats
        assert "cache_enabled" in stats
        assert stats["cache_size"] == 0
        assert stats["cache_enabled"] is True


class TestMultimodalIntegration:
    """Integration tests for multimodal functionality."""

    def test_end_to_end_image_analysis(self):
        """Test complete image analysis pipeline."""
        # Create test image
        img = Image.new("RGB", (200, 150), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        # Process through pipeline
        validator = MediaValidator()
        image_processor = ImageProcessor()
        analyzer = MultimodalAnalyzer()

        # Validate
        validation_result = validator.validate_media(img_data)
        assert validation_result.is_valid

        # Process
        processed_data, metadata = image_processor.process_image(img_data)
        assert isinstance(metadata, ImageMetadata)

        # Analyze
        media_data = {"test_image": img_data}
        analysis_result = analyzer.analyze_multimodal_content(media_data)

        assert analysis_result.media_analysis["test_image"]["valid"] is True
        assert analysis_result.task_recommendation is not None

    def test_multimodal_workflow(self):
        """Test complete multimodal workflow."""
        # Create test media
        img = Image.new("RGB", (100, 100), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        # Create multimodal data
        media_data = {"image1": img_data, "audio1": b"fake audio data"}

        # Run analysis
        analyzer = MultimodalAnalyzer()
        result = analyzer.analyze_multimodal_content(
            media_data,
            analysis_type=AnalysisType.COMPREHENSIVE,
            task_description="Analyze image and audio content",
        )

        # Verify results
        assert result.analysis_type == AnalysisType.COMPREHENSIVE
        assert len(result.media_analysis) == 2
        assert result.content_analysis is not None
        assert result.task_recommendation is not None
        assert result.task_recommendation.confidence_score > 0

    def test_error_handling(self):
        """Test error handling in multimodal pipeline."""
        analyzer = MultimodalAnalyzer()

        # Test with invalid data
        media_data = {"invalid": b"corrupted data"}

        result = analyzer.analyze_multimodal_content(media_data)

        # Should handle errors gracefully
        assert result.media_analysis["invalid"]["valid"] is False
        assert "error" in result.media_analysis["invalid"]
