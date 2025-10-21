"""
Field analysis and lookup generation.

This module handles analyzing Django model fields and generating
available lookups for different field types.
"""

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Dict, List, Optional

from django.db.models import Field
from django.db.models.fields.related import RelatedField

from ..utils.logging import get_debug_logger, get_logger, register_logger

# Use unified logging system with LSP integration
logger = get_logger("field_analyzer", use_lsp=True)
debug_logger = get_debug_logger("field_analyzer")

# Register logger for server updates
register_logger(logger)


@dataclass
class FieldLookup:
    """Represents a Django field lookup with documentation."""

    name: str
    doc: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert to dictionary format for backward compatibility."""
        return {"name": self.name, "doc": self.doc}


@dataclass
class FieldAnalysis:
    """Comprehensive analysis of a Django field."""

    type: str
    name: str
    verbose_name: str
    help_text: str
    null: bool
    blank: bool
    default: Optional[Any]
    lookups: List[FieldLookup] = field(default_factory=list)
    max_length: Optional[int] = None
    choices: Optional[Any] = None
    related_model: Optional[str] = None
    related_app: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backward compatibility."""
        result = {
            "type": self.type,
            "name": self.name,
            "verbose_name": self.verbose_name,
            "help_text": self.help_text,
            "null": self.null,
            "blank": self.blank,
            "default": self.default,
            "lookups": [lookup.to_dict() for lookup in self.lookups],
        }

        if self.max_length is not None:
            result["max_length"] = self.max_length
        if self.choices is not None:
            result["choices"] = self.choices
        if self.related_model is not None:
            result["related_model"] = self.related_model
        if self.related_app is not None:
            result["related_app"] = self.related_app

        return result


class FieldAnalyzer:
    """Analyzes Django model fields and generates lookups."""

    @staticmethod
    @lru_cache(maxsize=128)
    def get_field_lookups(field: Field) -> List[FieldLookup]:
        """
        Get available lookups for a Django field using Django's built-in APIs.

        This method is cached to improve performance for repeated lookups.

        Args:
            field: Django field instance

        Returns:
            List of FieldLookup objects
        """
        lookups: List[FieldLookup] = []

        # Django fields know their own lookups - just ask them!
        if hasattr(field, "get_lookups"):
            try:
                lookup_dict = field.get_lookups()
                for lookup_name, lookup_class in lookup_dict.items():
                    doc = getattr(lookup_class, "__doc__", None)
                    # Clean up documentation if available
                    if doc:
                        doc = doc.strip()
                        # Remove common prefixes for cleaner display
                        if doc.startswith("Return a"):
                            doc = doc[8:]  # Remove "Return a"
                        elif doc.startswith("Returns a"):
                            doc = doc[9:]  # Remove "Returns a"

                    lookups.append(FieldLookup(name=lookup_name, doc=doc))

                debug_logger.debug(
                    f"Retrieved {len(lookups)} lookups for {field.__class__.__name__}"
                )

            except Exception as e:
                logger.warning(
                    f"Error getting lookups for {field.__class__.__name__}: {e}"
                )
                debug_logger.error(f"Exception details: {type(e).__name__}: {e}")

        # If Django can't tell us the lookups, return empty list - don't guess!
        return lookups

    @staticmethod
    def analyze_field(field: Field) -> FieldAnalysis:
        """
        Analyze a Django field and return comprehensive information.

        Args:
            field: Django field instance

        Returns:
            FieldAnalysis object containing field analysis
        """
        debug_logger.debug(
            f"Analyzing field: {field.name} ({field.__class__.__name__})"
        )

        # Validate input
        if not isinstance(field, Field):
            raise ValueError(f"Expected Django Field, got {type(field).__name__}")

        # Get lookups for the field
        lookups = FieldAnalyzer.get_field_lookups(field)

        # Create base field analysis
        field_analysis = FieldAnalysis(
            type=field.__class__.__name__,
            name=field.name,
            verbose_name=getattr(field, "verbose_name", field.name),
            help_text=getattr(field, "help_text", ""),
            null=getattr(field, "null", False),
            blank=getattr(field, "blank", False),
            default=getattr(field, "default", None),
            lookups=lookups,
        )

        # Add field-specific attributes
        if hasattr(field, "max_length") and field.max_length:
            field_analysis.max_length = field.max_length

        if hasattr(field, "choices") and field.choices:
            field_analysis.choices = field.choices

        # Handle related fields
        if isinstance(field, RelatedField):
            if hasattr(field, "related_model") and field.related_model:
                field_analysis.related_model = field.related_model.__name__
                field_analysis.related_app = field.related_model._meta.app_label
                debug_logger.debug(
                    f"Related field: {field.name} -> {field_analysis.related_model} "
                    f"({field_analysis.related_app})"
                )

        debug_logger.debug(
            f"Field analysis complete: {field.name} has {len(lookups)} lookups"
        )

        return field_analysis

    @staticmethod
    def analyze_field_dict(field: Field) -> Dict[str, Any]:
        """
        Analyze a Django field and return dictionary format (backward compatibility).

        Args:
            field: Django field instance

        Returns:
            Dictionary containing field analysis
        """
        return FieldAnalyzer.analyze_field(field).to_dict()

    @staticmethod
    def get_field_type_info(field: Field) -> Dict[str, Any]:
        """
        Get basic type information for a field.

        Args:
            field: Django field instance

        Returns:
            Dictionary with basic type information
        """
        return {
            "type": field.__class__.__name__,
            "name": field.name,
            "is_related": isinstance(field, RelatedField),
            "is_nullable": getattr(field, "null", False),
        }

    @staticmethod
    def validate_field(field: Any) -> bool:
        """
        Validate that an object is a Django field.

        Args:
            field: Object to validate

        Returns:
            True if valid Django field, False otherwise
        """
        try:
            return isinstance(field, Field)
        except Exception:
            return False

    @staticmethod
    def clear_cache() -> None:
        """Clear the lookup cache. Useful for testing or memory management."""
        FieldAnalyzer.get_field_lookups.cache_clear()
        debug_logger.debug("Field lookup cache cleared")
