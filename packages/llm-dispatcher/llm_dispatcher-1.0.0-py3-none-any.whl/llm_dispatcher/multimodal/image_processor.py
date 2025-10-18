"""
Advanced image processing for multi-modal LLM tasks.

This module provides comprehensive image processing capabilities including
format conversion, optimization, analysis, and feature extraction.
"""

import base64
import io
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)


class ImageFormat(str, Enum):
    """Supported image formats."""

    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    BMP = "bmp"
    TIFF = "tiff"


class ImageQuality(str, Enum):
    """Image quality levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


@dataclass
class ImageMetadata:
    """Image metadata and analysis results."""

    width: int
    height: int
    format: str
    size_bytes: int
    color_mode: str
    has_transparency: bool
    dominant_colors: List[Tuple[int, int, int]]
    brightness: float
    contrast: float
    sharpness: float
    aspect_ratio: float
    file_hash: str
    processing_time_ms: float


class ImageProcessor:
    """
    Advanced image processor for multi-modal LLM tasks.

    This class provides comprehensive image processing capabilities including
    format conversion, optimization, analysis, and feature extraction.
    """

    def __init__(self, max_size_mb: int = 10, quality_threshold: int = 85):
        self.max_size_mb = max_size_mb
        self.quality_threshold = quality_threshold

        # Supported formats
        self.supported_formats = {
            "JPEG": ImageFormat.JPEG,
            "PNG": ImageFormat.PNG,
            "WEBP": ImageFormat.WEBP,
            "BMP": ImageFormat.BMP,
            "TIFF": ImageFormat.TIFF,
        }

    def validate_image(self, image_data: Union[str, bytes]) -> Tuple[bool, str]:
        """Validate image data and return validation result."""
        try:
            if isinstance(image_data, str):
                # Assume base64 encoded
                if image_data.startswith("data:"):
                    # Remove data URL prefix
                    image_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data

            # Check size
            if len(image_bytes) > self.max_size_mb * 1024 * 1024:
                return (
                    False,
                    f"Image too large: {len(image_bytes) / (1024*1024):.1f}MB > {self.max_size_mb}MB",
                )

            # Try to open image
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()

            return True, "Image is valid"

        except Exception as e:
            return False, f"Invalid image: {str(e)}"

    def process_image(
        self,
        image_data: Union[str, bytes],
        target_format: ImageFormat = ImageFormat.JPEG,
        max_dimension: int = 2048,
        quality: ImageQuality = ImageQuality.MEDIUM,
        resize: Optional[Tuple[int, int]] = None,
    ) -> Tuple[bytes, ImageMetadata]:
        """Process and optimize image for LLM consumption."""
        start_time = datetime.now()

        # Decode image
        if isinstance(image_data, str):
            if image_data.startswith("data:"):
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        # Open image
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(
                image, mask=image.split()[-1] if image.mode == "RGBA" else None
            )
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # Resize if necessary
        if max(image.size) > max_dimension:
            image = self._resize_image(image, max_dimension)

        # Apply specific resize if requested
        if resize:
            image = image.resize(resize, Image.Resampling.LANCZOS)

        # Apply quality optimizations
        if quality == ImageQuality.LOW:
            image = self._apply_low_quality_optimizations(image)
        elif quality == ImageQuality.HIGH:
            image = self._apply_high_quality_optimizations(image)
        elif quality == ImageQuality.ULTRA:
            image = self._apply_ultra_quality_optimizations(image)
        else:  # MEDIUM
            image = self._apply_medium_quality_optimizations(image)

        # Convert to target format
        output_buffer = io.BytesIO()
        save_kwargs = self._get_save_kwargs(target_format, quality)
        image.save(output_buffer, format=target_format.value.upper(), **save_kwargs)

        # Get processed bytes
        processed_bytes = output_buffer.getvalue()

        # Generate metadata
        metadata = self._generate_metadata(
            image, processed_bytes, start_time, target_format
        )

        logger.debug(f"Processed image: {image.size} -> {processed_bytes} bytes")
        return processed_bytes, metadata

    def _resize_image(self, image: Image.Image, max_dimension: int) -> Image.Image:
        """Resize image while maintaining aspect ratio."""
        width, height = image.size

        if width > height:
            new_width = max_dimension
            new_height = int(height * max_dimension / width)
        else:
            new_height = max_dimension
            new_width = int(width * max_dimension / height)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _apply_low_quality_optimizations(self, image: Image.Image) -> Image.Image:
        """Apply low quality optimizations."""
        # Reduce brightness slightly
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.9)

        # Reduce contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(0.8)

        return image

    def _apply_medium_quality_optimizations(self, image: Image.Image) -> Image.Image:
        """Apply medium quality optimizations."""
        # Slight sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)

        return image

    def _apply_high_quality_optimizations(self, image: Image.Image) -> Image.Image:
        """Apply high quality optimizations."""
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)

        return image

    def _apply_ultra_quality_optimizations(self, image: Image.Image) -> Image.Image:
        """Apply ultra quality optimizations."""
        # Maximum sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.15)

        # Enhance brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.05)

        return image

    def _get_save_kwargs(
        self, format: ImageFormat, quality: ImageQuality
    ) -> Dict[str, Any]:
        """Get save parameters for image format and quality."""
        kwargs = {}

        if format == ImageFormat.JPEG:
            quality_map = {
                ImageQuality.LOW: 60,
                ImageQuality.MEDIUM: 75,
                ImageQuality.HIGH: 85,
                ImageQuality.ULTRA: 95,
            }
            kwargs["quality"] = quality_map[quality]
            kwargs["optimize"] = True

        elif format == ImageFormat.WEBP:
            quality_map = {
                ImageQuality.LOW: 60,
                ImageQuality.MEDIUM: 75,
                ImageQuality.HIGH: 85,
                ImageQuality.ULTRA: 95,
            }
            kwargs["quality"] = quality_map[quality]
            kwargs["method"] = 6  # Best compression

        elif format == ImageFormat.PNG:
            kwargs["optimize"] = True
            if quality == ImageQuality.ULTRA:
                kwargs["compress_level"] = 1
            else:
                kwargs["compress_level"] = 6

        return kwargs

    def _generate_metadata(
        self,
        image: Image.Image,
        processed_bytes: bytes,
        start_time: datetime,
        target_format: ImageFormat,
    ) -> ImageMetadata:
        """Generate comprehensive image metadata."""
        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        # Basic properties
        width, height = image.size
        color_mode = image.mode
        has_transparency = image.mode in ("RGBA", "LA") or "transparency" in image.info

        # Calculate aspect ratio
        aspect_ratio = width / height if height > 0 else 1.0

        # Generate file hash
        file_hash = hashlib.sha256(processed_bytes).hexdigest()[:16]

        # Analyze image properties
        brightness = self._calculate_brightness(image)
        contrast = self._calculate_contrast(image)
        sharpness = self._calculate_sharpness(image)
        dominant_colors = self._extract_dominant_colors(image)

        return ImageMetadata(
            width=width,
            height=height,
            format=target_format.value.upper(),
            size_bytes=len(processed_bytes),
            color_mode=color_mode,
            has_transparency=has_transparency,
            dominant_colors=dominant_colors,
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness,
            aspect_ratio=aspect_ratio,
            file_hash=file_hash,
            processing_time_ms=processing_time,
        )

    def _calculate_brightness(self, image: Image.Image) -> float:
        """Calculate average brightness of image."""
        # Convert to grayscale
        gray_image = image.convert("L")

        # Calculate mean pixel value
        pixel_values = list(gray_image.getdata())
        return sum(pixel_values) / len(pixel_values) / 255.0

    def _calculate_contrast(self, image: Image.Image) -> float:
        """Calculate contrast of image."""
        # Convert to grayscale
        gray_image = image.convert("L")

        # Calculate standard deviation of pixel values
        pixel_values = list(gray_image.getdata())
        mean = sum(pixel_values) / len(pixel_values)
        variance = sum((x - mean) ** 2 for x in pixel_values) / len(pixel_values)
        std_dev = variance**0.5

        return std_dev / 255.0

    def _calculate_sharpness(self, image: Image.Image) -> float:
        """Calculate sharpness of image using Laplacian variance."""
        # Convert to grayscale
        gray_image = image.convert("L")
        img_array = np.array(gray_image)

        # Apply Laplacian filter (simplified version)
        # Calculate variance of differences between adjacent pixels
        diff_x = np.diff(img_array, axis=1)
        diff_y = np.diff(img_array, axis=0)

        sharpness = np.var(diff_x) + np.var(diff_y)
        return float(sharpness / 10000)  # Normalize

    def _extract_dominant_colors(
        self, image: Image.Image, num_colors: int = 5
    ) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from image."""
        # Resize image for faster processing
        small_image = image.resize((150, 150))

        # Convert to RGB if necessary
        if small_image.mode != "RGB":
            small_image = small_image.convert("RGB")

        # Get color data
        colors = small_image.getcolors(maxcolors=256 * 256 * 256)

        if not colors:
            return [(128, 128, 128)]  # Default gray

        # Sort by frequency
        colors.sort(key=lambda x: x[0], reverse=True)

        # Extract top colors
        dominant_colors = []
        for count, color in colors[:num_colors]:
            dominant_colors.append(color)

        return dominant_colors

    def batch_process_images(
        self,
        images: List[Union[str, bytes]],
        target_format: ImageFormat = ImageFormat.JPEG,
        max_dimension: int = 2048,
        quality: ImageQuality = ImageQuality.MEDIUM,
    ) -> List[Tuple[str, ImageMetadata]]:
        """Process multiple images in batch."""
        results = []

        for i, image_data in enumerate(images):
            try:
                processed_image, metadata = self.process_image(
                    image_data, target_format, max_dimension, quality
                )
                results.append((processed_image, metadata))

            except Exception as e:
                logger.error(f"Error processing image {i}: {e}")
                # Add placeholder result
                results.append(
                    (
                        "",
                        ImageMetadata(
                            width=0,
                            height=0,
                            format="ERROR",
                            size_bytes=0,
                            color_mode="ERROR",
                            has_transparency=False,
                            dominant_colors=[],
                            brightness=0.0,
                            contrast=0.0,
                            sharpness=0.0,
                            aspect_ratio=1.0,
                            file_hash="",
                            processing_time_ms=0.0,
                        ),
                    )
                )

        return results

    def create_image_thumbnail(
        self, image_data: Union[str, bytes], size: Tuple[int, int] = (256, 256)
    ) -> str:
        """Create a thumbnail of the image."""
        if isinstance(image_data, str):
            if image_data.startswith("data:"):
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        # Open and process image
        image = Image.open(io.BytesIO(image_bytes))
        image.thumbnail(size, Image.Resampling.LANCZOS)

        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        thumbnail_bytes = buffer.getvalue()

        return base64.b64encode(thumbnail_bytes).decode("utf-8")

    def detect_image_type(self, image_data: Union[str, bytes]) -> str:
        """Detect the type/content of the image."""
        if isinstance(image_data, str):
            if image_data.startswith("data:"):
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        try:
            image = Image.open(io.BytesIO(image_bytes))

            # Basic type detection based on properties
            width, height = image.size
            aspect_ratio = width / height

            # Detect common image types
            if abs(aspect_ratio - 1.0) < 0.1:
                return "square"
            elif aspect_ratio > 2.0:
                return "panoramic"
            elif aspect_ratio < 0.5:
                return "portrait_tall"
            elif aspect_ratio > 1.5:
                return "landscape_wide"
            else:
                return "standard"

        except Exception as e:
            logger.error(f"Error detecting image type: {e}")
            return "unknown"

    def get_image_complexity_score(self, image_data: Union[str, bytes]) -> float:
        """Calculate image complexity score (0-1)."""
        try:
            if isinstance(image_data, str):
                if image_data.startswith("data:"):
                    image_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data

            image = Image.open(io.BytesIO(image_bytes))
            gray_image = image.convert("L")
            img_array = np.array(gray_image)

            # Calculate edge density (complexity indicator)
            diff_x = np.diff(img_array, axis=1)
            diff_y = np.diff(img_array, axis=0)
            edge_density = (np.mean(np.abs(diff_x)) + np.mean(np.abs(diff_y))) / 255.0

            # Calculate color variance (another complexity indicator)
            if image.mode == "RGB":
                rgb_array = np.array(image)
                color_variance = np.var(rgb_array) / (255**2)
            else:
                color_variance = 0.1  # Default for grayscale

            # Combine metrics
            complexity_score = (edge_density * 0.7) + (color_variance * 0.3)

            return min(complexity_score, 1.0)

        except Exception as e:
            logger.error(f"Error calculating complexity score: {e}")
            return 0.5  # Default moderate complexity

    def _calculate_complexity_score(self, image: Image.Image) -> float:
        """Calculate complexity score for an Image object."""
        try:
            gray_image = image.convert("L")
            img_array = np.array(gray_image)

            # Calculate edge density (complexity indicator)
            diff_x = np.diff(img_array, axis=1)
            diff_y = np.diff(img_array, axis=0)
            edge_density = (np.mean(np.abs(diff_x)) + np.mean(np.abs(diff_y))) / 255.0

            # Calculate color variance (another complexity indicator)
            if image.mode == "RGB":
                rgb_array = np.array(image)
                color_variance = np.var(rgb_array) / (255**2)
            else:
                color_variance = 0.1  # Default for grayscale

            # Combine metrics
            complexity_score = (edge_density * 0.7) + (color_variance * 0.3)

            return min(complexity_score, 1.0)

        except Exception as e:
            logger.error(f"Error calculating complexity score: {e}")
            return 0.5  # Default moderate complexity

    def extract_image_features(self, image_data: bytes) -> Dict[str, Any]:
        """Extract features from an image for analysis."""
        try:
            image = Image.open(io.BytesIO(image_data))

            # Basic features
            features = {
                "dimensions": [image.width, image.height],
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "has_transparency": image.mode in ("RGBA", "LA")
                or "transparency" in image.info,
                "aspect_ratio": image.width / image.height if image.height > 0 else 1.0,
            }

            # Color analysis
            if image.mode == "RGB":
                rgb_array = np.array(image)
                features.update(
                    {
                        "mean_r": float(np.mean(rgb_array[:, :, 0])),
                        "mean_g": float(np.mean(rgb_array[:, :, 1])),
                        "mean_b": float(np.mean(rgb_array[:, :, 2])),
                        "color_variance": float(np.var(rgb_array)),
                        "brightness": float(np.mean(rgb_array)),
                        "contrast": float(np.std(rgb_array)),
                    }
                )
            else:
                # For grayscale images
                gray_array = np.array(image.convert("L"))
                features.update(
                    {
                        "brightness": float(np.mean(gray_array)),
                        "contrast": float(np.std(gray_array)),
                    }
                )

            # Complexity analysis
            features["complexity_score"] = self._calculate_complexity_score(image)

            return features

        except Exception as e:
            logger.error(f"Error extracting image features: {e}")
            return {
                "error": str(e),
                "dimensions": [0, 0],
                "width": 0,
                "height": 0,
                "format": "unknown",
                "mode": "unknown",
                "has_transparency": False,
                "aspect_ratio": 1.0,
                "brightness": 0.0,
                "contrast": 0.0,
                "complexity_score": 0.5,
            }
