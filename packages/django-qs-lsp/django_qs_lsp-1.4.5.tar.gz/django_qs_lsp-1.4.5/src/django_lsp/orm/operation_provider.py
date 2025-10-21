"""
Clean operation provider that uses pre-analyzed field data from ModelLoader.

This eliminates redundant field introspection since ModelLoader already does it.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..core.model_loader import ManagerInfo, ModelInfo
from ..utils.logging import get_logger
from .manager_analyzer import ManagerCapabilityAnalyzer

logger = get_logger("operation_provider")


@dataclass
class FieldCompletionData:
    """Data structure for field completion information."""

    name: str
    field_type: str
    is_related: bool = False
    related_model: Optional[str] = None


@dataclass
class LookupCompletionData:
    """Data structure for lookup completion information."""

    name: str
    lookup_type: str = ""
    field_name: str = ""
    documentation: Optional[str] = None


class OperationProvider:
    """Clean operation provider using pre-analyzed field data from ModelLoader."""

    def __init__(self, model_loader: Any) -> None:
        self.model_loader = model_loader
        self.manager_analyzer = ManagerCapabilityAnalyzer()

    def get_operation_data(
        self,
        model_name: str,
        manager_name: str,
        operation_name: str,
        typed_content: str = "",
        available_models: Optional[Dict[str, ModelInfo]] = None,
    ) -> Dict[str, Any]:
        """Get completion data for a specific operation using pre-analyzed data."""
        try:
            # Get model info (already contains analyzed fields)
            model_info = self.model_loader.get_model_info(model_name)
            if not model_info:
                logger.warning(f"Model '{model_name}' not found")
                return {"fields": [], "lookups": []}

            # Get manager info
            manager_info = model_info.managers.get(manager_name)
            if not manager_info:
                logger.warning(
                    f"Manager '{manager_name}' not found on model '{model_name}'"
                )
                return {"fields": [], "lookups": []}

            # Analyze manager capabilities dynamically
            capabilities = self._analyze_manager_capabilities(manager_info)

            # Check if this operation is supported
            if operation_name not in capabilities["operations"]:
                logger.info(
                    f"Operation '{operation_name}' not supported by manager '{manager_name}'"
                )
                return {"fields": [], "lookups": []}

            # Special handling for operations that expect field names with empty args
            # If typed_content is empty or clearly not a field path, fall back to base fields
            normalized_typed = (typed_content or "").strip()
            if operation_name in {"select_related", "prefetch_related", "annotate"}:
                if not normalized_typed or "(" in normalized_typed:
                    return self.get_model_fields(model_name, "", available_models)

            # Use the recursive field completion logic for other cases
            return self.get_model_fields(model_name, normalized_typed, available_models)

        except Exception as e:
            logger.error(f"Error getting operation data: {e}")
            return {"fields": [], "lookups": []}

    def get_all_completions(
        self,
        model_name: str,
        manager_name: str,
        operation_name: str,
        typed_content: str = "",
        available_models: Optional[Dict[str, ModelInfo]] = None,
    ) -> Dict[str, Any]:
        """Get ALL completions using pre-analyzed data."""
        try:
            # Get model info (already contains analyzed fields)
            model_info = self.model_loader.get_model_info(model_name)
            if not model_info:
                logger.warning(f"Model '{model_name}' not found")
                return {"fields": [], "lookups": []}

            # Get manager info
            manager_info = model_info.managers.get(manager_name)
            if not manager_info:
                logger.warning(
                    f"Manager '{manager_name}' not found on model '{model_name}'"
                )
                return {"fields": [], "lookups": []}

            # Analyze manager capabilities dynamically
            capabilities = self._analyze_manager_capabilities(manager_info)

            # Check if this operation is supported
            if operation_name not in capabilities["operations"]:
                logger.info(
                    f"Operation '{operation_name}' not supported by manager '{manager_name}'"
                )
                return {"fields": [], "lookups": []}

            # Use the recursive field completion logic
            return self.get_model_fields(model_name, typed_content, available_models)

        except Exception as e:
            logger.error(f"Error getting all completions: {e}")
            return {"fields": [], "lookups": []}

    def _analyze_manager_capabilities(
        self, manager_info: ManagerInfo
    ) -> Dict[str, Any]:
        """Analyze manager capabilities using Django introspection."""
        try:
            if hasattr(manager_info, "instance") and manager_info.instance:
                return self.manager_analyzer.analyze_manager_capabilities(
                    manager_info.instance
                )
            return {"operations": set(), "manager_type": "Unknown"}
        except Exception as e:
            logger.error(f"Error analyzing manager capabilities: {e}")
            return {"operations": set(), "manager_type": "Unknown"}

    def get_model_fields(
        self,
        model_name: str,
        field_path: str = "",
        available_models: Optional[Dict[str, ModelInfo]] = None,
    ) -> Dict[str, Any]:
        """Get model fields for completion using pre-analyzed data."""
        try:
            logger.info(
                f"get_model_fields called with model_name: {model_name}, field_path: '{field_path}'"
            )
            # Get model info
            base_model = self.model_loader.get_model_info(model_name)
            if not base_model:
                logger.warning(f"Model '{model_name}' not found")
                return {"fields": [], "lookups": []}

            # Case 1: Empty input - return all base model fields + first-level related fields
            if not field_path:
                logger.info("Case 1 triggered: Empty field_path")
                return self._get_base_model_fields(base_model, available_models)

            # Case 2: Field with trailing underscore (e.g., "id_") - return lookups for that field
            if field_path.endswith("_") and not field_path.endswith("__"):
                logger.info("Case 2 triggered: Field with trailing underscore")
                base_field_name = field_path.rstrip("_")
                if base_field_name in base_model.fields:
                    field_analysis = base_model.fields[base_field_name]
                    return {
                        "fields": [],
                        "lookups": self._get_field_lookups(
                            field_analysis, base_field_name
                        ),
                    }
                return {"fields": [], "lookups": []}

            # Case 3: Simple related field path ending with "__" (e.g., "user__") - return related model fields
            if field_path.endswith("__") and field_path.count("__") == 1:
                # Check if this is actually a related field
                base_field_name = field_path[:-2]
                if base_field_name in base_model.fields:
                    field_analysis = base_model.fields[base_field_name]
                    if field_analysis.related_model:
                        logger.info(
                            "Case 3 triggered: Simple related field path ending with __"
                        )
                        return self._get_related_model_fields(
                            base_model, field_path, available_models
                        )
                    else:
                        # This is a regular field, not a related field - show lookups
                        logger.info(
                            "Case 3: Regular field with trailing __ - showing lookups"
                        )
                        return {
                            "fields": [],
                            "lookups": self._get_field_lookups(
                                field_analysis, base_field_name
                            ),
                        }

            # Case 4: Check if this is an exact field match - return both field and lookups
            if field_path in base_model.fields:
                field_analysis = base_model.fields[field_path]
                # Return both the field itself and its lookups
                return {
                    "fields": [
                        FieldCompletionData(
                            name=field_path,
                            field_type=field_analysis.type,
                            is_related=field_analysis.related_model is not None,
                            related_model=field_analysis.related_model,
                        )
                    ],
                    "lookups": self._get_field_lookups(field_analysis, field_path),
                }

            # Case 4.4: Intermediate nested field path (e.g., "author__profile" or "author__profile__" should show Profile model fields)
            if "__" in field_path:
                logger.info(f"Case 4.4 triggered for field_path: {field_path}")
                # Split the path to find all field parts
                # Remove trailing __ if present to get the actual field path
                actual_field_path = field_path.removesuffix("__")
                path_parts = actual_field_path.split("__")
                logger.info(f"Path parts: {path_parts}")

                if len(path_parts) >= 2:
                    # Traverse the relationship chain to find the final model
                    current_model = base_model

                    for i, field_name in enumerate(path_parts):
                        if field_name not in current_model.fields:
                            logger.info(
                                f"Field {field_name} not found in model {current_model.model_name}"
                            )
                            return {"fields": [], "lookups": []}

                        field_analysis = current_model.fields[field_name]

                        # If this is the last field and it's not a related field, return lookups for it
                        if (
                            i == len(path_parts) - 1
                            and not field_analysis.related_model
                        ):
                            logger.info(
                                f"Final field {field_name} is not a related field, returning lookups"
                            )
                            return {
                                "fields": [],
                                "lookups": self._get_field_lookups(
                                    field_analysis, field_path
                                ),
                            }

                        # If this is not the last field, it must be a related field
                        if not field_analysis.related_model:
                            logger.info(
                                f"Field {field_name} is not a related field but not the final field"
                            )
                            return {"fields": [], "lookups": []}

                        # Move to the related model
                        if available_models:
                            related_model = available_models.get(
                                field_analysis.related_model
                            )
                            if related_model:
                                current_model = related_model
                            else:
                                logger.info(
                                    f"Related model {field_analysis.related_model} not found"
                                )
                                return {"fields": [], "lookups": []}
                        else:
                            logger.info("No available models for related field lookup")
                            return {"fields": [], "lookups": []}

                    # If we get here, we have a valid path to a related model
                    # Return fields from the final related model
                    fields = []
                    for field_name, field_analysis in current_model.fields.items():
                        fields.append(
                            FieldCompletionData(
                                name=f"{field_path.removesuffix('__')}__{field_name}",
                                field_type=field_analysis.type,
                                is_related=field_analysis.related_model is not None,
                                related_model=field_analysis.related_model,
                            )
                        )

                    logger.info(
                        f"Returning {len(fields)} fields from related model {current_model.model_name}"
                    )
                    return {"fields": fields, "lookups": []}

            # Case 4.5: Check if this is a complete lookup (e.g., "id__exact") - return nothing
            if "__" in field_path and not field_path.endswith("__"):
                # This is a complete lookup like "id__exact", no more completions needed
                return {"fields": [], "lookups": []}

            # Case 4.6: Partial foreign key field path (e.g., "author" should show author__username, author__email)
            if field_path in base_model.fields:
                field_analysis = base_model.fields[field_path]
                if field_analysis.related_model and available_models:
                    related_model = available_models.get(field_analysis.related_model)
                    if related_model:
                        # Return expanded foreign key fields
                        fields = []
                        for (
                            related_field_name,
                            related_field_analysis,
                        ) in related_model.fields.items():
                            fields.append(
                                FieldCompletionData(
                                    name=f"{field_path}__{related_field_name}",
                                    field_type=related_field_analysis.type,
                                    is_related=related_field_analysis.related_model
                                    is not None,
                                    related_model=related_field_analysis.related_model,
                                )
                            )
                        return {"fields": fields, "lookups": []}

            # Case 5: Partial field name or related path - return full level-1 field set
            # Let the LSP client handle filtering as the user types
            return self._get_base_model_fields(base_model, available_models)

        except Exception as e:
            logger.error(f"Error getting model fields: {e}")
            return {"fields": [], "lookups": []}

    def _get_field_lookups(
        self, field_analysis: Any, field_path: str = ""
    ) -> List[LookupCompletionData]:
        """Get lookups for a specific field from its FieldAnalysis."""
        lookups = []
        try:
            # Remove trailing underscores from field_path to avoid double underscores
            clean_field_path = field_path.rstrip("_")

            # The lookups are already analyzed and stored in field_analysis.lookups
            for lookup in field_analysis.lookups:
                # Create the full field path + lookup name
                full_lookup_name = (
                    f"{clean_field_path}__{lookup.name}"
                    if clean_field_path
                    else lookup.name
                )
                lookups.append(
                    LookupCompletionData(
                        name=full_lookup_name,
                        lookup_type=lookup.name,
                        field_name=field_analysis.name
                        if hasattr(field_analysis, "name")
                        else "unknown",
                        documentation=lookup.doc,
                    )
                )
        except Exception as e:
            logger.error(f"Error getting lookups for field: {e}")

        return lookups

    def _get_base_model_fields(
        self,
        model_info: ModelInfo,
        available_models: Optional[Dict[str, ModelInfo]] = None,
    ) -> Dict[str, Any]:
        """Get base model fields and their lookups for initial completion context.

        Returns direct model fields plus their common lookups, and expanded foreign key fields.
        """
        fields = []
        lookups = []

        # Add base model fields and their lookups
        for field_name, field_analysis in model_info.fields.items():
            # Add the field itself
            fields.append(
                FieldCompletionData(
                    name=field_name,
                    field_type=field_analysis.type,
                    is_related=field_analysis.related_model is not None,
                    related_model=field_analysis.related_model,
                )
            )

            # Add common lookups for this field
            field_lookups = self._get_field_lookups(field_analysis, field_name)
            lookups.extend(field_lookups)

            # If this is a foreign key field and we have available models, expand it
            if field_analysis.related_model and available_models:
                related_model = available_models.get(field_analysis.related_model)
                if related_model:
                    # Add expanded foreign key fields (e.g., author__username, author__email)
                    for (
                        related_field_name,
                        related_field_analysis,
                    ) in related_model.fields.items():
                        expanded_field_name = f"{field_name}__{related_field_name}"
                        fields.append(
                            FieldCompletionData(
                                name=expanded_field_name,
                                field_type=related_field_analysis.type,
                                is_related=related_field_analysis.related_model
                                is not None,
                                related_model=related_field_analysis.related_model,
                            )
                        )

        return {"fields": fields, "lookups": lookups}

    def _get_fields_starting_with(
        self, model_info: ModelInfo, partial: str, prefix: str = ""
    ) -> Dict[str, Any]:
        """Get fields that start with the given partial from pre-analyzed data."""
        fields = []
        for field_name, field_analysis in model_info.fields.items():
            if field_name.startswith(partial):
                full_name = f"{prefix}__{field_name}" if prefix else field_name
                fields.append(
                    FieldCompletionData(
                        name=full_name,
                        field_type=field_analysis.type,
                        is_related=field_analysis.related_model is not None,
                        related_model=field_analysis.related_model,
                    )
                )

        return {"fields": fields, "lookups": []}

    def _get_lookups_for_field(
        self, model_info: ModelInfo, field_name: str, field_path: str
    ) -> Dict[str, Any]:
        """Get lookups for a specific field using pre-analyzed data."""
        try:
            field_analysis = model_info.fields.get(field_name)
            if not field_analysis:
                return {"fields": [], "lookups": []}

            # The lookups are already analyzed and stored in field_analysis.lookups
            lookups = []
            for lookup in field_analysis.lookups:
                lookups.append(
                    LookupCompletionData(
                        name=f"{field_path}__{lookup.name}",
                        lookup_type=lookup.name,
                        field_name=field_name,
                        documentation=lookup.doc,
                    )
                )

            return {"fields": [], "lookups": lookups}

        except Exception as e:
            logger.error(f"Error getting lookups for field {field_name}: {e}")
            return {"fields": [], "lookups": []}

    def _get_related_model_fields(
        self,
        base_model: ModelInfo,
        field_path: str,
        available_models: Optional[Dict[str, ModelInfo]],
    ) -> Dict[str, Any]:
        """Get fields from a related model with the field path as prefix."""
        if not field_path.endswith("__"):
            return {"fields": [], "lookups": []}  # Should not happen for this case

        # Remove trailing separator for processing
        path_parts = field_path[:-2].split("__")
        if not path_parts:
            return {"fields": [], "lookups": []}

        # Traverse to the target model
        current_model = base_model
        for part in path_parts:
            if part not in current_model.fields:
                return {"fields": [], "lookups": []}

            analysis = current_model.fields[part]
            if not analysis.related_model or not available_models:
                return {"fields": [], "lookups": []}

            if analysis.related_model not in available_models:
                return {"fields": [], "lookups": []}

            current_model = available_models[analysis.related_model]

        # Return all fields from the related model with the prefix
        fields = []
        # Remove trailing underscores from field_path to avoid double underscores
        clean_field_path = field_path.rstrip("_")
        for field_name, field_analysis in current_model.fields.items():
            fields.append(
                FieldCompletionData(
                    name=f"{clean_field_path}__{field_name}",
                    field_type=field_analysis.type,
                    is_related=field_analysis.related_model is not None,
                    related_model=field_analysis.related_model,
                )
            )
        return {"fields": fields, "lookups": []}
