"""
Documentation generation utilities.

This module provides utilities for generating documentation for
Django fields and lookups.
"""

from typing import Any, Dict, Optional

from lsprotocol.types import MarkupContent, MarkupKind


class DocumentationGenerator:
    """Generates documentation for Django fields and lookups."""

    def generate_field_documentation(
        self, field_info: Dict[str, Any], field_name: str
    ) -> MarkupContent:
        """
        Generate documentation for a Django field.

        Args:
            field_info: Field information dictionary
            field_name: Name of the field

        Returns:
            MarkupContent with field documentation
        """
        field_type = field_info["type"]
        field_obj = field_info["field"]

        # Get field help text if available
        help_text = getattr(field_obj, "help_text", "")

        # Get field description from verbose_name if available
        getattr(field_obj, "verbose_name", field_name)

        # Build documentation like a proper LSP
        doc_parts = [f"{field_name}: {field_type}"]

        if help_text:
            doc_parts.append(help_text)

        # Add field-specific information
        if hasattr(field_obj, "max_length") and field_obj.max_length:
            doc_parts.append(f"Max length: {field_obj.max_length}")

        if hasattr(field_obj, "null") and field_obj.null:
            doc_parts.append("Nullable: Yes")

        if hasattr(field_obj, "blank") and field_obj.blank:
            doc_parts.append("Blank allowed: Yes")

        if hasattr(field_obj, "default") and field_obj.default is not None:
            doc_parts.append(f"Default: {field_obj.default}")

        # For related fields, add relationship info
        if "related_model" in field_info:
            doc_parts.append(f"Related model: {field_info['related_model']}")

        return MarkupContent(kind=MarkupKind.Markdown, value="\n".join(doc_parts))

    def generate_lookup_documentation(
        self,
        lookup_name: str,
        field_type: str,
        field_info: Optional[Dict[str, Any]] = None,
    ) -> MarkupContent:
        """
        Generate documentation for a Django field lookup using Django introspection.

        Args:
            lookup_name: Name of the lookup
            field_type: Type of the field
            field_info: Optional field information containing lookups from Django introspection

        Returns:
            MarkupContent with lookup documentation
        """
        # Try to get documentation from Django introspection first
        if field_info and "lookups" in field_info:
            lookups = field_info["lookups"]
            for lookup in lookups:
                lookup_name_from_lookup = (
                    lookup["name"]
                    if isinstance(lookup, dict) and "name" in lookup
                    else str(lookup)
                )
                if lookup_name_from_lookup == lookup_name:
                    # Use Django's built-in documentation if available
                    doc = (
                        lookup.get("doc")
                        if isinstance(lookup, dict)
                        else getattr(lookup, "doc", None)
                    )
                    if doc:
                        return MarkupContent(
                            kind=MarkupKind.Markdown,
                            value=f"__{lookup_name}(value)\n{doc!s}",
                        )
                    break

        # Fallback to basic description if no Django introspection available
        description = f"Lookup '{lookup_name}' for {field_type}"

        return MarkupContent(
            kind=MarkupKind.Markdown, value=f"__{lookup_name}(value)\n{description}"
        )

    def generate_field_lookup_documentation(
        self,
        field_info: Dict[str, Any],
        field_name: str,
        lookup_name: str,
        model_name: str,
    ) -> MarkupContent:
        """
        Generate simple documentation for a field lookup combination.

        Args:
            field_info: Field information dictionary
            field_name: Name of the field
            lookup_name: Name of the lookup
            model_name: Name of the model

        Returns:
            MarkupContent with field and lookup documentation
        """
        field_type = field_info["type"]
        field_obj = field_info["field"]

        # Get field help text if available
        help_text = getattr(field_obj, "help_text", "")
        verbose_name = getattr(field_obj, "verbose_name", field_name)

        # Build documentation like a proper LSP
        doc_parts = [f"{field_name}__{lookup_name}(value)"]

        # Field information
        if help_text:
            doc_parts.append(f"{verbose_name} ({field_type}): {help_text}")
        else:
            doc_parts.append(f"{verbose_name} ({field_type})")

        # Lookup information
        lookup_description = self._get_lookup_description(
            lookup_name, field_type, field_info
        )
        doc_parts.append(lookup_description)

        return MarkupContent(kind=MarkupKind.Markdown, value="\n".join(doc_parts))

    def _get_lookup_description(
        self,
        lookup_name: str,
        field_type: str,
        field_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Get description for a lookup using Django introspection."""
        # Try to get documentation from Django introspection first
        if field_info and "lookups" in field_info:
            lookups = field_info["lookups"]
            for lookup in lookups:
                lookup_name_from_lookup = (
                    lookup["name"]
                    if isinstance(lookup, dict) and "name" in lookup
                    else str(lookup)
                )
                if lookup_name_from_lookup == lookup_name:
                    # Use Django's built-in documentation if available
                    doc = (
                        lookup.get("doc")
                        if isinstance(lookup, dict)
                        else getattr(lookup, "doc", None)
                    )
                    if doc:
                        return str(doc)  # Ensure it's a string
                    break

        # Fallback to basic description if no Django introspection available
        return f"Lookup '{lookup_name}' for {field_type}"
