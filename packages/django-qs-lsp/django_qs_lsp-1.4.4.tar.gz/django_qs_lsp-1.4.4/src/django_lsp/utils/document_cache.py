"""
Document cache manager for efficient model loading and caching.

This module provides intelligent caching of Django models and document information
to avoid reloading models on every completion request.
"""

import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from ..core.model_loader import ModelLoader
from ..utils.logging import get_debug_logger

debug_logger = get_debug_logger("document_cache")


@dataclass
class ORMOperation:
    """Represents an ORM operation with its position and context."""

    range_start_line: int
    range_start_character: int
    range_end_line: int
    range_end_character: int
    model_name: str
    manager_name: str
    operation_name: str
    context_type: str  # "filter", "exclude", "get", "annotate", etc.
    field_name: Optional[str] = None
    lookup_name: Optional[str] = None


class DocumentCache:
    """
    Cache manager for documents and Django models.

    This cache ensures:
    - Models are loaded once per workspace and cached
    - Document information is cached with proper invalidation
    - ORM operations are cached with position ranges for fast lookup
    - Memory-efficient storage using weak references
    - Thread-safe access to cached data
    """

    def __init__(self, model_loader: ModelLoader) -> None:
        self.model_loader = model_loader

        # Cache for Django models per workspace
        self._model_cache: Dict[str, Dict[str, Any]] = {}
        self._model_cache_timestamps: Dict[str, float] = {}
        self._model_cache_lock = threading.RLock()

        # Cache for document information - use regular dict since WeakValueDictionary can't store dicts
        self._document_cache: Dict[str, Dict[str, Any]] = {}
        self._document_cache_lock = threading.RLock()

        # Cache for ORM operations with position ranges
        self._orm_operations_cache: Dict[str, List[ORMOperation]] = {}
        self._orm_operations_lock = threading.RLock()

        # Track which workspaces have been loaded
        self._loaded_workspaces: Set[str] = set()
        self._workspace_lock = threading.RLock()

        # Cache invalidation settings
        self._model_cache_ttl = 300  # 5 minutes
        self._document_cache_ttl = 60  # 1 minute
        self._orm_operations_ttl = 30  # 30 seconds

        # Track document cache timestamps for TTL
        self._document_cache_timestamps: Dict[str, float] = {}
        self._orm_operations_timestamps: Dict[str, float] = {}

    def get_models_for_workspace(self, workspace_root: str) -> Dict[str, Any]:
        """
        Get Django models for a workspace with caching.

        Args:
            workspace_root: Path to the workspace root

        Returns:
            Dictionary of model information
        """
        with self._model_cache_lock:
            current_time = time.time()

            # Check if we have cached models and they're still valid
            if workspace_root in self._model_cache:
                cache_time = self._model_cache_timestamps.get(workspace_root, 0)
                if current_time - cache_time < self._model_cache_ttl:
                    debug_logger.debug(
                        f"Using cached models for workspace: {workspace_root}"
                    )
                    return self._model_cache[workspace_root]
                else:
                    # Remove expired entry
                    debug_logger.debug(f"Cache expired for workspace: {workspace_root}")
                    self._model_cache.pop(workspace_root, None)
                    self._model_cache_timestamps.pop(workspace_root, None)

            # Load models and cache them
            debug_logger.debug(f"Loading models for workspace: {workspace_root}")
            try:
                debug_logger.debug(
                    f"Calling model_loader.load_models({workspace_root})"
                )
                models = self.model_loader.load_models(workspace_root)
                debug_logger.debug(
                    f"Model loader returned: {type(models)} with {len(models) if models else 0} items"
                )

                if not models:
                    debug_logger.warning(
                        f"Model loader returned no models for workspace: {workspace_root}"
                    )
                    return {}

                self._model_cache[workspace_root] = models
                self._model_cache_timestamps[workspace_root] = current_time

                with self._workspace_lock:
                    self._loaded_workspaces.add(workspace_root)

                debug_logger.debug(
                    f"Cached {len(models)} models for workspace: {workspace_root}"
                )
                return models

            except Exception as e:
                debug_logger.error(
                    f"Failed to load models for workspace {workspace_root}: {e}"
                )
                debug_logger.error(f"Exception type: {type(e).__name__}")
                debug_logger.error(f"Exception details: {e!s}")
                # Don't cache the failure - let the caller handle it
                return {}

    def get_models_for_document(
        self, document_uri: str, workspace_root: str
    ) -> Dict[str, Any]:
        """
        Get Django models for a specific document.

        This method ensures models are loaded for the workspace and returns
        them for use in document-specific operations.
        """
        return self.get_models_for_workspace(workspace_root)

    def invalidate_workspace_models(self, workspace_root: str) -> None:
        """
        Invalidate cached models for a workspace.

        This is typically called when model files change.
        """
        with self._model_cache_lock:
            self._model_cache.pop(workspace_root, None)
            self._model_cache_timestamps.pop(workspace_root, None)

        with self._workspace_lock:
            self._loaded_workspaces.discard(workspace_root)

        debug_logger.debug(f"Invalidated model cache for workspace: {workspace_root}")

    def refresh_workspace_models(self, workspace_root: str) -> Dict[str, Any]:
        """
        Refresh models for a workspace.

        This forces a reload of models and updates the cache.
        """
        self.invalidate_workspace_models(workspace_root)
        return self.get_models_for_workspace(workspace_root)

    def get_document_info(self, document_uri: str) -> Optional[Dict[str, Any]]:
        """
        Get cached document information.

        Args:
            document_uri: URI of the document

        Returns:
            Cached document information or None
        """
        with self._document_cache_lock:
            current_time = time.time()

            # Check if we have cached info and it's still valid
            if document_uri in self._document_cache:
                cache_time = self._document_cache_timestamps.get(document_uri, 0)
                if current_time - cache_time < self._document_cache_ttl:
                    return self._document_cache[document_uri]
                else:
                    # Remove expired entry
                    self._document_cache.pop(document_uri, None)
                    self._document_cache_timestamps.pop(document_uri, None)

            return None

    def cache_document_info(self, document_uri: str, info: Dict[str, Any]) -> None:
        """
        Cache document information.

        Args:
            document_uri: URI of the document
            info: Document information to cache
        """
        with self._document_cache_lock:
            self._document_cache[document_uri] = info
            self._document_cache_timestamps[document_uri] = time.time()

    def cache_orm_operations(
        self, document_uri: str, orm_operations: List[ORMOperation]
    ) -> None:
        """
        Cache ORM operations with their position ranges.

        Args:
            document_uri: URI of the document
            orm_operations: List of ORM operations with position ranges
        """
        with self._orm_operations_lock:
            self._orm_operations_cache[document_uri] = orm_operations
            self._orm_operations_timestamps[document_uri] = time.time()
            debug_logger.debug(
                f"Cached {len(orm_operations)} ORM operations for {document_uri}"
            )

    def get_orm_context_at_position(
        self, document_uri: str, line: int, character: int
    ) -> Optional[ORMOperation]:
        """
        Get ORM context at a specific position.

        Args:
            document_uri: URI of the document
            line: 0-based line number
            character: 0-based character position

        Returns:
            ORM operation context if cursor is within an ORM operation range, None otherwise
        """
        with self._orm_operations_lock:
            current_time = time.time()

            # Check if we have cached ORM operations and they're still valid
            if document_uri in self._orm_operations_cache:
                cache_time = self._orm_operations_timestamps.get(document_uri, 0)
                if current_time - cache_time < self._orm_operations_ttl:
                    orm_operations = self._orm_operations_cache[document_uri]

                    # Find ORM operation that contains the cursor position
                    for orm_op in orm_operations:
                        if orm_op.range_start_line <= line <= orm_op.range_end_line:
                            # Check character position for the specific line
                            if (
                                line == orm_op.range_start_line
                                and character < orm_op.range_start_character
                            ):
                                continue
                            if (
                                line == orm_op.range_end_line
                                and character > orm_op.range_end_character
                            ):
                                continue
                            return orm_op
                else:
                    # Remove expired entry
                    self._orm_operations_cache.pop(document_uri, None)
                    self._orm_operations_timestamps.pop(document_uri, None)

            return None

    def get_all_orm_operations(self, document_uri: str) -> List[ORMOperation]:
        """
        Get all cached ORM operations for a document.

        Args:
            document_uri: URI of the document

        Returns:
            List of ORM operations or empty list if none cached
        """
        with self._orm_operations_lock:
            current_time = time.time()

            if document_uri in self._orm_operations_cache:
                cache_time = self._orm_operations_timestamps.get(document_uri, 0)
                if current_time - cache_time < self._orm_operations_ttl:
                    return self._orm_operations_cache[document_uri]
                else:
                    # Remove expired entry
                    self._orm_operations_cache.pop(document_uri, None)
                    self._orm_operations_timestamps.pop(document_uri, None)

            return []

    def invalidate_document(self, document_uri: str) -> None:
        """
        Invalidate cached information for a document.

        Args:
            document_uri: URI of the document
        """
        with self._document_cache_lock:
            self._document_cache.pop(document_uri, None)
            self._document_cache_timestamps.pop(document_uri, None)

        with self._orm_operations_lock:
            self._orm_operations_cache.pop(document_uri, None)
            self._orm_operations_timestamps.pop(document_uri, None)

        debug_logger.debug(f"Invalidated document cache for: {document_uri}")

    def clear_workspace(self, workspace_root: str) -> None:
        """
        Clear all cached data for a workspace.

        Args:
            workspace_root: Path to the workspace root
        """
        self.invalidate_workspace_models(workspace_root)

        # Clear document cache entries for this workspace
        with self._document_cache_lock:
            keys_to_remove = [
                uri for uri in self._document_cache if workspace_root in uri
            ]
            for uri in keys_to_remove:
                self._document_cache.pop(uri, None)
                self._document_cache_timestamps.pop(uri, None)

        # Clear ORM operations cache entries for this workspace
        with self._orm_operations_lock:
            keys_to_remove = [
                uri for uri in self._orm_operations_cache if workspace_root in uri
            ]
            for uri in keys_to_remove:
                self._orm_operations_cache.pop(uri, None)
                self._orm_operations_timestamps.pop(uri, None)

    def clear_all(self) -> None:
        """Clear all cached data."""
        with self._model_cache_lock:
            self._model_cache.clear()
            self._model_cache_timestamps.clear()

        with self._document_cache_lock:
            self._document_cache.clear()
            self._document_cache_timestamps.clear()

        with self._orm_operations_lock:
            self._orm_operations_cache.clear()
            self._orm_operations_timestamps.clear()

        with self._workspace_lock:
            self._loaded_workspaces.clear()

        debug_logger.debug("Cleared all document and model caches")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._model_cache_lock:
            model_cache_size = len(self._model_cache)
            model_cache_keys = list(self._model_cache.keys())

        with self._document_cache_lock:
            document_cache_size = len(self._document_cache)

        with self._orm_operations_lock:
            orm_operations_cache_size = len(self._orm_operations_cache)

        with self._workspace_lock:
            loaded_workspaces = list(self._loaded_workspaces)

        return {
            "model_cache_size": model_cache_size,
            "model_cache_keys": model_cache_keys,
            "document_cache_size": document_cache_size,
            "orm_operations_cache_size": orm_operations_cache_size,
            "loaded_workspaces": loaded_workspaces,
            "model_cache_ttl": self._model_cache_ttl,
            "document_cache_ttl": self._document_cache_ttl,
            "orm_operations_ttl": self._orm_operations_ttl,
        }

    def set_model_cache_ttl(self, ttl_seconds: int) -> None:
        """Set the TTL for model cache entries."""
        self._model_cache_ttl = ttl_seconds

    def set_document_cache_ttl(self, ttl_seconds: int) -> None:
        """Set the TTL for document cache entries."""
        self._document_cache_ttl = ttl_seconds

    def set_orm_operations_ttl(self, ttl_seconds: int) -> None:
        """Set the TTL for ORM operations cache entries."""
        self._orm_operations_ttl = ttl_seconds

    def cache_document_source(self, document_uri: str, source: str) -> None:
        """
        Cache document source code for fast access.

        Args:
            document_uri: URI of the document
            source: Document source code
        """
        with self._document_cache_lock:
            # Store source in document cache with a special key
            if document_uri not in self._document_cache:
                self._document_cache[document_uri] = {}
            self._document_cache[document_uri]["source"] = source
            self._document_cache_timestamps[document_uri] = time.time()
            debug_logger.debug(f"Cached document source for {document_uri}")

    def get_document_source(self, document_uri: str) -> Optional[str]:
        """
        Get cached document source code.

        Args:
            document_uri: URI of the document

        Returns:
            Cached document source or None
        """
        with self._document_cache_lock:
            current_time = time.time()

            # Check if we have cached source and it's still valid
            if document_uri in self._document_cache:
                cache_time = self._document_cache_timestamps.get(document_uri, 0)
                if current_time - cache_time < self._document_cache_ttl:
                    doc_info = self._document_cache[document_uri]
                    return doc_info.get("source")
                else:
                    # Remove expired entry
                    self._document_cache.pop(document_uri, None)
                    self._document_cache_timestamps.pop(document_uri, None)

            return None
