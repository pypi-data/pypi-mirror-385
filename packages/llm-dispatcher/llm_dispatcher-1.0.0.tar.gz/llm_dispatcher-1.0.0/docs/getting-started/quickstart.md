# Quick Start

Get up and running with LLM-Dispatcher in minutes!

## Basic Usage

### Simple Text Generation

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
def generate_text(prompt: str) -> str:
    """Automatically routed to the best LLM for text generation."""
    return prompt

# Usage
result = generate_text("Write a story about a robot")
print(result)
```

### With Task Types

```python
from llm_dispatcher import llm_dispatcher, TaskType

@llm_dispatcher(task_type=TaskType.CODE_GENERATION)
def generate_code(description: str) -> str:
    """Automatically uses the best model for code generation."""
    return description

@llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)
def analyze_image(prompt: str, image_path: str) -> str:
    """Automatically uses vision-capable models."""
    return prompt

# Usage
code = generate_code("Create a Python function to sort a list")
analysis = analyze_image("Describe this image", "path/to/image.jpg")
```

## Advanced Configuration

### Custom Switch Instance

```python
from llm_dispatcher import LLMSwitch, TaskType

# Initialize with custom configuration
switch = LLMSwitch(
    providers={
        "openai": {"api_key": "sk-..."},
        "anthropic": {"api_key": "sk-ant-..."},
        "google": {"api_key": "..."}
    },
    config={
        "prefer_cost_efficiency": True,
        "max_latency_ms": 2000,
        "fallback_enabled": True
    }
)

@switch.route(task_type=TaskType.CODE_GENERATION)
def generate_code(description: str) -> str:
    """Uses the configured switch instance."""
    return description
```

### Cost and Performance Limits

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher(
    max_cost=0.05,  # Maximum cost per request
    max_latency=3000,  # Maximum latency in milliseconds
    fallback_enabled=True
)
def generate_with_limits(prompt: str) -> str:
    """Generation with cost and performance constraints."""
    return prompt
```

## Multimodal Examples

### Image Analysis

```python
import base64
from llm_dispatcher import llm_dispatcher, TaskType

@llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)
def analyze_image(prompt: str, images: list) -> str:
    """Analyze images with vision-capable models."""
    return prompt

# Usage with base64 encoded images
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

result = analyze_image("What's in this image?", [image_data])
```

### Audio Processing

```python
@llm_dispatcher(task_type=TaskType.AUDIO_TRANSCRIPTION)
def transcribe_audio(prompt: str, audio: str) -> str:
    """Transcribe audio with appropriate models."""
    return prompt

# Usage with base64 encoded audio
with open("audio.mp3", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

transcript = transcribe_audio("Transcribe this audio", audio_data)
```

## Streaming Responses

### Basic Streaming

```python
from llm_dispatcher import llm_stream

@llm_stream(task_type=TaskType.TEXT_GENERATION)
async def stream_text(prompt: str):
    """Stream text generation in real-time."""
    # This is a placeholder - actual streaming would be handled internally
    yield "Streaming response chunk 1"
    yield "Streaming response chunk 2"
    yield "Streaming response chunk 3"

# Usage
async for chunk in stream_text("Write a long story"):
    print(chunk, end="")
```

### Streaming with Metadata

```python
from llm_dispatcher import llm_stream_with_metadata

@llm_stream_with_metadata(task_type=TaskType.TEXT_GENERATION)
async def stream_with_metadata(prompt: str):
    """Stream with additional metadata."""
    # This is a placeholder - actual streaming would be handled internally
    yield {"chunk": "Chunk 1", "chunk_index": 0, "provider": "openai"}
    yield {"chunk": "Chunk 2", "chunk_index": 1, "provider": "openai"}

# Usage
async for metadata in stream_with_metadata("Write a story"):
    print(f"Chunk {metadata['chunk_index']}: {metadata['chunk']}")
```

## Error Handling

### Basic Error Handling

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.exceptions import LLMDispatcherError

@llm_dispatcher(fallback_enabled=True)
def reliable_generation(prompt: str) -> str:
    """Generation with automatic fallback."""
    return prompt

try:
    result = reliable_generation("Your prompt here")
except LLMDispatcherError as e:
    print(f"Error: {e}")
    # Handle fallback or retry logic
```

### Custom Error Handling

```python
@llm_dispatcher(
    fallback_enabled=True,
    providers=["openai", "google"],  # Try these in order
    max_retries=3
)
def robust_generation(prompt: str) -> str:
    """Generation with custom retry logic."""
    return prompt
```

## Performance Optimization

### Cost Optimization

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.config.settings import OptimizationStrategy

@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.COST,
    max_cost=0.01
)
def cost_optimized_generation(prompt: str) -> str:
    """Optimized for cost efficiency."""
    return prompt
```

### Speed Optimization

```python
@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.SPEED,
    max_latency=1000
)
def speed_optimized_generation(prompt: str) -> str:
    """Optimized for speed."""
    return prompt
```

### Quality Optimization

```python
@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.PERFORMANCE
)
def quality_optimized_generation(prompt: str) -> str:
    """Optimized for best quality."""
    return prompt
```

## Monitoring and Analytics

### System Status

```python
from llm_dispatcher import get_global_switch

# Get system status
switch = get_global_switch()
status = switch.get_system_status()
print(f"Providers: {status['total_providers']}")
print(f"Models: {status['total_models']}")

# Get decision weights
weights = switch.get_decision_weights()
print(f"Decision weights: {weights}")
```

### Task Analysis

```python
from llm_dispatcher.core.base import TaskRequest

# See which model would be selected
request = TaskRequest(
    prompt="Write a story",
    task_type=TaskType.TEXT_GENERATION
)

decision = await switch.select_llm(request)
print(f"Selected: {decision.provider}:{decision.model}")
print(f"Confidence: {decision.confidence}")
print(f"Reasoning: {decision.reasoning}")
```

## Configuration File

Create a `config.yaml` file for persistent configuration:

```yaml
# config.yaml
switching_rules:
  optimization_strategy: "balanced"
  max_latency_ms: 5000
  max_cost_per_request: 0.10
  fallback_enabled: true

monitoring:
  enable_monitoring: true
  performance_window_hours: 24

providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    models: ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    models: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
  google:
    api_key: "${GOOGLE_API_KEY}"
    models: ["gemini-2.5-pro", "gemini-2.5-flash"]
```

Load configuration:

```python
from llm_dispatcher import init_config

# Initialize with config file
switch = init_config("config.yaml")
```

## Next Steps

Now that you have the basics, explore:

- [:octicons-gear-24: Advanced Configuration](configuration.md) - Detailed configuration options
- [:octicons-eye-24: Multimodal Support](../user-guide/multimodal.md) - Working with images and audio
- [:octicons-lightning-bolt-24: Streaming](../user-guide/streaming.md) - Real-time response streaming
- [:octicons-shield-check-24: Error Handling](../user-guide/error-handling.md) - Robust error handling
- [:octicons-chart-line-24: Performance Tips](../user-guide/performance.md) - Optimization strategies

