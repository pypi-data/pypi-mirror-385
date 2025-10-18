"""
Environment and setup tests for LLM-Dispatcher package.

This module tests the environment setup, configuration loading,
and basic package functionality.
"""

import pytest
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestEnvironmentSetup:
    """Test environment setup and configuration."""

    def test_dotenv_loading(self):
        """Test that dotenv can load environment variables."""
        # Load environment variables
        load_dotenv()

        # Check that we can access environment variables
        assert os.getenv("OPENAI_API_KEY") is not None
        # Note: The actual value might be "your_openai_api_key_here" for testing

    def test_package_imports(self):
        """Test that all package modules can be imported."""
        try:
            from llm_dispatcher import (
                LLMSwitch,
                llm_dispatcher,
                LLMProvider,
                TaskType,
                Capability,
                BenchmarkManager,
                SwitchConfig,
                init_config,
                get_config,
            )

            assert True  # If we get here, imports worked
        except ImportError as e:
            pytest.fail(f"Failed to import package modules: {e}")

    def test_core_imports(self):
        """Test that core modules can be imported."""
        try:
            from llm_dispatcher.core.base import (
                TaskRequest,
                TaskResponse,
                ModelInfo,
                PerformanceMetrics,
            )
            from llm_dispatcher.core.switch_engine import LLMSwitch

            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import core modules: {e}")

    def test_provider_imports(self):
        """Test that provider modules can be imported."""
        try:
            from llm_dispatcher.providers.openai_provider import OpenAIProvider
            from llm_dispatcher.providers.anthropic_provider import AnthropicProvider
            from llm_dispatcher.providers.google_provider import GoogleProvider
            from llm_dispatcher.providers.base_provider import BaseProvider

            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import provider modules: {e}")

    def test_utils_imports(self):
        """Test that utility modules can be imported."""
        try:
            from llm_dispatcher.utils.benchmark_manager import BenchmarkManager
            from llm_dispatcher.utils.cost_calculator import CostCalculator
            from llm_dispatcher.utils.performance_monitor import PerformanceMonitor
            from llm_dispatcher.utils.task_classifier import TaskClassifier
            from llm_dispatcher.utils.token_counter import TokenCounter

            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import utility modules: {e}")

    def test_config_imports(self):
        """Test that configuration modules can be imported."""
        try:
            from llm_dispatcher.config.settings import SwitchConfig, ProviderConfig
            from llm_dispatcher.config.config_loader import init_config, get_config

            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import configuration modules: {e}")

    def test_decorator_imports(self):
        """Test that decorator modules can be imported."""
        try:
            from llm_dispatcher.decorators.switch_decorator import llm_dispatcher

            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import decorator modules: {e}")


class TestPackageVersion:
    """Test package version and metadata."""

    def test_package_version(self):
        """Test that package version is accessible."""
        from llm_dispatcher import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_package_author(self):
        """Test that package author information is accessible."""
        from llm_dispatcher import __author__, __email__

        assert __author__ is not None
        assert __email__ is not None
        assert isinstance(__author__, str)
        assert isinstance(__email__, str)

    def test_package_all_exports(self):
        """Test that __all__ exports are properly defined."""
        from llm_dispatcher import __all__

        assert isinstance(__all__, list)
        assert len(__all__) > 0

        # Check that all exports are strings
        for export in __all__:
            assert isinstance(export, str)
            assert len(export) > 0


class TestBasicFunctionality:
    """Test basic package functionality."""

    def test_task_type_enum(self):
        """Test that TaskType enum works correctly."""
        from llm_dispatcher.core.base import TaskType

        # Test that we can access task types
        assert TaskType.TEXT_GENERATION == "text_generation"
        assert TaskType.CODE_GENERATION == "code_generation"
        assert TaskType.VISION_ANALYSIS == "vision_analysis"
        assert TaskType.MATH == "math"

        # Test that we can iterate over task types
        task_types = list(TaskType)
        assert len(task_types) > 0

    def test_capability_enum(self):
        """Test that Capability enum works correctly."""
        from llm_dispatcher.core.base import Capability

        # Test that we can access capabilities
        assert Capability.TEXT == "text"
        assert Capability.VISION == "vision"
        assert Capability.AUDIO == "audio"
        assert Capability.CODE == "code"

        # Test that we can iterate over capabilities
        capabilities = list(Capability)
        assert len(capabilities) > 0

    def test_task_request_creation(self):
        """Test that TaskRequest can be created."""
        from llm_dispatcher.core.base import TaskRequest, TaskType

        request = TaskRequest(prompt="Test prompt", task_type=TaskType.TEXT_GENERATION)

        assert request.prompt == "Test prompt"
        assert request.task_type == TaskType.TEXT_GENERATION
        assert request.temperature == 0.7  # Default value

    def test_benchmark_manager_creation(self):
        """Test that BenchmarkManager can be created."""
        from llm_dispatcher.utils.benchmark_manager import BenchmarkManager

        manager = BenchmarkManager()
        assert manager is not None
        assert len(manager.benchmark_data) > 0

    def test_switch_config_creation(self):
        """Test that SwitchConfig can be created."""
        from llm_dispatcher.config.settings import SwitchConfig

        config = SwitchConfig()
        assert config is not None
        assert config.switching_rules is not None


class TestEnvironmentVariables:
    """Test environment variable handling."""

    def test_openai_api_key_env_var(self):
        """Test that OPENAI_API_KEY environment variable is accessible."""
        api_key = os.getenv("OPENAI_API_KEY")
        assert api_key is not None
        # Note: The value might be a placeholder for testing

    def test_other_api_keys_env_vars(self):
        """Test that other API key environment variables are accessible."""
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")
        xai_key = os.getenv("XAI_API_KEY")

        # These might be None if not set, which is okay for testing
        assert isinstance(anthropic_key, (str, type(None)))
        assert isinstance(google_key, (str, type(None)))
        assert isinstance(xai_key, (str, type(None)))

    def test_config_env_vars(self):
        """Test that configuration environment variables are accessible."""
        config_path = os.getenv("LLM_DISPATCHER_CONFIG_PATH")
        log_level = os.getenv("LLM_DISPATCHER_LOG_LEVEL")

        # These might be None if not set, which is okay for testing
        assert isinstance(config_path, (str, type(None)))
        assert isinstance(log_level, (str, type(None)))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
