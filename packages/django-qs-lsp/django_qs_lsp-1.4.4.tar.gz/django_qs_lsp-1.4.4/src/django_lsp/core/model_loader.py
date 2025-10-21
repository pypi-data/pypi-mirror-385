"""
Model loading and caching.

This module handles loading Django models from the project and caching
them for efficient access by LSP features.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from django.apps import apps
from django.db.models import Model

from ..utils.logging import get_debug_logger, get_logger, register_logger
from .field_analyzer import FieldAnalysis, FieldAnalyzer

# Use unified logging system with LSP integration
logger = get_logger("model_loader", use_lsp=True)
debug_logger = get_debug_logger("model_loader")

# Register logger for server updates
register_logger(logger)


@dataclass
class ManagerInfo:
    """Information about a Django model manager."""

    name: str
    type: str  # "DefaultManager" or "CustomManager"
    manager_class: str
    manager_module: str
    is_default: bool
    description: str
    instance: Any = None  # The actual Django manager instance for introspection

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backward compatibility."""
        return {
            "name": self.name,
            "type": self.type,
            "manager_class": self.manager_class,
            "manager_module": self.manager_module,
            "is_default": self.is_default,
            "description": self.description,
        }


@dataclass
class ModelInfo:
    """Comprehensive information about a Django model."""

    app_label: str
    model_name: str
    verbose_name: str
    verbose_name_plural: Optional[str]
    fields: Dict[str, FieldAnalysis] = field(default_factory=dict)
    managers: Dict[str, ManagerInfo] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backward compatibility."""
        return {
            "app_label": self.app_label,
            "model_name": self.model_name,
            "verbose_name": self.verbose_name,
            "verbose_name_plural": self.verbose_name_plural,
            "fields": {
                name: field_info.to_dict() for name, field_info in self.fields.items()
            },
            "managers": {
                name: manager_info.to_dict()
                for name, manager_info in self.managers.items()
            },
        }


class ModelLoader:
    """Loads and caches Django models for LSP features across multiple workspaces."""

    def __init__(self) -> None:
        # Cache models per workspace
        self.workspace_models_cache: Dict[str, Dict[str, ModelInfo]] = {}
        self.workspace_loaded: Dict[str, bool] = {}
        # Global cache for backward compatibility
        self.models_cache: Dict[str, ModelInfo] = {}
        self.is_loaded: bool = False
        debug_logger.debug("ModelLoader initialized")

    def load_models(self, workspace_root: Optional[str] = None) -> Dict[str, ModelInfo]:
        """
        Load all Django models from the project using Django's apps registry.

        Args:
            workspace_root: Optional workspace root to load models for specific workspace

        Returns:
            Dictionary mapping model names to ModelInfo objects
        """
        # Check cache first
        if self._is_cache_valid(workspace_root):
            cache = self._get_cache(workspace_root)
            debug_logger.debug(
                f"Returning cached models for workspace: {workspace_root or 'global'}"
            )
            return cache

        models_info: Dict[str, ModelInfo] = {}

        try:
            logger.info(
                f"Loading Django models for workspace: {workspace_root or 'global'}"
            )

            # Check if Django is properly configured
            try:
                from django.conf import settings

                debug_logger.debug(
                    f"Django settings module: {getattr(settings, 'DJANGO_SETTINGS_MODULE', 'Not set')}"
                )
                debug_logger.debug(
                    f"Django apps registry available: {apps is not None}"
                )
            except Exception as django_error:
                debug_logger.error(f"Django not properly configured: {django_error}")
                return {}

            # Get all registered apps
            try:
                app_configs = apps.get_app_configs()
                debug_logger.debug(f"Found {len(app_configs)} Django apps")
                for app_config in app_configs:
                    debug_logger.debug(f"App: {app_config.label} ({app_config.name})")
            except Exception as app_error:
                debug_logger.error(f"Failed to get Django app configs: {app_error}")
                return {}

            for app_config in app_configs:
                debug_logger.debug(f"Processing app: {app_config.label}")
                try:
                    app_models = app_config.get_models()
                    # Django's get_models() returns a generator, convert to list for length check
                    app_models_list = list(app_models)
                    debug_logger.debug(
                        f"App {app_config.label} has {len(app_models_list)} models"
                    )
                except Exception as model_error:
                    debug_logger.error(
                        f"Failed to get models for app {app_config.label}: {model_error}"
                    )
                    continue

                for model in app_models_list:
                    model_name = model.__name__
                    debug_logger.debug(f"Loading model: {model_name}")
                    try:
                        model_info = self._analyze_model(model, app_config.label)
                        models_info[model_name] = model_info
                    except Exception as analyze_error:
                        debug_logger.error(
                            f"Failed to analyze model {model_name}: {analyze_error}"
                        )
                        continue

            # Cache the results
            self._update_cache(models_info, workspace_root)

            model_count = len(models_info)
            model_names = list(models_info.keys())
            logger.info(
                f"Loaded {model_count} models for workspace {workspace_root or 'global'}: {model_names}"
            )

            return models_info

        except Exception as e:
            logger.error(f"Error loading Django models: {e!s}")
            logger.error(
                "This usually means the LSP server doesn't have access to the Django project's dependencies"
            )
            logger.error(
                "Make sure the LSP server is running in the same Python environment as your Django project"
            )
            debug_logger.error(f"Exception details: {type(e).__name__}: {e}")
            return {}

    def _is_cache_valid(self, workspace_root: Optional[str] = None) -> bool:
        """Check if cache is valid for the given workspace."""
        if workspace_root is None:
            return self.is_loaded and bool(self.models_cache)
        else:
            return (
                self.workspace_loaded.get(workspace_root, False)
                and workspace_root in self.workspace_models_cache
            )

    def _get_cache(self, workspace_root: Optional[str] = None) -> Dict[str, ModelInfo]:
        """Get the appropriate cache for the workspace."""
        if workspace_root is None:
            return self.models_cache
        else:
            return self.workspace_models_cache.get(workspace_root, {})

    def _update_cache(
        self, models_info: Dict[str, ModelInfo], workspace_root: Optional[str] = None
    ) -> None:
        """Update the appropriate cache with new model information."""
        if workspace_root:
            self.workspace_models_cache[workspace_root] = models_info
            self.workspace_loaded[workspace_root] = True
        else:
            self.models_cache = models_info
            self.is_loaded = True

    def _analyze_model(self, model: Type[Model], app_label: str) -> ModelInfo:
        """
        Analyze a Django model and return comprehensive information.

        Args:
            model: Django model class
            app_label: Application label

        Returns:
            ModelInfo object containing model analysis
        """
        debug_logger.debug(f"Analyzing model: {model.__name__} from app {app_label}")

        # Create base model info
        model_info = ModelInfo(
            app_label=app_label,
            model_name=model.__name__,
            verbose_name=getattr(model._meta, "verbose_name", model.__name__),
            verbose_name_plural=getattr(model._meta, "verbose_name_plural", None),
        )

        # Analyze managers
        self._analyze_managers(model, model_info)

        # Get all forward fields from the model
        for django_field in model._meta.get_fields():
            field_name = django_field.name
            try:
                # Only analyze actual Django fields, skip reverse relations
                from django.db.models import Field as DjangoField

                if isinstance(django_field, DjangoField):
                    field_analysis = FieldAnalyzer.analyze_field(django_field)
                    model_info.fields[field_name] = field_analysis
                else:
                    debug_logger.debug(
                        f"Skipping non-field object: {field_name} ({type(django_field).__name__})"
                    )
            except Exception as e:
                debug_logger.warning(
                    f"Error analyzing field {field_name} in model {model.__name__}: {e}"
                )
                # Create a basic field info as fallback
                model_info.fields[field_name] = FieldAnalysis(
                    type=django_field.__class__.__name__,
                    name=field_name,
                    verbose_name=field_name,
                    help_text="",
                    null=False,
                    blank=False,
                    default=None,
                    lookups=[],
                )

        # Add reverse relations (related managers) that are explicitly named
        self._add_reverse_relations(model, model_info)

        debug_logger.debug(
            f"Model analysis complete: {model.__name__} has {len(model_info.fields)} fields and {len(model_info.managers)} managers"
        )
        return model_info

    def _add_reverse_relations(self, model: Type[Model], model_info: ModelInfo) -> None:
        """Add reverse relations to the model info."""
        for related_object in model._meta.related_objects:
            if hasattr(related_object, "get_accessor_name"):
                accessor_name = related_object.get_accessor_name()
                if accessor_name:  # Only add if there's an explicit accessor name
                    field_analysis = FieldAnalysis(
                        type="RelatedManager",
                        name=accessor_name,
                        verbose_name=accessor_name,
                        help_text="",
                        null=False,
                        blank=False,
                        default=None,
                        lookups=[],
                        related_model=related_object.related_model.__name__,
                        related_app=related_object.related_model._meta.app_label,
                    )
                    model_info.fields[accessor_name] = field_analysis
                    debug_logger.debug(
                        f"Added reverse relation: {accessor_name} -> {related_object.related_model.__name__}"
                    )

    def _analyze_managers(self, model: Type[Model], model_info: ModelInfo) -> None:
        """
        Analyze managers defined on a Django model.

        Args:
            model: Django model class
            model_info: ModelInfo object to update
        """
        # Get the default manager name
        default_manager_name = getattr(model._meta, "default_manager_name", "objects")

        # If default_manager_name is None, the first manager in the list is the default
        if default_manager_name is None and model._meta.managers_map:
            default_manager_name = next(iter(model._meta.managers_map.keys()))

        # Get all managers including custom ones
        for manager_name, manager_instance in model._meta.managers_map.items():
            is_default = manager_name == default_manager_name
            manager_type = "DefaultManager" if is_default else "CustomManager"

            manager_info = ManagerInfo(
                name=manager_name,
                type=manager_type,
                manager_class=manager_instance.__class__.__name__,
                manager_module=manager_instance.__class__.__module__,
                is_default=is_default,
                description=f"{'Default' if is_default else 'Custom'} manager '{manager_name}' for {model.__name__}",
                instance=manager_instance,
            )
            model_info.managers[manager_name] = manager_info

            debug_logger.debug(
                f"Added {manager_type.lower()} '{manager_name}' for model {model.__name__}"
            )

        # Also check for any manager attributes defined directly on the model class
        for attr_name in dir(model):
            attr_value = getattr(model, attr_name, None)
            if (
                attr_value is not None
                and hasattr(attr_value, "__class__")
                and hasattr(attr_value.__class__, "_queryset_class")
                and attr_name not in model_info.managers
            ):
                # This looks like a manager instance
                is_default = attr_name == default_manager_name
                manager_type = "DefaultManager" if is_default else "CustomManager"

                manager_info = ManagerInfo(
                    name=attr_name,
                    type=manager_type,
                    manager_class=attr_value.__class__.__name__,
                    manager_module=attr_value.__class__.__module__,
                    is_default=is_default,
                    description=f"{'Default' if is_default else 'Custom'} manager '{attr_name}' for {model.__name__}",
                    instance=attr_value,
                )
                model_info.managers[attr_name] = manager_info

                debug_logger.debug(
                    f"Added {manager_type.lower()} attribute '{attr_name}' for model {model.__name__}"
                )

    def get_model_info(
        self, model_name: str, workspace_root: Optional[str] = None
    ) -> Optional[ModelInfo]:
        """
        Get model info from cache, reloading if necessary.

        Args:
            model_name: Name of the model to retrieve
            workspace_root: Optional workspace root for workspace-specific lookup

        Returns:
            ModelInfo object or None if not found
        """
        # Ensure cache is loaded
        cache = self._ensure_cache_loaded(workspace_root)

        model_info = cache.get(model_name)
        if model_info:
            debug_logger.debug(f"Found model: {model_name}")
        else:
            logger.warning(f"Model not found: {model_name}")
            debug_logger.debug(f"Available models: {list(cache.keys())}")

        return model_info

    def get_model_info_dict(
        self, model_name: str, workspace_root: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get model info as dictionary (backward compatibility).

        Args:
            model_name: Name of the model to retrieve
            workspace_root: Optional workspace root for workspace-specific lookup

        Returns:
            Model information dictionary or None if not found
        """
        model_info = self.get_model_info(model_name, workspace_root)
        return model_info.to_dict() if model_info else None

    def _ensure_cache_loaded(
        self, workspace_root: Optional[str] = None
    ) -> Dict[str, ModelInfo]:
        """Ensure cache is loaded for the given workspace."""
        if not self._is_cache_valid(workspace_root):
            debug_logger.debug(
                f"Cache not valid for workspace {workspace_root or 'global'}, loading models..."
            )
            self.load_models(workspace_root)
        return self._get_cache(workspace_root)

    def get_all_models(self, workspace_root: Optional[str] = None) -> List[str]:
        """
        Get list of all available model names.

        Args:
            workspace_root: Optional workspace root for workspace-specific models

        Returns:
            List of model names
        """
        cache = self._ensure_cache_loaded(workspace_root)
        return list(cache.keys())

    def clear_cache(self, workspace_root: Optional[str] = None) -> None:
        """Clear the model cache for a specific workspace or globally."""
        if workspace_root:
            if workspace_root in self.workspace_models_cache:
                del self.workspace_models_cache[workspace_root]
            if workspace_root in self.workspace_loaded:
                del self.workspace_loaded[workspace_root]
            logger.info(f"Model cache cleared for workspace: {workspace_root}")
        else:
            self.models_cache.clear()
            self.is_loaded = False
            logger.info("Global model cache cleared")

    def reload_models(
        self, workspace_root: Optional[str] = None
    ) -> Dict[str, ModelInfo]:
        """
        Force reload of all models for a specific workspace or globally.

        Args:
            workspace_root: Optional workspace root for workspace-specific reload

        Returns:
            Updated model information dictionary
        """
        self.clear_cache(workspace_root)
        return self.load_models(workspace_root)

    def get_workspace_cache_info(self) -> Dict[str, Any]:
        """Get information about cached workspaces."""
        return {
            "workspaces": list(self.workspace_models_cache.keys()),
            "loaded_workspaces": list(self.workspace_loaded.keys()),
            "global_loaded": self.is_loaded,
            "total_workspaces": len(self.workspace_models_cache),
        }

    def get_cache_info(self) -> Dict[str, Any]:
        """Get comprehensive cache information."""
        return {
            "workspace_cache": self.get_workspace_cache_info(),
            "global_cache": {
                "is_loaded": self.is_loaded,
                "model_count": len(self.models_cache),
                "models": list(self.models_cache.keys()) if self.models_cache else [],
            },
            "total_workspaces": len(self.workspace_models_cache),
            "total_models_global": len(self.models_cache),
            "total_models_all_workspaces": sum(
                len(cache) for cache in self.workspace_models_cache.values()
            ),
        }

    def __enter__(self) -> "ModelLoader":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        """Context manager exit - cleanup resources."""
        self.clear_cache()

    def get_model_by_name(
        self, model_name: str, workspace_root: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get the actual Django model class by name.

        Args:
            model_name: Name of the model to retrieve
            workspace_root: Optional workspace root for workspace-specific lookup

        Returns:
            Django model class or None if not found
        """
        model_info = self.get_model_info(model_name, workspace_root)
        if model_info:
            # Try to get the actual model class from Django's registry
            try:
                return apps.get_model(model_info.app_label, model_info.model_name)
            except Exception as e:
                debug_logger.warning(f"Could not get model class for {model_name}: {e}")
        return None

    def validate_model_name(
        self, model_name: str, workspace_root: Optional[str] = None
    ) -> bool:
        """
        Validate that a model name exists in the current workspace.

        Args:
            model_name: Name of the model to validate
            workspace_root: Optional workspace root for workspace-specific validation

        Returns:
            True if model exists, False otherwise
        """
        return self.get_model_info(model_name, workspace_root) is not None

    def get_models_by_app(
        self, app_label: str, workspace_root: Optional[str] = None
    ) -> List[str]:
        """
        Get all models from a specific app.

        Args:
            app_label: Application label
            workspace_root: Optional workspace root for workspace-specific lookup

        Returns:
            List of model names from the app
        """
        cache = self._ensure_cache_loaded(workspace_root)
        return [
            model_name
            for model_name, model_info in cache.items()
            if model_info.app_label == app_label
        ]

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the model loader."""
        return {
            "cache_info": self.get_cache_info(),
            "field_analyzer_stats": {
                "cache_hits": FieldAnalyzer.get_field_lookups.cache_info().hits,
                "cache_misses": FieldAnalyzer.get_field_lookups.cache_info().misses,
            },
            "total_models_analyzed": sum(
                len(cache) for cache in self.workspace_models_cache.values()
            )
            + len(self.models_cache),
        }

    def preload_common_models(self, workspace_root: Optional[str] = None) -> None:
        """
        Preload commonly used models for better performance.

        This method can be called during LSP initialization to warm up the cache
        with frequently accessed models.
        """
        common_models = [
            "User",
            "Group",
            "Permission",
            "ContentType",
            "Session",
            "Site",
            "LogEntry",
            "Migration",
        ]

        cache = self._ensure_cache_loaded(workspace_root)
        preloaded = []

        for model_name in common_models:
            if model_name in cache:
                preloaded.append(model_name)

        debug_logger.debug(f"Preloaded {len(preloaded)} common models: {preloaded}")

    def get_model_dependencies(
        self, model_name: str, workspace_root: Optional[str] = None
    ) -> List[str]:
        """
        Get list of models that the specified model depends on.

        Args:
            model_name: Name of the model
            workspace_root: Optional workspace root for workspace-specific lookup

        Returns:
            List of dependent model names
        """
        model_info = self.get_model_info(model_name, workspace_root)
        if not model_info:
            return []

        dependencies = set()

        # Check for foreign key relationships
        for field_info in model_info.fields.values():
            if field_info.related_model:
                dependencies.add(field_info.related_model)

        return list(dependencies)
