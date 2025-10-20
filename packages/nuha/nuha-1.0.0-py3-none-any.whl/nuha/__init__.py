"""Nuha - AI-Powered Terminal Assistant."""

__version__ = "1.0.0"
__author__ = "Nuha Team"
__email__ = "support@nuha.ai"

from nuha.core.ai_client import AIClient
from nuha.core.config import Config

__all__ = ["AIClient", "Config", "__version__"]
