# Streaming

LLM-Dispatcher provides comprehensive streaming support for real-time response generation across all supported providers.

## Overview

Streaming allows you to receive responses in real-time as they are generated, providing a better user experience for long-running tasks and enabling interactive applications.

### Benefits of Streaming

- **Real-time feedback** - Users see responses as they're generated
- **Better UX** - No waiting for complete responses
- **Interactive applications** - Enable real-time conversations
- **Progress indication** - Show generation progress
- **Lower perceived latency** - Responses appear faster

## Basic Streaming

### Simple Streaming

```python
from llm_dispatcher import llm_stream, TaskType

@llm_stream(task_type=TaskType.TEXT_GENERATION)
async def stream_text(prompt: str):
    """Stream text generation in real-time."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        "This is a streaming response. ",
        "Each chunk is delivered ",
        "as it becomes available. ",
        "This provides a better ",
        "user experience for long responses."
    ]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    async for chunk in stream_text("Write a long story about space exploration"):
        print(chunk, end="", flush=True)

# Run the async function
import asyncio
asyncio.run(main())
```

### Streaming with Metadata

```python
from llm_dispatcher import llm_stream_with_metadata, TaskType

@llm_stream_with_metadata(task_type=TaskType.TEXT_GENERATION)
async def stream_with_metadata(prompt: str):
    """Stream with additional metadata."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        {"chunk": "Chunk 1: ", "chunk_index": 0, "provider": "openai", "model": "gpt-4"},
        {"chunk": "Chunk 2: ", "chunk_index": 1, "provider": "openai", "model": "gpt-4"},
        {"chunk": "Chunk 3: ", "chunk_index": 2, "provider": "openai", "model": "gpt-4"}
    ]

    for chunk_data in chunks:
        yield chunk_data

# Usage
async def main():
    async for metadata in stream_with_metadata("Write a story"):
        print(f"[{metadata['provider']}:{metadata['model']}] {metadata['chunk']}")

asyncio.run(main())
```

## Advanced Streaming Features

### Streaming with Progress Tracking

```python
from llm_dispatcher import llm_stream
from llm_dispatcher.streaming import ProgressTracker

@llm_stream(
    task_type=TaskType.TEXT_GENERATION,
    progress_tracker=ProgressTracker()
)
async def stream_with_progress(prompt: str):
    """Stream with progress tracking."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Chunk 1", "Chunk 2", "Chunk 3", "Chunk 4", "Chunk 5"]

    for i, chunk in enumerate(chunks):
        yield chunk
        # Progress would be automatically tracked

# Usage with progress
async def main():
    progress_tracker = ProgressTracker()

    async for chunk in stream_with_progress("Write a detailed analysis"):
        print(chunk, end="", flush=True)
        print(f"\nProgress: {progress_tracker.get_progress():.1f}%")

asyncio.run(main())
```

### Streaming with Callbacks

```python
from llm_dispatcher import llm_stream
from llm_dispatcher.streaming import StreamingCallbacks

def on_chunk_received(chunk: str, metadata: dict):
    """Callback when a chunk is received."""
    print(f"Received chunk: {chunk[:50]}...")

def on_stream_start(metadata: dict):
    """Callback when streaming starts."""
    print(f"Streaming started with {metadata['provider']}:{metadata['model']}")

def on_stream_end(metadata: dict):
    """Callback when streaming ends."""
    print(f"Streaming completed. Total tokens: {metadata['total_tokens']}")

callbacks = StreamingCallbacks(
    on_chunk_received=on_chunk_received,
    on_stream_start=on_stream_start,
    on_stream_end=on_stream_end
)

@llm_stream(
    task_type=TaskType.TEXT_GENERATION,
    callbacks=callbacks
)
async def stream_with_callbacks(prompt: str):
    """Stream with custom callbacks."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    async for chunk in stream_with_callbacks("Write a story"):
        # Chunks are automatically processed by callbacks
        pass

asyncio.run(main())
```

## Provider-Specific Streaming

### OpenAI Streaming

```python
@llm_stream(
    task_type=TaskType.TEXT_GENERATION,
    providers=["openai"],
    model="gpt-4"
)
async def openai_stream(prompt: str):
    """Stream using OpenAI's streaming API."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["OpenAI", " streaming", " response", " chunks"]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    async for chunk in openai_stream("Write a technical explanation"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

### Anthropic Streaming

```python
@llm_stream(
    task_type=TaskType.TEXT_GENERATION,
    providers=["anthropic"],
    model="claude-3-sonnet"
)
async def anthropic_stream(prompt: str):
    """Stream using Anthropic's streaming API."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Anthropic", " streaming", " response", " chunks"]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    async for chunk in anthropic_stream("Write a creative story"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

### Google Streaming

```python
@llm_stream(
    task_type=TaskType.TEXT_GENERATION,
    providers=["google"],
    model="gemini-2.5-pro"
)
async def google_stream(prompt: str):
    """Stream using Google's streaming API."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Google", " streaming", " response", " chunks"]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    async for chunk in google_stream("Write a summary"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

## Multimodal Streaming

### Image + Text Streaming

```python
@llm_stream(task_type=TaskType.VISION_ANALYSIS)
async def stream_image_analysis(prompt: str, images: list):
    """Stream image analysis with text."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        "Analyzing image... ",
        "I can see ",
        "various objects ",
        "and details. ",
        "The image shows... "
    ]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    image_data = encode_image("path/to/image.jpg")
    async for chunk in stream_image_analysis("Describe this image", [image_data]):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

### Audio Streaming

```python
@llm_stream(task_type=TaskType.AUDIO_TRANSCRIPTION)
async def stream_audio_transcription(prompt: str, audio: str):
    """Stream audio transcription."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        "Transcribing audio... ",
        "I can hear ",
        "the speaker saying ",
        "various words. ",
        "The transcription is... "
    ]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    audio_data = encode_audio("path/to/audio.mp3")
    async for chunk in stream_audio_transcription("Transcribe this audio", audio_data):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

## Error Handling in Streaming

### Robust Streaming with Error Handling

```python
from llm_dispatcher.exceptions import StreamingError, ProviderError

@llm_stream(
    task_type=TaskType.TEXT_GENERATION,
    fallback_enabled=True,
    max_retries=3
)
async def robust_stream(prompt: str):
    """Stream with error handling and fallback."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Robust", " streaming", " with", " error", " handling"]

    for chunk in chunks:
        yield chunk

# Usage with error handling
async def main():
    try:
        async for chunk in robust_stream("Write a story"):
            print(chunk, end="", flush=True)
    except StreamingError as e:
        print(f"Streaming error: {e}")
        # Handle streaming-specific errors
    except ProviderError as e:
        print(f"Provider error: {e}")
        # Handle provider errors
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle other errors

asyncio.run(main())
```

### Streaming with Timeout

```python
@llm_stream(
    task_type=TaskType.TEXT_GENERATION,
    timeout=30,  # 30 seconds timeout
    fallback_enabled=True
)
async def stream_with_timeout(prompt: str):
    """Stream with timeout protection."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Streaming", " with", " timeout", " protection"]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    try:
        async for chunk in stream_with_timeout("Write a long story"):
            print(chunk, end="", flush=True)
    except asyncio.TimeoutError:
        print("Streaming timed out")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
```

## Performance Optimization

### Batch Streaming

```python
async def batch_stream(requests: list):
    """Stream multiple requests efficiently."""
    switch = get_global_switch()

    # Group requests by provider for efficiency
    grouped_requests = switch.group_requests_by_provider(requests)

    for provider, provider_requests in grouped_requests.items():
        # Stream each provider's requests
        for request in provider_requests:
            async for chunk in switch.stream_request(request):
                yield chunk

# Usage
requests = [
    TaskRequest(prompt="Write a story", task_type=TaskType.TEXT_GENERATION),
    TaskRequest(prompt="Explain AI", task_type=TaskType.TEXT_GENERATION),
    TaskRequest(prompt="Code example", task_type=TaskType.CODE_GENERATION)
]

async def main():
    async for chunk in batch_stream(requests):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

### Streaming with Caching

```python
from llm_dispatcher.cache import StreamingCache

# Cache streaming responses
cache = StreamingCache(
    similarity_threshold=0.95,
    max_cache_size=100
)

@llm_stream(
    task_type=TaskType.TEXT_GENERATION,
    cache=cache
)
async def cached_stream(prompt: str):
    """Stream with caching for similar requests."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Cached", " streaming", " response"]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    async for chunk in cached_stream("Write a story about AI"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

## Real-World Examples

### Chat Application

```python
@llm_stream(task_type=TaskType.TEXT_GENERATION)
async def chat_response(message: str, conversation_history: list = None):
    """Generate chat response with streaming."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        "I understand your question. ",
        "Let me provide you with ",
        "a comprehensive answer. ",
        "Based on the context, ",
        "here's what I think..."
    ]

    for chunk in chunks:
        yield chunk

# Usage in chat application
async def handle_chat_message(message: str):
    print("Assistant: ", end="", flush=True)
    async for chunk in chat_response(message):
        print(chunk, end="", flush=True)
    print()  # New line after response

# Simulate chat
async def main():
    await handle_chat_message("What is artificial intelligence?")
    await handle_chat_message("How does machine learning work?")

asyncio.run(main())
```

### Code Generation with Streaming

```python
@llm_stream(task_type=TaskType.CODE_GENERATION)
async def stream_code_generation(description: str, language: str = "python"):
    """Generate code with streaming."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        f"# {description}\n",
        f"def {description.lower().replace(' ', '_')}():\n",
        "    \"\"\"Generated function.\"\"\"\n",
        "    # Implementation here\n",
        "    pass\n"
    ]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    print("Generated code:")
    async for chunk in stream_code_generation("Create a function to sort a list", "python"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

### Content Generation with Progress

```python
from llm_dispatcher.streaming import ProgressTracker

@llm_stream(
    task_type=TaskType.TEXT_GENERATION,
    progress_tracker=ProgressTracker()
)
async def stream_content_generation(topic: str, length: str = "medium"):
    """Generate content with progress tracking."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        f"# {topic}\n\n",
        "## Introduction\n",
        "This article explores ",
        f"the topic of {topic}. ",
        "Let's dive into the details...\n\n",
        "## Main Content\n",
        "The key points to consider ",
        "are as follows...\n\n",
        "## Conclusion\n",
        "In summary, ",
        f"{topic} is an important topic ",
        "that deserves attention."
    ]

    for chunk in chunks:
        yield chunk

# Usage with progress
async def main():
    progress_tracker = ProgressTracker()

    print("Generating content...")
    async for chunk in stream_content_generation("Artificial Intelligence", "long"):
        print(chunk, end="", flush=True)
        progress = progress_tracker.get_progress()
        if progress > 0:
            print(f"\nProgress: {progress:.1f}%", end="\r", flush=True)

asyncio.run(main())
```

## Best Practices

### 1. **Handle Streaming Errors Gracefully**

```python
async def safe_stream(prompt: str):
    """Stream with proper error handling."""
    try:
        async for chunk in stream_text(prompt):
            print(chunk, end="", flush=True)
    except StreamingError as e:
        print(f"\nStreaming error: {e}")
        # Implement fallback or retry logic
    except Exception as e:
        print(f"\nUnexpected error: {e}")
```

### 2. **Use Appropriate Timeouts**

```python
@llm_stream(timeout=60)  # Set reasonable timeout
async def stream_with_timeout(prompt: str):
    return prompt
```

### 3. **Implement Progress Feedback**

```python
# Always provide progress feedback for long streams
progress_tracker = ProgressTracker()
async for chunk in stream_with_progress(prompt):
    print(chunk, end="", flush=True)
    print(f"\nProgress: {progress_tracker.get_progress():.1f}%", end="\r")
```

### 4. **Use Callbacks for Complex Logic**

```python
# Use callbacks for complex processing
callbacks = StreamingCallbacks(
    on_chunk_received=process_chunk,
    on_stream_start=log_stream_start,
    on_stream_end=log_stream_end
)
```

### 5. **Optimize for Performance**

```python
# Use caching for similar requests
@llm_stream(cache=StreamingCache())
async def cached_stream(prompt: str):
    return prompt
```

## Next Steps

- [:octicons-shield-check-24: Error Handling](error-handling.md) - Robust error handling
- [:octicons-chart-line-24: Performance Tips](performance.md) - Optimization strategies
- [:octicons-gear-24: Advanced Features](advanced-features.md) - Advanced capabilities
- [:octicons-eye-24: Multimodal Support](multimodal.md) - Working with images and audio
