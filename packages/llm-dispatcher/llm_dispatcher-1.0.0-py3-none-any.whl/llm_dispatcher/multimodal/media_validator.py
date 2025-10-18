"""
Media validation and security for multi-modal LLM tasks.

This module provides comprehensive media validation including format validation,
security checks, content analysis, and sanitization for safe LLM processing.
"""

import base64
import hashlib
import mimetypes
import io
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from enum import Enum
import re

try:
    from PIL import Image

    IMAGE_LIBS_AVAILABLE = True
except ImportError:
    IMAGE_LIBS_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    from pydub import AudioSegment

    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False

logger = logging.getLogger(__name__)


class MediaType(str, Enum):
    """Supported media types."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class ValidationSeverity(str, Enum):
    """Validation severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """A validation issue found in media."""

    severity: ValidationSeverity
    message: str
    code: str
    details: Dict[str, Any] = None


@dataclass
class ValidationResult:
    """Result of media validation."""

    is_valid: bool
    media_type: MediaType
    format: str
    size_bytes: int
    issues: List[ValidationIssue]
    metadata: Dict[str, Any]
    security_score: float  # 0-1, higher is safer
    processing_time_ms: float


class MediaValidator:
    """
    Comprehensive media validator for safe LLM processing.

    This class provides validation, security checks, and sanitization
    for various media types including images, audio, and documents.
    """

    def __init__(
        self,
        max_image_size_mb: int = 10,
        max_audio_size_mb: int = 25,
        max_video_size_mb: int = 100,
        allowed_image_formats: List[str] = None,
        allowed_audio_formats: List[str] = None,
        security_strict: bool = True,
    ):
        self.max_image_size_mb = max_image_size_mb
        self.max_audio_size_mb = max_audio_size_mb
        self.max_video_size_mb = max_video_size_mb

        self.allowed_image_formats = allowed_image_formats or [
            "JPEG",
            "PNG",
            "WEBP",
            "GIF",
            "BMP",
        ]
        self.allowed_audio_formats = allowed_audio_formats or [
            "WAV",
            "MP3",
            "FLAC",
            "AAC",
            "OGG",
            "M4A",
        ]

        self.security_strict = security_strict

        # Security patterns
        self.suspicious_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"data:text/html",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
        ]

        # Known malicious file signatures
        self.malicious_signatures = {
            b"\x4d\x5a": "PE executable",
            b"\x7f\x45\x4c\x46": "ELF executable",
            b"\xfe\xed\xfa": "Mach-O executable",
        }

    def validate_media(
        self, media_data: Union[str, bytes], media_type: Optional[MediaType] = None
    ) -> ValidationResult:
        """Comprehensive media validation."""
        start_time = datetime.now()

        try:
            # Decode if base64
            if isinstance(media_data, str):
                if media_data.startswith("data:"):
                    # Extract media type and data from data URL
                    media_type_str, base64_data = media_data.split(",", 1)
                    detected_type = self._detect_media_type_from_data_url(
                        media_type_str
                    )
                    if media_type is None:
                        media_type = detected_type
                    media_bytes = base64.b64decode(base64_data)
                else:
                    media_bytes = base64.b64decode(media_data)
            else:
                media_bytes = media_data

            # Basic security checks
            issues = self._perform_security_checks(media_bytes)

            # Detect media type if not provided
            if media_type is None:
                media_type = self._detect_media_type(media_bytes)

            # Type-specific validation
            type_issues, metadata = self._validate_by_type(media_type, media_bytes)
            issues.extend(type_issues)

            # Calculate security score
            security_score = self._calculate_security_score(issues, media_bytes)

            # Determine if valid
            is_valid = all(
                issue.severity
                not in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
                for issue in issues
            )

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return ValidationResult(
                is_valid=is_valid,
                media_type=media_type,
                format=metadata.get("format", "unknown"),
                size_bytes=len(media_bytes),
                issues=issues,
                metadata=metadata,
                security_score=security_score,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Error validating media: {e}")
            return ValidationResult(
                is_valid=False,
                media_type=MediaType.UNKNOWN,
                format="unknown",
                size_bytes=0,
                issues=[
                    ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Validation failed: {str(e)}",
                        code="VALIDATION_ERROR",
                    )
                ],
                metadata={},
                security_score=0.0,
                processing_time_ms=0.0,
            )

    def _detect_media_type_from_data_url(self, data_url: str) -> MediaType:
        """Detect media type from data URL."""
        if "image/" in data_url:
            return MediaType.IMAGE
        elif "audio/" in data_url:
            return MediaType.AUDIO
        elif "video/" in data_url:
            return MediaType.VIDEO
        elif "text/" in data_url:
            return MediaType.DOCUMENT
        else:
            return MediaType.UNKNOWN

    def _detect_media_type(self, data: bytes) -> MediaType:
        """Detect media type from binary data."""
        # Check file signatures
        if data.startswith(b"\xff\xd8\xff"):
            return MediaType.IMAGE  # JPEG
        elif data.startswith(b"\x89PNG\r\n\x1a\n"):
            return MediaType.IMAGE  # PNG
        elif data.startswith(b"GIF8"):
            return MediaType.IMAGE  # GIF
        elif data.startswith(b"RIFF") and b"WAVE" in data[:12]:
            return MediaType.AUDIO  # WAV
        elif data.startswith(b"ID3") or data.startswith(b"\xff\xfb"):
            return MediaType.AUDIO  # MP3
        elif data.startswith(b"fLaC"):
            return MediaType.AUDIO  # FLAC
        elif data.startswith(b"ftypM4A"):
            return MediaType.AUDIO  # M4A
        elif data.startswith(b"%PDF"):
            return MediaType.DOCUMENT  # PDF
        elif data.startswith(b"PK\x03\x04"):
            return MediaType.DOCUMENT  # ZIP/Office
        else:
            return MediaType.UNKNOWN

    def _perform_security_checks(self, data: bytes) -> List[ValidationIssue]:
        """Perform security checks on media data."""
        issues = []

        # Check for malicious signatures
        for signature, description in self.malicious_signatures.items():
            if data.startswith(signature):
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Malicious file signature detected: {description}",
                        code="MALICIOUS_SIGNATURE",
                        details={
                            "signature": signature.hex(),
                            "description": description,
                        },
                    )
                )

        # Check for embedded scripts or suspicious content
        try:
            data_str = data.decode("utf-8", errors="ignore")
            for pattern in self.suspicious_patterns:
                if re.search(pattern, data_str, re.IGNORECASE):
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Suspicious content detected: {pattern}",
                            code="SUSPICIOUS_CONTENT",
                            details={"pattern": pattern},
                        )
                    )
        except:
            pass  # Binary data, skip text checks

        # Check for extremely large files
        size_mb = len(data) / (1024 * 1024)
        if size_mb > 100:  # 100MB limit
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Very large file: {size_mb:.1f}MB",
                    code="LARGE_FILE",
                    details={"size_mb": size_mb},
                )
            )

        return issues

    def _validate_by_type(
        self, media_type: MediaType, data: bytes
    ) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """Perform type-specific validation."""
        issues = []
        metadata = {}

        if media_type == MediaType.IMAGE:
            issues, metadata = self._validate_image(data)
        elif media_type == MediaType.AUDIO:
            issues, metadata = self._validate_audio(data)
        elif media_type == MediaType.VIDEO:
            issues, metadata = self._validate_video(data)
        elif media_type == MediaType.DOCUMENT:
            issues, metadata = self._validate_document(data)
        else:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Unknown media type",
                    code="UNKNOWN_TYPE",
                )
            )

        return issues, metadata

    def _validate_image(
        self, data: bytes
    ) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """Validate image data."""
        issues = []
        metadata = {}

        # Check size
        size_mb = len(data) / (1024 * 1024)
        if size_mb > self.max_image_size_mb:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Image too large: {size_mb:.1f}MB > {self.max_image_size_mb}MB",
                    code="IMAGE_TOO_LARGE",
                    details={"size_mb": size_mb, "max_size_mb": self.max_image_size_mb},
                )
            )

        if not IMAGE_LIBS_AVAILABLE:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Image libraries not available for detailed validation",
                    code="LIBRARY_UNAVAILABLE",
                )
            )
            return issues, {"size_bytes": len(data)}

        try:
            # Load and analyze image
            image = Image.open(io.BytesIO(data))

            metadata = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "has_transparency": "transparency" in image.info,
                "size_bytes": len(data),
            }

            # Check format
            if image.format and image.format.upper() not in self.allowed_image_formats:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Image format {image.format} not in allowed list",
                        code="UNALLOWED_FORMAT",
                        details={
                            "format": image.format,
                            "allowed": self.allowed_image_formats,
                        },
                    )
                )

            # Check dimensions
            if image.width > 10000 or image.height > 10000:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Very large image dimensions: {image.width}x{image.height}",
                        code="LARGE_DIMENSIONS",
                        details={"width": image.width, "height": image.height},
                    )
                )

            # Check for suspicious metadata
            if hasattr(image, "info") and image.info:
                suspicious_keys = ["exif", "xmp", "icc_profile"]
                for key in suspicious_keys:
                    if key in image.info:
                        issues.append(
                            ValidationIssue(
                                severity=ValidationSeverity.INFO,
                                message=f"Image contains {key} metadata",
                                code="METADATA_PRESENT",
                                details={"metadata_type": key},
                            )
                        )

        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Invalid image format: {str(e)}",
                    code="INVALID_IMAGE",
                    details={"error": str(e)},
                )
            )

        return issues, metadata

    def _validate_audio(
        self, data: bytes
    ) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """Validate audio data."""
        issues = []
        metadata = {}

        # Check size
        size_mb = len(data) / (1024 * 1024)
        if size_mb > self.max_audio_size_mb:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Audio too large: {size_mb:.1f}MB > {self.max_audio_size_mb}MB",
                    code="AUDIO_TOO_LARGE",
                    details={"size_mb": size_mb, "max_size_mb": self.max_audio_size_mb},
                )
            )

        if not AUDIO_LIBS_AVAILABLE:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Audio libraries not available for detailed validation",
                    code="LIBRARY_UNAVAILABLE",
                )
            )
            return issues, {"size_bytes": len(data)}

        try:
            # Load and analyze audio
            audio_segment = AudioSegment.from_file(io.BytesIO(data))

            metadata = {
                "duration_seconds": audio_segment.duration_seconds,
                "sample_rate": audio_segment.frame_rate,
                "channels": audio_segment.channels,
                "bit_depth": audio_segment.sample_width * 8,
                "format": "audio",
                "size_bytes": len(data),
            }

            # Check duration
            if audio_segment.duration_seconds > 600:  # 10 minutes
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Long audio duration: {audio_segment.duration_seconds:.1f}s",
                        code="LONG_DURATION",
                        details={"duration_seconds": audio_segment.duration_seconds},
                    )
                )

            # Check for very high sample rates (potential attack vector)
            if audio_segment.frame_rate > 192000:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Very high sample rate: {audio_segment.frame_rate}Hz",
                        code="HIGH_SAMPLE_RATE",
                        details={"sample_rate": audio_segment.frame_rate},
                    )
                )

        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Invalid audio format: {str(e)}",
                    code="INVALID_AUDIO",
                    details={"error": str(e)},
                )
            )

        return issues, metadata

    def _validate_video(
        self, data: bytes
    ) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """Validate video data."""
        issues = []
        metadata = {}

        # Check size
        size_mb = len(data) / (1024 * 1024)
        if size_mb > self.max_video_size_mb:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Video too large: {size_mb:.1f}MB > {self.max_video_size_mb}MB",
                    code="VIDEO_TOO_LARGE",
                    details={"size_mb": size_mb, "max_size_mb": self.max_video_size_mb},
                )
            )

        # Basic video validation (without video processing libraries)
        metadata = {
            "size_bytes": len(data),
            "format": "video",
        }

        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.INFO,
                message="Video validation limited - consider using specialized video libraries",
                code="LIMITED_VALIDATION",
            )
        )

        return issues, metadata

    def _validate_document(
        self, data: bytes
    ) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """Validate document data."""
        issues = []
        metadata = {}

        metadata = {
            "size_bytes": len(data),
            "format": "document",
        }

        # Check for embedded objects or macros
        try:
            data_str = data.decode("utf-8", errors="ignore").lower()

            # Check for common macro patterns
            macro_patterns = ["vba", "macro", "script", "javascript"]
            for pattern in macro_patterns:
                if pattern in data_str:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message=f"Document may contain {pattern}",
                            code="POTENTIAL_MACRO",
                            details={"pattern": pattern},
                        )
                    )
        except:
            pass

        return issues, metadata

    def _calculate_security_score(
        self, issues: List[ValidationIssue], data: bytes
    ) -> float:
        """Calculate security score based on validation issues."""
        if not issues:
            return 1.0

        # Start with perfect score
        score = 1.0

        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                score -= 0.5
            elif issue.severity == ValidationSeverity.ERROR:
                score -= 0.3
            elif issue.severity == ValidationSeverity.WARNING:
                score -= 0.1
            elif issue.severity == ValidationSeverity.INFO:
                score -= 0.05

        # Additional penalties for suspicious characteristics
        size_mb = len(data) / (1024 * 1024)
        if size_mb > 50:
            score -= 0.1
        if size_mb > 100:
            score -= 0.2

        return max(0.0, min(1.0, score))

    def sanitize_media(
        self, media_data: Union[str, bytes], media_type: MediaType
    ) -> bytes:
        """Sanitize media data for safe processing."""
        try:
            # Decode if base64
            if isinstance(media_data, str):
                if media_data.startswith("data:"):
                    media_data = media_data.split(",")[1]
                media_bytes = base64.b64decode(media_data)
            else:
                media_bytes = media_data

            # Basic sanitization - remove suspicious patterns
            if media_type == MediaType.IMAGE and IMAGE_LIBS_AVAILABLE:
                try:
                    # Re-save image to remove metadata
                    image = Image.open(io.BytesIO(media_bytes))
                    output = io.BytesIO()
                    image.save(output, format=image.format or "PNG")
                    return output.getvalue()
                except:
                    pass

            # For other types, return original data
            return media_bytes

        except Exception as e:
            logger.error(f"Error sanitizing media: {e}")
            return media_data if isinstance(media_data, bytes) else b""

    def batch_validate(
        self, media_list: List[Union[str, bytes]]
    ) -> List[ValidationResult]:
        """Validate multiple media files."""
        results = []

        for media_data in media_list:
            try:
                result = self.validate_media(media_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Error validating media in batch: {e}")
                results.append(
                    ValidationResult(
                        is_valid=False,
                        media_type=MediaType.UNKNOWN,
                        format="unknown",
                        size_bytes=0,
                        issues=[
                            ValidationIssue(
                                severity=ValidationSeverity.CRITICAL,
                                message=f"Batch validation error: {str(e)}",
                                code="BATCH_ERROR",
                            )
                        ],
                        metadata={},
                        security_score=0.0,
                        processing_time_ms=0.0,
                    )
                )

        return results
