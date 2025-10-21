"""
Django ORM Language Server Protocol support.

This module provides dynamic manager-aware completion for Django ORM operations.
"""

from .manager_analyzer import ManagerCapabilityAnalyzer
from .operation_provider import OperationProvider

__all__ = [
    "ManagerCapabilityAnalyzer",
    "OperationProvider",
]
