"""
Manager analysis and capability discovery.

This module analyzes Django model managers to determine what operations
they support and what arguments they accept.
"""

from typing import Any, Dict, List, Set

from django.db.models import Manager, QuerySet

from ..utils.logging import get_logger

logger = get_logger("manager_analyzer")


class ManagerCapabilityAnalyzer:
    """Analyzes Django model managers to determine their capabilities."""

    def analyze_manager_capabilities(self, manager: Manager) -> Dict[str, Any]:
        """
        Analyze what operations and arguments a manager supports.

        Args:
            manager: Django manager instance to analyze

        Returns:
            Dictionary containing manager capabilities
        """
        try:
            capabilities = {
                "operations": self._discover_operations(manager),
                "custom_methods": self._discover_custom_methods(manager),
                "queryset_methods": self._discover_queryset_methods(manager),
                "manager_type": self._classify_manager(manager),
                "supports_filtering": self._supports_filtering(manager),
                "supports_annotation": self._supports_annotation(manager),
                "supports_related_loading": self._supports_related_loading(manager),
            }

            logger.info(
                f"Analyzed manager {manager.__class__.__name__}: {capabilities}"
            )
            return capabilities

        except Exception as e:
            logger.warning(f"Error analyzing manager capabilities: {e}")
            # Return conservative defaults
            return {
                "operations": {"filter", "exclude", "get", "all"},
                "custom_methods": [],
                "queryset_methods": set(),
                "manager_type": "Unknown",
                "supports_filtering": True,
                "supports_annotation": False,
                "supports_related_loading": False,
            }

    def _discover_operations(self, manager: Manager) -> Set[str]:
        """
        Discover what ORM operations this manager supports.

        Args:
            manager: Django manager instance

        Returns:
            Set of operation names this manager supports
        """
        operations = set()

        try:
            # Check if it's a QuerySet manager (most common)
            if hasattr(manager, "get_queryset"):
                queryset = manager.get_queryset()

                # These are the core operations that most QuerySet managers support
                core_operations = {"filter", "exclude", "get", "all", "first", "last"}
                operations.update(core_operations)

                # Check for additional operations based on queryset type
                if hasattr(queryset, "annotate"):
                    operations.add("annotate")
                if hasattr(queryset, "select_related"):
                    operations.add("select_related")
                if hasattr(queryset, "prefetch_related"):
                    operations.add("prefetch_related")
                if hasattr(queryset, "order_by"):
                    operations.add("order_by")
                if hasattr(queryset, "values"):
                    operations.add("values")
                if hasattr(queryset, "values_list"):
                    operations.add("values_list")
                if hasattr(queryset, "distinct"):
                    operations.add("distinct")
                if hasattr(queryset, "only"):
                    operations.add("only")
                if hasattr(queryset, "defer"):
                    operations.add("defer")

            # Check for custom operations defined on the manager
            custom_operations = self._discover_custom_methods(manager)
            operations.update(custom_operations)

        except Exception as e:
            logger.warning(f"Error discovering operations: {e}")
            # Fallback to basic operations
            operations.update({"filter", "exclude", "get", "all"})

        return operations

    def _discover_custom_methods(self, manager: Manager) -> List[str]:
        """
        Discover custom methods defined on the manager.

        Args:
            manager: Django manager instance

        Returns:
            List of custom method names
        """
        custom_methods = []

        try:
            # Look for methods that aren't inherited from Manager/QuerySet
            manager_methods = set(dir(manager))
            base_manager_methods = set(dir(Manager()))
            base_queryset_methods = set(dir(QuerySet()))

            # Custom methods are those not in the base classes
            custom = manager_methods - base_manager_methods - base_queryset_methods

            for method_name in custom:
                method = getattr(manager, method_name)
                if callable(method) and not method_name.startswith("_"):
                    custom_methods.append(method_name)

        except Exception as e:
            logger.warning(f"Error discovering custom methods: {e}")

        return custom_methods

    def _discover_queryset_methods(self, manager: Manager) -> Set[str]:
        """
        Discover what QuerySet methods are available.

        Args:
            manager: Django manager instance

        Returns:
            Set of available QuerySet method names
        """
        queryset_methods = set()

        try:
            if hasattr(manager, "get_queryset"):
                queryset = manager.get_queryset()
                # Get all public methods from the queryset
                for attr_name in dir(queryset):
                    if not attr_name.startswith("_") and callable(
                        getattr(queryset, attr_name)
                    ):
                        queryset_methods.add(attr_name)

        except Exception as e:
            logger.warning(f"Error discovering queryset methods: {e}")

        return queryset_methods

    def _classify_manager(self, manager: Manager) -> str:
        """
        Classify the type of manager.

        Args:
            manager: Django manager instance

        Returns:
            String classification of the manager type
        """
        try:
            if hasattr(manager, "get_queryset"):
                return "QuerySetManager"
            elif hasattr(manager, "_queryset_class"):
                return "CustomQuerySetManager"
            elif hasattr(manager, "__class__") and manager.__class__ != Manager:
                return "CustomManager"
            else:
                return "BaseManager"
        except Exception:
            return "Unknown"

    def _supports_filtering(self, manager: Manager) -> bool:
        """Check if the manager supports filtering operations."""
        try:
            return hasattr(manager, "filter") and callable(manager.filter)
        except Exception:
            return False

    def _supports_annotation(self, manager: Manager) -> bool:
        """Check if the manager supports annotation operations."""
        try:
            if hasattr(manager, "get_queryset"):
                queryset = manager.get_queryset()
                return hasattr(queryset, "annotate") and callable(queryset.annotate)
            return False
        except Exception:
            return False

    def _supports_related_loading(self, manager: Manager) -> bool:
        """Check if the manager supports related field loading."""
        try:
            if hasattr(manager, "get_queryset"):
                queryset = manager.get_queryset()
                return hasattr(queryset, "select_related") and hasattr(
                    queryset, "prefetch_related"
                )
            return False
        except Exception:
            return False
