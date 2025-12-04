"""
Historical metrics tracking module for image comparison.

This module provides database persistence, composite metrics calculation,
statistical analysis, and anomaly detection for image comparison results
over time.
"""

from .database import Database
from .retention import RetentionPolicy

# Import HistoryManager only if models are available
try:
    from .history_manager import HistoryManager
    __all__ = ["Database", "HistoryManager", "RetentionPolicy"]
except (ImportError, ValueError):
    # Models not available yet (during initial setup or testing)
    __all__ = ["Database", "RetentionPolicy"]
