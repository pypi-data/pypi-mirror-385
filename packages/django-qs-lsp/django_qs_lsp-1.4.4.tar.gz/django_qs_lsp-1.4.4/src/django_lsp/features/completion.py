"""
Django LSP completion feature that works with the caching system.
"""

from typing import Any, Dict

from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    InsertTextFormat,
)

from ..orm.operation_provider import OperationProvider
from ..utils.logging import get_logger

logger = get_logger(__name__)


class CompletionFeature:
    """
    Django LSP completion feature.
    """

    def __init__(
        self,
        django_setup: Any = None,
        model_loader: Any = None,
        ls: Any = None,
        document_cache: Any = None,
    ):
        self.django_setup = django_setup
        self.model_loader = model_loader
        self.ls = ls
        self.document_cache = document_cache
        # Create OperationProvider once to avoid recreating it on every completion request
        self.operation_provider = None
        if self.model_loader:
            from ..orm.operation_provider import OperationProvider

            self.operation_provider = OperationProvider(self.model_loader)

    def handle_completion(self, params: Any) -> Dict[str, Any]:
        """
        Handle completion request.
        """
        try:
            logger.info(
                f"Handling completion request at position {params.position.line}:{params.position.character}"
            )

            # Get ORM context from document cache
            orm_context = self._get_orm_context_from_cache(params)
            if not orm_context:
                logger.info(
                    "No cached ORM context found - server should parse and cache ORM context on next change"
                )
                return {"items": [], "is_incomplete": False}

            # Handle completion with context
            result = self._handle_completion_with_context(params, orm_context)
            return result

        except Exception as e:
            logger.error(f"Error handling completion request: {e}")
            return {"items": [], "is_incomplete": False}

    def resolve_completion_item(self, params: CompletionItem) -> CompletionItem:
        """
        Resolve completion item details.

        Args:
            params: Completion item resolve parameters

        Returns:
            Resolved completion item or original params if resolution fails
        """
        try:
            # For now, just return the original params
            # This can be enhanced later to provide additional details
            return params
        except Exception as e:
            logger.error(f"Error resolving completion item: {e}")
            return params

    def _get_orm_context_from_cache(self, params: Any) -> Any:
        """
        Get ORM context from document cache.
        """
        try:
            if not self.document_cache:
                return None

            # Get ORM operations from document cache
            document_uri = params.text_document.uri
            orm_operations = self.document_cache.get_all_orm_operations(document_uri)

            if not orm_operations:
                return None

            # Find ORM operation that contains or is near the cursor position
            cursor_line = params.position.line
            cursor_character = params.position.character

            # First try to find exact containment
            for orm_op in orm_operations:
                if (
                    orm_op.range_start_line <= cursor_line <= orm_op.range_end_line
                    and (
                        cursor_line > orm_op.range_start_line
                        or cursor_character >= orm_op.range_start_character
                    )
                    and (
                        cursor_line < orm_op.range_end_line
                        or cursor_character <= orm_op.range_end_character
                    )
                ):
                    logger.info(
                        f"Found ORM context (exact): {orm_op.model_name}.{orm_op.manager_name}.{orm_op.operation_name}"
                    )
                    return orm_op

            # If no exact containment, find the closest ORM operation
            # This handles cases where cursor is positioned after typing (e.g., filter(id|))
            closest_orm_op = None
            min_distance = float("inf")

            for orm_op in orm_operations:
                # Calculate distance to ORM operation center
                op_center_line = (orm_op.range_start_line + orm_op.range_end_line) / 2
                op_center_char = (
                    orm_op.range_start_character + orm_op.range_end_character
                ) / 2

                distance = (
                    abs(cursor_line - op_center_line)
                    + abs(cursor_character - op_center_char) / 100
                )

                # Check if cursor is reasonably close to the ORM operation
                # Allow for some flexibility in positioning
                if (
                    abs(cursor_line - orm_op.range_start_line) <= 1
                    and abs(cursor_line - orm_op.range_end_line) <= 1
                ):
                    if distance < min_distance:
                        min_distance = distance
                        closest_orm_op = orm_op

            if closest_orm_op:
                logger.info(
                    f"Found ORM context (closest): {closest_orm_op.model_name}.{closest_orm_op.manager_name}.{closest_orm_op.operation_name}"
                )
                return closest_orm_op

            return None

        except Exception as e:
            logger.error(f"Error getting ORM context from cache: {e}")
            return None

    def _handle_completion_with_context(
        self, params: Any, orm_context: Any
    ) -> Dict[str, Any]:
        """
        Handle completion with ORM context.
        """
        try:
            logger.info("Starting completion with context...")

            # Get available models from model loader
            if not self.model_loader:
                logger.warning("No model loader available")
                return {"items": [], "is_incomplete": False}

            logger.info("Getting available models...")
            available_models = self.model_loader.load_models()
            if not available_models:
                logger.warning("No available models found")
                return {"items": [], "is_incomplete": False}

            # Get the model name, manager name, and operation from ORM context
            model_name = orm_context.model_name
            manager_name = orm_context.manager_name
            operation = orm_context.operation_name

            # Extract the current argument at the cursor position using tree-sitter parser
            typed_content = self._extract_current_argument(params, orm_context)

            logger.info(
                f"Model: {model_name}, Manager: {manager_name}, Operation: {operation}, Typed: '{typed_content}'"
            )

            if not model_name or not manager_name or not operation:
                logger.warning(
                    "Missing model name, manager name, or operation in ORM context"
                )
                return {"items": [], "is_incomplete": False}

            # Get completion items from operation provider
            operation_provider = OperationProvider(self.model_loader)
            completion_data = operation_provider.get_operation_data(
                model_name,
                manager_name,
                operation,
                typed_content,
                available_models,
            )

            # Convert the completion data to completion items
            completion_items = []

            # Process both fields and lookups if present
            if completion_data.get("fields"):
                logger.info(
                    f"User typed '{typed_content}', showing fields ({len(completion_data.get('fields', []))})"
                )
                for field in completion_data.get("fields", []):
                    completion_items.append(
                        CompletionItem(
                            label=field.name,
                            kind=CompletionItemKind.Field,
                            detail=f"Field: {field.name}",
                            sort_text=f"0_{field.name}",
                            insert_text=f"{field.name}=",
                            insert_text_format=InsertTextFormat.PlainText,
                        )
                    )

            if completion_data.get("lookups"):
                logger.info(
                    f"User typed '{typed_content}', showing lookups ({len(completion_data.get('lookups', []))})"
                )
                for lookup in completion_data.get("lookups", []):
                    completion_items.append(
                        CompletionItem(
                            label=lookup.name,
                            kind=CompletionItemKind.Keyword,
                            detail=f"Lookup: {lookup.name}",
                            sort_text=f"0_{lookup.name}",
                            insert_text=f"{lookup.name}=",
                            insert_text_format=InsertTextFormat.PlainText,
                        )
                    )

            logger.info(f"Got {len(completion_items)} completion items")
            return {"items": completion_items, "is_incomplete": False}

        except Exception as e:
            logger.error(f"Error in completion with context: {e}")
            return {"items": [], "is_incomplete": False}

    def _extract_current_argument(self, params: Any, orm_context: Any) -> str:
        """
        Extract the current argument at the cursor position by analyzing the current document content.

        Args:
            params: Completion parameters with cursor position
            orm_context: ORM context from document cache

        Returns:
            The current argument text at the cursor position
        """
        try:
            if not self.document_cache:
                return ""

            # Get the current document source from cache (LSP already provided this via didChange)
            document_uri = params.text_document.uri
            document_source = self.document_cache.get_document_source(document_uri)
            if not document_source:
                return ""

            # Simple text-based extraction: look backwards from cursor to find the current argument
            cursor_line = params.position.line
            cursor_col = params.position.character

            lines = document_source.split("\n")
            if cursor_line >= len(lines):
                return ""

            current_line = lines[cursor_line]

            # Ensure cursor position is within line bounds
            if cursor_col > len(current_line):
                cursor_col = len(current_line)

            # Debug: log the current line and cursor position
            logger.info(f"Current line: '{current_line}'")
            logger.info(f"Cursor position: {cursor_line}:{cursor_col}")

            # Look backwards from cursor to find the start of the current argument
            # This handles cases like: filter(id|) -> "id", filter(id__exact|) -> "id__exact"
            start_pos = cursor_col
            while start_pos > 0 and (
                current_line[start_pos - 1].isalnum()
                or current_line[start_pos - 1] == "_"
            ):
                start_pos -= 1

            current_argument = current_line[start_pos:cursor_col]
            logger.info(
                f"Extracted current argument: '{current_argument}' at position {cursor_line}:{cursor_col}"
            )

            return str(current_argument)

        except Exception as e:
            logger.error(f"Error extracting current argument: {e}")
            return ""
