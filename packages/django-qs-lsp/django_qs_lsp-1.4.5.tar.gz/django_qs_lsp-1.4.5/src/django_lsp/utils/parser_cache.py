"""
Simple parser cache for managing Tree-sitter parser instances.

This module provides a simple caching mechanism for parser instances
with proper lifecycle management and workspace isolation.
"""

import threading
from typing import Optional
from weakref import WeakValueDictionary

from .simple_tree_sitter_parser import TreeSitterParser


class ParserCache:
    """
    Simple cache for Tree-sitter parser instances.

    This cache ensures:
    - One parser instance per workspace
    - Proper cleanup when workspaces are removed
    - Thread-safe access to parsers
    - Memory-efficient storage using weak references
    """

    def __init__(self) -> None:
        # Use WeakValueDictionary to allow garbage collection of unused parsers
        self._parsers: WeakValueDictionary[str, TreeSitterParser] = (
            WeakValueDictionary()
        )
        self._lock = threading.RLock()

    def get_parser(self, workspace_root: str) -> Optional[TreeSitterParser]:
        """
        Get or create a SimpleTreeSitterParser for the given workspace.

        Args:
            workspace_root: Path to the workspace root

        Returns:
            Parser instance or None if creation fails
        """
        with self._lock:
            if workspace_root in self._parsers:
                return self._parsers[workspace_root]

            try:
                parser = TreeSitterParser()
                if (
                    parser.language and parser.parser
                ):  # Verify parser is properly initialized
                    self._parsers[workspace_root] = parser
                    return parser
            except Exception:
                pass

            return None

    def clear_workspace(self, workspace_root: str) -> None:
        """
        Clear parser for a specific workspace.

        Args:
            workspace_root: Path to the workspace root
        """
        with self._lock:
            self._parsers.pop(workspace_root, None)

    def clear_all(self) -> None:
        """Clear all parser instances."""
        with self._lock:
            self._parsers.clear()

    def get_workspace_count(self) -> int:
        """Get the number of workspaces with parsers."""
        with self._lock:
            return len(self._parsers)


# Global parser cache instance
_parser_cache = ParserCache()


def get_parser_cache() -> ParserCache:
    """Get the global parser cache instance."""
    return _parser_cache


def get_parser(workspace_root: str) -> Optional[TreeSitterParser]:
    """
    Get a parser for the given workspace.

    This is a convenience function that uses the global cache.
    """
    return _parser_cache.get_parser(workspace_root)


def clear_workspace_parser(workspace_root: str) -> None:
    """Clear parser for a specific workspace."""
    _parser_cache.clear_workspace(workspace_root)


def clear_all_parsers() -> None:
    """Clear all parser instances."""
    _parser_cache.clear_all()
