"""
Advanced audio processing for multi-modal LLM tasks.

This module provides comprehensive audio processing capabilities including
format conversion, analysis, feature extraction, and audio optimization.
"""

import base64
import io
import wave
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from enum import Enum
import numpy as np

try:
    import librosa
    import soundfile as sf
    from pydub import AudioSegment

    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    # Create a dummy AudioSegment class for type hints when pydub is not available
    class AudioSegment:
        pass

logger = logging.getLogger(__name__)


class AudioFormat(str, Enum):
    """Supported audio formats."""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"


class AudioQuality(str, Enum):
    """Audio quality levels."""

    LOW = "low"  # 8kHz, 16-bit
    MEDIUM = "medium"  # 16kHz, 16-bit
    HIGH = "high"  # 44.1kHz, 16-bit
    ULTRA = "ultra"  # 48kHz, 24-bit


@dataclass
class AudioMetadata:
    """Audio metadata and analysis results."""

    duration_seconds: float
    sample_rate: int
    channels: int
    bit_depth: int
    format: str
    size_bytes: int
    bitrate_kbps: Optional[int]

    # Audio analysis
    loudness_db: float
    peak_amplitude: float
    rms_amplitude: float
    zero_crossing_rate: float
    spectral_centroid: float
    spectral_bandwidth: float
    mfcc_features: List[float]

    # File info
    file_hash: str
    processing_time_ms: float


class AudioProcessor:
    """
    Advanced audio processor for multi-modal LLM tasks.

    This class provides comprehensive audio processing capabilities including
    format conversion, analysis, feature extraction, and audio optimization.
    """

    def __init__(self, max_size_mb: int = 25, max_duration_seconds: int = 300):
        self.max_size_mb = max_size_mb
        self.max_duration_seconds = max_duration_seconds

        if not AUDIO_LIBS_AVAILABLE:
            logger.warning(
                "Audio processing libraries not available. Install librosa, soundfile, and pydub for full functionality."
            )

        # Supported formats
        self.supported_formats = {
            "WAV": AudioFormat.WAV,
            "MP3": AudioFormat.MP3,
            "FLAC": AudioFormat.FLAC,
            "AAC": AudioFormat.AAC,
            "OGG": AudioFormat.OGG,
            "M4A": AudioFormat.M4A,
        }

    def validate_audio(self, audio_data: Union[str, bytes]) -> Tuple[bool, str]:
        """Validate audio data and return validation result."""
        try:
            if isinstance(audio_data, str):
                # Assume base64 encoded
                if audio_data.startswith("data:"):
                    # Remove data URL prefix
                    audio_data = audio_data.split(",")[1]
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = audio_data

            # Check size
            if len(audio_bytes) > self.max_size_mb * 1024 * 1024:
                return (
                    False,
                    f"Audio too large: {len(audio_bytes) / (1024*1024):.1f}MB > {self.max_size_mb}MB",
                )

            if not AUDIO_LIBS_AVAILABLE:
                return True, "Audio libraries not available for validation"

            # Try to load audio
            try:
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))

                # Check duration
                if audio_segment.duration_seconds > self.max_duration_seconds:
                    return (
                        False,
                        f"Audio too long: {audio_segment.duration_seconds:.1f}s > {self.max_duration_seconds}s",
                    )

                return True, "Audio validation successful"

            except Exception as e:
                return False, f"Invalid audio format: {str(e)}"

        except Exception as e:
            return False, f"Audio validation failed: {str(e)}"

    def process_audio(
        self,
        audio_data: Union[str, bytes],
        target_format: AudioFormat = AudioFormat.WAV,
        quality: AudioQuality = AudioQuality.MEDIUM,
        normalize: bool = True,
        remove_silence: bool = False,
    ) -> Tuple[bytes, AudioMetadata]:
        """Process and optimize audio data."""
        start_time = datetime.now()

        try:
            # Decode if base64
            if isinstance(audio_data, str):
                if audio_data.startswith("data:"):
                    audio_data = audio_data.split(",")[1]
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = audio_data

            if not AUDIO_LIBS_AVAILABLE:
                # Return original data with basic metadata
                metadata = AudioMetadata(
                    duration_seconds=0.0,
                    sample_rate=16000,
                    channels=1,
                    bit_depth=16,
                    format=target_format.value,
                    size_bytes=len(audio_bytes),
                    bitrate_kbps=None,
                    loudness_db=0.0,
                    peak_amplitude=0.0,
                    rms_amplitude=0.0,
                    zero_crossing_rate=0.0,
                    spectral_centroid=0.0,
                    spectral_bandwidth=0.0,
                    mfcc_features=[],
                    file_hash=hashlib.sha256(audio_bytes).hexdigest(),
                    processing_time_ms=0.0,
                )
                return audio_bytes, metadata

            # Load audio
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))

            # Apply processing
            processed_audio = self._apply_audio_processing(
                audio_segment, target_format, quality, normalize, remove_silence
            )

            # Convert to target format
            output_buffer = io.BytesIO()
            processed_audio.export(output_buffer, format=target_format.value.lower())
            processed_bytes = output_buffer.getvalue()

            # Generate metadata
            metadata = self._generate_audio_metadata(
                processed_audio, processed_bytes, start_time
            )

            return processed_bytes, metadata

        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            raise RuntimeError(f"Audio processing failed: {e}")

    def _apply_audio_processing(
        self,
        audio_segment: AudioSegment,
        target_format: AudioFormat,
        quality: AudioQuality,
        normalize: bool,
        remove_silence: bool,
    ) -> AudioSegment:
        """Apply audio processing operations."""
        processed = audio_segment

        # Normalize audio
        if normalize:
            processed = processed.normalize()

        # Remove silence
        if remove_silence:
            processed = self._remove_silence(processed)

        # Set quality parameters
        processed = self._set_audio_quality(processed, quality)

        return processed

    def _set_audio_quality(
        self, audio: AudioSegment, quality: AudioQuality
    ) -> AudioSegment:
        """Set audio quality parameters."""
        quality_params = {
            AudioQuality.LOW: {"sample_rate": 8000, "channels": 1},
            AudioQuality.MEDIUM: {"sample_rate": 16000, "channels": 1},
            AudioQuality.HIGH: {"sample_rate": 44100, "channels": 2},
            AudioQuality.ULTRA: {"sample_rate": 48000, "channels": 2},
        }

        params = quality_params.get(quality, quality_params[AudioQuality.MEDIUM])

        # Resample if needed
        if audio.frame_rate != params["sample_rate"]:
            audio = audio.set_frame_rate(params["sample_rate"])

        # Set channels
        if params["channels"] == 1 and audio.channels > 1:
            audio = audio.set_channels(1)
        elif params["channels"] == 2 and audio.channels == 1:
            audio = audio.set_channels(2)

        return audio

    def _remove_silence(
        self, audio: AudioSegment, silence_thresh: int = -50
    ) -> AudioSegment:
        """Remove silence from audio."""
        try:
            # Split audio into non-silent chunks
            chunks = AudioSegment.silence_detection(audio, silence_thresh)

            # Combine non-silent chunks
            if chunks:
                combined = chunks[0]
                for chunk in chunks[1:]:
                    combined += chunk
                return combined
            else:
                return audio
        except Exception:
            # Fallback: return original audio
            return audio

    def _generate_audio_metadata(
        self, audio: AudioSegment, audio_bytes: bytes, start_time: datetime
    ) -> AudioMetadata:
        """Generate comprehensive audio metadata."""
        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        # Basic metadata
        duration_seconds = audio.duration_seconds
        sample_rate = audio.frame_rate
        channels = audio.channels
        bit_depth = audio.sample_width * 8
        size_bytes = len(audio_bytes)
        bitrate_kbps = (
            int((size_bytes * 8) / duration_seconds / 1000)
            if duration_seconds > 0
            else None
        )

        # Audio analysis
        audio_analysis = self._analyze_audio_features(audio)

        return AudioMetadata(
            duration_seconds=duration_seconds,
            sample_rate=sample_rate,
            channels=channels,
            bit_depth=bit_depth,
            format=audio.frame_rate,
            size_bytes=size_bytes,
            bitrate_kbps=bitrate_kbps,
            loudness_db=audio.dBFS,
            peak_amplitude=audio.max_possible_amplitude,
            rms_amplitude=audio.rms,
            zero_crossing_rate=audio_analysis.get("zero_crossing_rate", 0.0),
            spectral_centroid=audio_analysis.get("spectral_centroid", 0.0),
            spectral_bandwidth=audio_analysis.get("spectral_bandwidth", 0.0),
            mfcc_features=audio_analysis.get("mfcc_features", []),
            file_hash=hashlib.sha256(audio_bytes).hexdigest(),
            processing_time_ms=processing_time,
        )

    def _analyze_audio_features(self, audio: AudioSegment) -> Dict[str, Any]:
        """Analyze audio features using librosa."""
        if not AUDIO_LIBS_AVAILABLE:
            return {}

        try:
            # Convert to numpy array
            audio_data = np.array(audio.get_array_of_samples())
            if audio.channels > 1:
                audio_data = audio_data.reshape((-1, audio.channels))
                audio_data = np.mean(audio_data, axis=1)  # Convert to mono

            # Normalize
            audio_data = audio_data.astype(np.float32) / audio.max_possible_amplitude

            # Calculate features
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio_data))

            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(
                y=audio_data, sr=audio.frame_rate
            )
            spectral_centroid = np.mean(spectral_centroids)

            spectral_bandwidths = librosa.feature.spectral_bandwidth(
                y=audio_data, sr=audio.frame_rate
            )
            spectral_bandwidth = np.mean(spectral_bandwidths)

            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=audio.frame_rate, n_mfcc=13)
            mfcc_features = np.mean(mfccs, axis=1).tolist()

            return {
                "zero_crossing_rate": float(zero_crossing_rate),
                "spectral_centroid": float(spectral_centroid),
                "spectral_bandwidth": float(spectral_bandwidth),
                "mfcc_features": mfcc_features,
            }

        except Exception as e:
            logger.warning(f"Error analyzing audio features: {e}")
            return {}

    def batch_process_audio(
        self,
        audio_list: List[Union[str, bytes]],
        target_format: AudioFormat = AudioFormat.WAV,
        quality: AudioQuality = AudioQuality.MEDIUM,
        **kwargs,
    ) -> List[Tuple[bytes, AudioMetadata]]:
        """Process multiple audio files."""
        results = []

        for audio_data in audio_list:
            try:
                result = self.process_audio(
                    audio_data, target_format, quality, **kwargs
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing audio in batch: {e}")
                # Add empty result to maintain list structure
                results.append(
                    (
                        b"",
                        AudioMetadata(
                            duration_seconds=0.0,
                            sample_rate=16000,
                            channels=1,
                            bit_depth=16,
                            format=target_format.value,
                            size_bytes=0,
                            bitrate_kbps=None,
                            loudness_db=0.0,
                            peak_amplitude=0.0,
                            rms_amplitude=0.0,
                            zero_crossing_rate=0.0,
                            spectral_centroid=0.0,
                            spectral_bandwidth=0.0,
                            mfcc_features=[],
                            file_hash="",
                            processing_time_ms=0.0,
                        ),
                    )
                )

        return results

    def extract_audio_features(self, audio_data: Union[str, bytes]) -> Dict[str, Any]:
        """Extract audio features for analysis."""
        try:
            _, metadata = self.process_audio(audio_data)

            return {
                "duration": metadata.duration_seconds,
                "loudness_db": metadata.loudness_db,
                "peak_amplitude": metadata.peak_amplitude,
                "rms_amplitude": metadata.rms_amplitude,
                "zero_crossing_rate": metadata.zero_crossing_rate,
                "spectral_centroid": metadata.spectral_centroid,
                "spectral_bandwidth": metadata.spectral_bandwidth,
                "mfcc_features": metadata.mfcc_features,
                "sample_rate": metadata.sample_rate,
                "channels": metadata.channels,
            }
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            return {}

    def get_audio_info(self, audio_data: Union[str, bytes]) -> Dict[str, Any]:
        """Get basic audio information."""
        try:
            if isinstance(audio_data, str):
                if audio_data.startswith("data:"):
                    audio_data = audio_data.split(",")[1]
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = audio_data

            if not AUDIO_LIBS_AVAILABLE:
                return {
                    "size_bytes": len(audio_bytes),
                    "format": "unknown",
                    "duration_seconds": 0.0,
                }

            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))

            return {
                "size_bytes": len(audio_bytes),
                "format": audio_segment.frame_rate,
                "duration_seconds": audio_segment.duration_seconds,
                "sample_rate": audio_segment.frame_rate,
                "channels": audio_segment.channels,
                "bit_depth": audio_segment.sample_width * 8,
            }

        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {"error": str(e)}

    def optimize_for_llm(
        self, audio_data: Union[str, bytes]
    ) -> Tuple[bytes, AudioMetadata]:
        """Optimize audio specifically for LLM processing."""
        return self.process_audio(
            audio_data,
            target_format=AudioFormat.WAV,
            quality=AudioQuality.MEDIUM,
            normalize=True,
            remove_silence=True,
        )
