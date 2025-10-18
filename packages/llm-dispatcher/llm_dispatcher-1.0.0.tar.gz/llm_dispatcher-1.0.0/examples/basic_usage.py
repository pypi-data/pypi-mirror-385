"""
Basic usage example for LLM-Dispatcher package.

This example demonstrates how to use the LLM-Dispatcher package for
intelligent LLM selection and dispatching.
"""

import asyncio
import os
from llm_dispatcher import llm_dispatcher, init, TaskType, OptimizationStrategy


# Example 1: Basic text generation with automatic LLM selection
@llm_dispatcher(task_type=TaskType.TEXT_GENERATION)
def generate_story(prompt: str) -> str:
    """Generate a story based on the prompt."""
    return prompt


# Example 2: Code generation with performance optimization
@llm_dispatcher(
    task_type=TaskType.CODE_GENERATION,
    optimization_strategy=OptimizationStrategy.PERFORMANCE,
)
def generate_code(description: str) -> str:
    """Generate code based on the description."""
    return description


# Example 3: Math problems with cost optimization
@llm_dispatcher(
    task_type=TaskType.MATH,
    optimization_strategy=OptimizationStrategy.COST,
    max_cost=0.01,
)
def solve_math_problem(problem: str) -> str:
    """Solve a math problem."""
    return problem


# Example 4: Vision analysis with specific providers
@llm_dispatcher(
    task_type=TaskType.VISION_ANALYSIS,
    providers=["openai", "anthropic"],  # Only use these providers
)
def analyze_image(image_path: str) -> str:
    """Analyze an image."""
    return f"Analyzing image: {image_path}"


# Example 5: Reasoning tasks with fallback disabled
@llm_dispatcher(
    task_type=TaskType.REASONING,
    fallback_enabled=False,
    max_latency=2000,  # 2 seconds max
)
def reason_about_problem(problem: str) -> str:
    """Reason about a complex problem."""
    return problem


async def main():
    """Main example function."""
    # Initialize LLM-Dispatcher with API keys
    # Note: In practice, you would set these as environment variables
    switch = init(
        openai_api_key=os.getenv("OPENAI_API_KEY", "sk-test-key"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "sk-ant-test-key"),
        google_api_key=os.getenv("GOOGLE_API_KEY", "test-key"),
    )

    print("LLM-Dispatcher initialized successfully!")
    print(f"Available providers: {list(switch.providers.keys())}")

    # Example 1: Generate a story
    print("\n=== Example 1: Story Generation ===")
    story_prompt = "Write a short story about a robot learning to paint"
    try:
        result = await generate_story(story_prompt)
        print(f"Generated story: {result}")
    except Exception as e:
        print(f"Error generating story: {e}")

    # Example 2: Generate code
    print("\n=== Example 2: Code Generation ===")
    code_prompt = "Write a Python function to calculate the factorial of a number"
    try:
        result = await generate_code(code_prompt)
        print(f"Generated code: {result}")
    except Exception as e:
        print(f"Error generating code: {e}")

    # Example 3: Solve math problem
    print("\n=== Example 3: Math Problem ===")
    math_prompt = "Solve the equation: 2x + 5 = 15"
    try:
        result = await solve_math_problem(math_prompt)
        print(f"Math solution: {result}")
    except Exception as e:
        print(f"Error solving math problem: {e}")

    # Example 4: Analyze image
    print("\n=== Example 4: Image Analysis ===")
    image_prompt = "Describe what you see in this image"
    try:
        result = await analyze_image(image_prompt)
        print(f"Image analysis: {result}")
    except Exception as e:
        print(f"Error analyzing image: {e}")

    # Example 5: Reasoning
    print("\n=== Example 5: Reasoning ===")
    reasoning_prompt = "Explain why renewable energy is important for the future"
    try:
        result = await reason_about_problem(reasoning_prompt)
        print(f"Reasoning result: {result}")
    except Exception as e:
        print(f"Error in reasoning: {e}")

    # Show system status
    print("\n=== System Status ===")
    status = switch.get_system_status()
    print(f"Total providers: {status['total_providers']}")
    print(f"Total models: {status['total_models']}")
    print(f"Optimization strategy: {status['optimization_strategy']}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
