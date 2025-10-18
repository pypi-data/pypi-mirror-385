# Multimodal Support

LLM-Dispatcher provides comprehensive support for multimodal AI tasks, including text, images, audio, and structured data processing.

## Overview

Multimodal support allows you to work with different types of media and data formats across various LLM providers. LLM-Dispatcher automatically routes multimodal requests to the most capable providers.

### Supported Media Types

| Media Type          | Supported Providers       | Capabilities                      |
| ------------------- | ------------------------- | --------------------------------- |
| **Text**            | All providers             | Generation, analysis, translation |
| **Images**          | OpenAI, Google, Anthropic | Analysis, description, OCR        |
| **Audio**           | OpenAI, Google            | Transcription, analysis           |
| **Structured Data** | All providers             | JSON, XML, CSV processing         |

## Image Processing

### Basic Image Analysis

```python
import base64
from llm_dispatcher import llm_dispatcher, TaskType

@llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)
def analyze_image(prompt: str, images: list) -> str:
    """Analyze images with vision-capable models."""
    return prompt

def encode_image(image_path: str) -> str:
    """Encode image to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Usage
image_data = encode_image("path/to/image.jpg")
result = analyze_image("What's in this image?", [image_data])
print(result)
```

### Multiple Image Analysis

```python
@llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)
def compare_images(prompt: str, images: list) -> str:
    """Compare multiple images."""
    return prompt

# Analyze multiple images
images = [
    encode_image("image1.jpg"),
    encode_image("image2.jpg"),
    encode_image("image3.jpg")
]

comparison = compare_images("Compare these three images and identify the differences", images)
print(comparison)
```

### Image Processing with Context

```python
@llm_dispatcher(
    task_type=TaskType.VISION_ANALYSIS,
    optimization_strategy="performance"
)
def detailed_image_analysis(prompt: str, images: list, context: dict = None) -> str:
    """Detailed image analysis with context."""
    return prompt

# Use with context
context = {
    "analysis_type": "medical",
    "focus_areas": ["anatomy", "abnormalities"],
    "detail_level": "high"
}

result = detailed_image_analysis(
    "Analyze this medical image for any abnormalities",
    [medical_image],
    context
)
```

## Audio Processing

### Audio Transcription

```python
@llm_dispatcher(task_type=TaskType.AUDIO_TRANSCRIPTION)
def transcribe_audio(prompt: str, audio: str) -> str:
    """Transcribe audio to text."""
    return prompt

def encode_audio(audio_path: str) -> str:
    """Encode audio to base64."""
    with open(audio_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Usage
audio_data = encode_audio("path/to/audio.mp3")
transcript = transcribe_audio("Transcribe this audio", audio_data)
print(transcript)
```

### Audio Analysis

```python
@llm_dispatcher(task_type=TaskType.AUDIO_ANALYSIS)
def analyze_audio(prompt: str, audio: str) -> str:
    """Analyze audio content."""
    return prompt

# Analyze audio
analysis = analyze_audio(
    "Analyze the sentiment and key topics in this audio",
    audio_data
)
print(analysis)
```

### Multi-Language Audio Processing

```python
@llm_dispatcher(
    task_type=TaskType.AUDIO_TRANSCRIPTION,
    providers=["openai", "google"]  # Both support multiple languages
)
def multilingual_transcription(prompt: str, audio: str, language: str = "auto") -> str:
    """Transcribe audio in multiple languages."""
    return prompt

# Transcribe in specific language
transcript = multilingual_transcription(
    "Transcribe this audio in Spanish",
    spanish_audio,
    language="es"
)
```

## Multimodal Analysis

### Text + Image Analysis

```python
@llm_dispatcher(task_type=TaskType.MULTIMODAL_ANALYSIS)
def analyze_text_and_image(prompt: str, images: list, text: str = None) -> str:
    """Analyze text and images together."""
    return prompt

# Analyze document with images
result = analyze_text_and_image(
    "Analyze this document and its images for key information",
    [document_image],
    text="This is a technical specification document."
)
```

### Audio + Image Analysis

```python
@llm_dispatcher(task_type=TaskType.MULTIMODAL_ANALYSIS)
def analyze_audio_and_image(prompt: str, audio: str, images: list) -> str:
    """Analyze audio and images together."""
    return prompt

# Analyze presentation with audio and slides
analysis = analyze_audio_and_image(
    "Analyze this presentation for key points and visual elements",
    presentation_audio,
    [slide1, slide2, slide3]
)
```

## Structured Data Processing

### JSON Processing

```python
@llm_dispatcher(task_type=TaskType.STRUCTURED_DATA_PROCESSING)
def process_json(prompt: str, json_data: str) -> str:
    """Process JSON data."""
    return prompt

import json

# Process JSON data
json_data = json.dumps({
    "users": [
        {"name": "John", "age": 30, "city": "New York"},
        {"name": "Jane", "age": 25, "city": "Los Angeles"}
    ]
})

result = process_json(
    "Analyze this user data and provide insights",
    json_data
)
```

### CSV Processing

```python
@llm_dispatcher(task_type=TaskType.STRUCTURED_DATA_PROCESSING)
def process_csv(prompt: str, csv_data: str) -> str:
    """Process CSV data."""
    return prompt

# Process CSV data
csv_data = """name,age,city
John,30,New York
Jane,25,Los Angeles
Bob,35,Chicago"""

result = process_csv(
    "Analyze this CSV data and provide statistics",
    csv_data
)
```

## Advanced Multimodal Features

### Custom Media Processing

```python
from llm_dispatcher.multimodal import ImageProcessor, AudioProcessor

class CustomMediaProcessor:
    def process_video(self, video_path: str) -> str:
        """Extract frames from video for analysis."""
        # Extract key frames
        frames = self.extract_frames(video_path)
        return frames

    def process_document(self, doc_path: str) -> dict:
        """Process document and extract text + images."""
        text = self.extract_text(doc_path)
        images = self.extract_images(doc_path)
        return {"text": text, "images": images}

# Use custom processor
processor = CustomMediaProcessor()

@llm_dispatcher(
    task_type=TaskType.MULTIMODAL_ANALYSIS,
    media_processor=processor
)
def analyze_video(prompt: str, video_path: str) -> str:
    """Analyze video content."""
    return prompt
```

### Batch Multimodal Processing

```python
async def batch_multimodal_processing(requests: list) -> list:
    """Process multiple multimodal requests efficiently."""
    switch = get_global_switch()

    # Group requests by media type for optimization
    grouped_requests = switch.group_by_media_type(requests)

    results = []
    for media_type, media_requests in grouped_requests.items():
        # Process each media type with appropriate provider
        media_results = await asyncio.gather(*[
            switch.process_multimodal_request(req) for req in media_requests
        ])
        results.extend(media_results)

    return results

# Usage
requests = [
    TaskRequest(prompt="Analyze image", images=[image1], task_type=TaskType.VISION_ANALYSIS),
    TaskRequest(prompt="Transcribe audio", audio=audio1, task_type=TaskType.AUDIO_TRANSCRIPTION),
    TaskRequest(prompt="Process document", images=[doc_image], task_type=TaskType.MULTIMODAL_ANALYSIS)
]

results = await batch_multimodal_processing(requests)
```

## Provider-Specific Capabilities

### OpenAI Vision

```python
@llm_dispatcher(
    task_type=TaskType.VISION_ANALYSIS,
    providers=["openai"],
    model="gpt-4-vision-preview"
)
def openai_vision_analysis(prompt: str, images: list) -> str:
    """Use OpenAI's vision capabilities."""
    return prompt

# OpenAI supports detailed image analysis
result = openai_vision_analysis(
    "Describe this image in detail, including colors, objects, and composition",
    [detailed_image]
)
```

### Google Multimodal

```python
@llm_dispatcher(
    task_type=TaskType.MULTIMODAL_ANALYSIS,
    providers=["google"],
    model="gemini-2.5-pro"
)
def google_multimodal_analysis(prompt: str, images: list, audio: str = None) -> str:
    """Use Google's multimodal capabilities."""
    return prompt

# Google supports text, images, and audio together
result = google_multimodal_analysis(
    "Analyze this presentation with audio and slides",
    [slide1, slide2],
    audio=presentation_audio
)
```

### Anthropic Vision

```python
@llm_dispatcher(
    task_type=TaskType.VISION_ANALYSIS,
    providers=["anthropic"],
    model="claude-3-opus"
)
def anthropic_vision_analysis(prompt: str, images: list) -> str:
    """Use Anthropic's vision capabilities."""
    return prompt

# Anthropic excels at detailed analysis
result = anthropic_vision_analysis(
    "Analyze this scientific diagram and explain the concepts",
    [scientific_diagram]
)
```

## Performance Optimization

### Media Size Optimization

```python
from llm_dispatcher.multimodal import MultimodalAnalyzer

# Optimize media before processing
analyzer = MultimodalAnalyzer()

@llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)
def optimized_image_analysis(prompt: str, images: list) -> str:
    """Image analysis with optimization."""
    return prompt
```

### Caching Multimodal Results

```python
from llm_dispatcher.cache import MultimodalCache

# Cache based on media content hash
cache = MultimodalCache(
    similarity_threshold=0.95,
    max_cache_size=500
)

@llm_dispatcher(
    task_type=TaskType.VISION_ANALYSIS,
    cache=cache
)
def cached_image_analysis(prompt: str, images: list) -> str:
    """Cached image analysis."""
    return prompt
```

## Error Handling

### Multimodal-Specific Errors

```python
from llm_dispatcher.exceptions import (
    MediaProcessingError,
    UnsupportedMediaTypeError,
    MediaSizeExceededError
)

@llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)
def robust_image_analysis(prompt: str, images: list) -> str:
    """Robust image analysis with error handling."""
    return prompt

try:
    result = robust_image_analysis("Analyze this image", [image_data])
except MediaProcessingError as e:
    print(f"Media processing failed: {e}")
    # Try with different provider or fallback
except UnsupportedMediaTypeError as e:
    print(f"Unsupported media type: {e}")
    # Convert to supported format
except MediaSizeExceededError as e:
    print(f"Media too large: {e}")
    # Optimize media size
```

## Best Practices

### 1. **Choose Appropriate Providers**

```python
# For detailed image analysis
@llm_dispatcher(
    task_type=TaskType.VISION_ANALYSIS,
    providers=["openai", "anthropic"]  # Best for detailed analysis
)
def detailed_analysis(prompt: str, images: list) -> str:
    return prompt

# For fast image processing
@llm_dispatcher(
    task_type=TaskType.VISION_ANALYSIS,
    providers=["google"]  # Fast and cost-effective
)
def fast_analysis(prompt: str, images: list) -> str:
    return prompt
```

### 2. **Optimize Media Size**

```python
# Always optimize large media files
def optimize_media(media_path: str) -> str:
    if media_path.endswith(('.jpg', '.png')):
        return resize_image(media_path, max_size=(1024, 1024))
    elif media_path.endswith(('.mp3', '.wav')):
        return compress_audio(media_path, max_duration=300)
    return media_path
```

### 3. **Use Appropriate Task Types**

```python
# Use specific task types for better routing
@llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)  # For images
def image_analysis(prompt: str, images: list) -> str:
    return prompt

@llm_dispatcher(task_type=TaskType.AUDIO_TRANSCRIPTION)  # For audio
def audio_transcription(prompt: str, audio: str) -> str:
    return prompt

@llm_dispatcher(task_type=TaskType.MULTIMODAL_ANALYSIS)  # For multiple media
def multimodal_analysis(prompt: str, images: list, audio: str) -> str:
    return prompt
```

### 4. **Handle Large Files Efficiently**

```python
# Process large files in chunks
async def process_large_video(video_path: str) -> str:
    chunks = extract_video_chunks(video_path, chunk_duration=60)
    results = []

    for chunk in chunks:
        result = await analyze_video_chunk("Analyze this video segment", chunk)
        results.append(result)

    return combine_results(results)
```

## Next Steps

- [:octicons-lightning-bolt-24: Streaming](streaming.md) - Real-time response streaming
- [:octicons-shield-check-24: Error Handling](error-handling.md) - Robust error handling
- [:octicons-chart-line-24: Performance Tips](performance.md) - Optimization strategies
- [:octicons-gear-24: Advanced Features](advanced-features.md) - Advanced capabilities
