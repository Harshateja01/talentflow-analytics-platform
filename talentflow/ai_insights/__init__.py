"""AI-powered natural language insights module with deterministic safe fallbacks."""

from .engine import AIInsightsEngine
from .prompts import SUPPORTED_QUESTIONS

__all__ = ["AIInsightsEngine", "SUPPORTED_QUESTIONS"]
