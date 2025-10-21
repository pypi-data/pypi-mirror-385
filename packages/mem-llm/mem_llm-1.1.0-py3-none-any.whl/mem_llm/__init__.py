"""
Memory-LLM: Memory-Enabled Mini Assistant
AI library that remembers user interactions
"""

from .mem_agent import MemAgent
from .memory_manager import MemoryManager
from .llm_client import OllamaClient

# Tools (optional)
try:
    from .memory_tools import MemoryTools, ToolExecutor
    __all_tools__ = ["MemoryTools", "ToolExecutor"]
except ImportError:
    __all_tools__ = []

# Pro version imports (optional)
try:
    from .memory_db import SQLMemoryManager
    from .config_manager import get_config
    from .config_from_docs import create_config_from_document
    from .dynamic_prompt import dynamic_prompt_builder
    __all_pro__ = ["SQLMemoryManager", "get_config", "create_config_from_document", "dynamic_prompt_builder"]
except ImportError:
    __all_pro__ = []

# Security features (optional, v1.1.0+)
try:
    from .prompt_security import (
        PromptInjectionDetector,
        InputSanitizer,
        SecurePromptBuilder
    )
    __all_security__ = ["PromptInjectionDetector", "InputSanitizer", "SecurePromptBuilder"]
except ImportError:
    __all_security__ = []

# Enhanced features (v1.1.0+)
try:
    from .logger import get_logger, MemLLMLogger
    from .retry_handler import exponential_backoff_retry, SafeExecutor
    __all_enhanced__ = ["get_logger", "MemLLMLogger", "exponential_backoff_retry", "SafeExecutor"]
except ImportError:
    __all_enhanced__ = []

__version__ = "1.1.0"
__author__ = "C. Emre Karataş"

# CLI
try:
    from .cli import cli
    __all_cli__ = ["cli"]
except ImportError:
    __all_cli__ = []

__all__ = [
    "MemAgent",
    "MemoryManager", 
    "OllamaClient",
] + __all_tools__ + __all_pro__ + __all_cli__ + __all_security__ + __all_enhanced__