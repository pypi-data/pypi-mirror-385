"""
Setup script for LLM-Dispatcher package.

This script provides easy setup and installation of the LLM-Dispatcher package
with all its dependencies and configuration.
"""

from setuptools import setup, find_packages
import os


# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read requirements from pyproject.toml
def read_requirements():
    requirements = []
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            requirements = [
                line.strip() for line in fh if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        # Fallback to basic requirements if requirements.txt doesn't exist
        requirements = [
            "pydantic>=2.0.0",
            "requests>=2.31.0",
            "aiohttp>=3.8.0",
            "tenacity>=8.0.0",
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "google-generativeai>=0.3.0",
            "tiktoken>=0.5.0",
            "pillow>=9.0.0",
            "pydub>=0.25.0",
            "numpy>=1.21.0",
            "pyyaml>=6.0",
            "python-dotenv>=1.0.0",
        ]
    return requirements


setup(
    name="llm-dispatcher",
    version="1.0.0",
    author="ashhadahsan",
    author_email="ashhadahsan@gmail.com",
    description="Intelligent LLM dispatching with performance-based routing, multimodal support, streaming, monitoring, and comprehensive analytics",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ashhadahsan/llm-dispatcher",
    project_urls={
        "Bug Tracker": "https://github.com/ashhadahsan/llm-dispatcher/issues",
        "Documentation": "https://llm-dispatcher.readthedocs.io",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "pre-commit>=3.0.0",
            "jupyter>=1.0.0",
            "ipykernel>=6.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
        "benchmark": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "accelerate>=0.20.0",
            "datasets>=2.0.0",
            "evaluate>=0.4.0",
        ],
    },
    keywords=[
        "llm",
        "ai",
        "openai",
        "anthropic",
        "google",
        "machine-learning",
        "nlp",
        "routing",
        "dispatch",
        "multimodal",
        "streaming",
        "monitoring",
        "analytics",
        "caching",
    ],
    include_package_data=True,
    zip_safe=False,
)
