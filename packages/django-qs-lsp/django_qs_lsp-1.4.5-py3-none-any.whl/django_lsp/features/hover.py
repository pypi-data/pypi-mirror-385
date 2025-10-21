# mypy: disable-error-code="unreachable"
"""
Hover feature implementation for Django LSP.

This module provides hover functionality for Django ORM operations,
including field documentation and lookup information.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from lsprotocol import types

from ..core.django_setup import DjangoSetup
from ..core.model_loader import ModelLoader
from ..utils.documentation import DocumentationGenerator
from ..utils.logging import get_debug_logger
from ..utils.parser_cache import get_parser_cache

# server_state will be passed as a parameter to avoid circular imports

# Use unified logging system
debug_logger = get_debug_logger("hover")


@dataclass
class HoverContext:
    """Context information for hover operations."""

    document_uri: str
    position: types.Position
    document_source: str
    line_content: str


@dataclass
class ORMOperationInfo:
    """Information about detected ORM operations."""

    model_name: str
    operation_name: str
    typed_content: Any
    field_name: str
    lookup_name: Optional[str] = None


@dataclass
class HoverResult:
    """Result of hover analysis."""

    documentation: str
    range: Optional[types.Range]
    success: bool
    error_message: Optional[str] = None


class HoverFeature:
    """Handles hover requests for Django ORM operations."""

    def __init__(
        self,
        django_setup: DjangoSetup,
        model_loader: ModelLoader,
        server: Any = None,
        server_state: Any = None,
    ) -> None:
        self.django_setup = django_setup
        self.model_loader = model_loader
        self.server = server
        self.server_state = server_state
        self.doc_generator = DocumentationGenerator()
        # Use the parser cache
        self.parser_cache = get_parser_cache()

        debug_logger.info("HoverFeature initialized")

    def handle_hover(
        self, params: types.HoverParams, document: Any
    ) -> Optional[types.Hover]:
        """
        Handle hover request.

        Args:
            params: Hover parameters
            document: The text document

        Returns:
            Hover information or None
        """
        debug_logger.info(
            f"🔍 HoverFeature.handle_hover called for {params.text_document.uri} at position {params.position.line}:{params.position.character}"
        )

        try:
            # Create hover context
            context = self._create_hover_context(params, document)
            if not context:
                debug_logger.warning("❌ Could not create hover context")
                return None

            debug_logger.info(
                f"✅ Created hover context with line content: '{context.line_content}'"
            )

            # Detect ORM operation
            orm_info = self._detect_orm_operation(context)
            if not orm_info:
                debug_logger.warning("❌ No ORM operation detected")
                return None

            debug_logger.info(
                f"✅ Detected ORM operation: {orm_info.model_name}.objects.{orm_info.operation_name}"
            )

            # Analyze field information
            field_info = self._get_field_info(orm_info)
            if not field_info:
                debug_logger.warning(
                    f"❌ No field info found for {orm_info.field_name} in model {orm_info.model_name}"
                )
                return None

            debug_logger.info(f"✅ Found field info for {orm_info.field_name}")

            # Generate documentation
            result = self._generate_hover_documentation(context, orm_info, field_info)
            if not result.success:
                debug_logger.warning(
                    f"❌ Hover documentation generation failed: {result.error_message}"
                )
                return None

            debug_logger.info(
                f"✅ Generated hover documentation: {result.documentation[:100]}..."
            )

            return types.Hover(
                contents=result.documentation,
                range=result.range,
            )

        except Exception as e:
            debug_logger.error(f"❌ Unexpected error in hover: {e}", exc_info=True)
            return None

    def _create_hover_context(
        self, params: types.HoverParams, document: Any
    ) -> Optional[HoverContext]:
        """Create hover context from request parameters."""
        try:
            if not document:
                debug_logger.warning("No document provided for hover request")
                return None

            # Get line content safely
            try:
                line_content = document.lines[params.position.line]
            except IndexError:
                debug_logger.warning(
                    f"Line {params.position.line} not found in document"
                )
                return None

            # Get document source
            document_source = "\n".join(document.lines)

            return HoverContext(
                document_uri=params.text_document.uri,
                position=params.position,
                document_source=document_source,
                line_content=line_content,
            )

        except Exception as e:
            debug_logger.error(f"Error creating hover context: {e}")
            return None

    def _detect_orm_operation(
        self, context: HoverContext
    ) -> Optional[ORMOperationInfo]:
        """Detect ORM operation at cursor position using cached information first."""
        result: Optional[ORMOperationInfo] = None

        try:
            # First, try to get ORM context from cached operations
            if self.server_state and self.server_state.document_cache:
                orm_context = (
                    self.server_state.document_cache.get_orm_context_at_position(
                        context.document_uri,
                        context.position.line,
                        context.position.character,
                    )
                )
                if orm_context:
                    debug_logger.info(f"✅ Found cached ORM context: {orm_context}")

                    # Extract information from cached ORM operation
                    model_name = orm_context.model_name
                    operation_name = orm_context.operation_name

                    # Parse field and lookup information from the context
                    field_name, lookup_name = self._parse_field_lookup(
                        orm_context.field_name or ""
                    )

                    debug_logger.info(
                        f"📊 From cache: model={model_name}, operation={operation_name}, field={field_name}, lookup={lookup_name}"
                    )

                    result = ORMOperationInfo(
                        model_name=model_name,
                        operation_name=operation_name,
                        typed_content=orm_context.field_name or "",
                        field_name=field_name,
                        lookup_name=lookup_name,
                    )
                    debug_logger.info(f"✅ Created ORM info from cache: {result}")
                    return result

            # Fallback: use parser if no cached context found
            debug_logger.info("No cached ORM context found, falling back to parsing")

            # Get workspace root from document URI
            workspace_root = self._get_workspace_root_from_uri(context.document_uri)
            if not workspace_root:
                debug_logger.warning("Could not determine workspace root")
                return None

            # Get parser from cache
            from ..utils.parser_cache import get_parser_cache

            orm_parser = get_parser_cache().get_parser(workspace_root)
            if not orm_parser:
                debug_logger.warning("No parser available for workspace")
                return None

            debug_logger.info(
                f"🔍 Starting ORM detection for position {context.position.line}:{context.position.character}"
            )

            # Use the parser
            completion_context = orm_parser.get_completion_context(
                context.document_source,
                context.position.line + 1,  # Tree-sitter uses 1-based line numbers
                context.position.character,
            )

            debug_logger.info(f"🔍 Completion context result: {completion_context}")

            if completion_context:
                debug_logger.info(f"✅ Found completion context: {completion_context}")

                # Extract information from completion context
                model_name = completion_context.get("model_name")
                operation_name = completion_context.get("operation_name")
                current_argument = completion_context.get("current_argument", "")

                debug_logger.info(
                    f"📊 Extracted: model={model_name}, operation={operation_name}, argument={current_argument}"
                )

                if model_name and operation_name and current_argument:
                    # Resolve 'self' to class name if needed
                    model_name = orm_parser.resolve_model_name_if_self(
                        model_name, context.document_source, context.position.line
                    )

                    # Parse field and lookup information from current argument
                    field_name, lookup_name = self._parse_field_lookup(current_argument)
                    debug_logger.info(
                        f"🔍 Parsed: field={field_name}, lookup={lookup_name}"
                    )

                    result = ORMOperationInfo(
                        model_name=model_name,
                        operation_name=operation_name,
                        typed_content=current_argument,
                        field_name=field_name,
                        lookup_name=lookup_name,
                    )
                    debug_logger.info(f"✅ Created ORM info: {result}")
                else:
                    debug_logger.warning(
                        f"❌ Missing required context: model={model_name}, operation={operation_name}, argument={current_argument}"
                    )
            else:
                debug_logger.debug("No ORM operation detected at cursor position")

        except Exception as e:
            debug_logger.error(f"Error detecting ORM operation: {e}")

        return result

    def _parse_field_lookup(self, word: str) -> Tuple[str, Optional[str]]:
        """Parse field name and lookup from word under cursor."""
        if "__" in word:
            field_name, lookup_name = word.split("__", 1)
            return field_name, lookup_name
        return word, None

    def _get_field_info(self, orm_info: ORMOperationInfo) -> Optional[Dict[str, Any]]:
        """Get field information from model."""
        try:
            model_info = self.model_loader.get_model_info(orm_info.model_name)
            if not model_info:
                debug_logger.warning(f"Model info not found for: {orm_info.model_name}")
                return None

            field_info = (
                model_info.fields.get(orm_info.field_name)
                if hasattr(model_info, "fields")
                else None
            )
            if not field_info:
                debug_logger.warning(
                    f"Field info not found for: {orm_info.field_name} in model {orm_info.model_name}"
                )
                return None

            # Convert FieldAnalysis to dict for backward compatibility
            if hasattr(field_info, "to_dict"):
                return field_info.to_dict()
            elif isinstance(field_info, dict):
                return field_info
            else:
                return None

        except Exception as e:
            debug_logger.error(f"Error getting field info: {e}")
            return None

    def _generate_hover_documentation(
        self,
        context: HoverContext,
        orm_info: ORMOperationInfo,
        field_info: Dict[str, Any],
    ) -> HoverResult:
        """Generate hover documentation."""
        try:
            # Generate appropriate documentation
            if orm_info.lookup_name:
                documentation = self.doc_generator.generate_field_lookup_documentation(
                    field_info,
                    orm_info.field_name,
                    orm_info.lookup_name,
                    orm_info.model_name,
                )
            else:
                documentation = self.doc_generator.generate_field_documentation(
                    field_info, orm_info.field_name
                )

            # For now, return None for range since the new parser doesn't have complex position handling
            # This can be enhanced later if needed
            range_obj = None

            return HoverResult(
                documentation=documentation.value
                if hasattr(documentation, "value")
                else str(documentation),
                range=range_obj,
                success=True,
            )

        except Exception as e:
            debug_logger.error(f"Error generating hover documentation: {e}")
            return HoverResult(
                documentation="", range=None, success=False, error_message=str(e)
            )

    def _extract_word_under_cursor(self, node: Any, source: str) -> Optional[str]:
        """Extract the word under the cursor from a Tree-sitter node."""
        try:
            return self._find_identifier_in_node(node)
        except Exception as e:
            debug_logger.error(f"Error extracting word under cursor: {e}")
            return None

    def _find_identifier_in_node(self, node: Any) -> Optional[str]:
        """Recursively find identifier in node tree."""
        if not node:
            return None

        # Handle keyword_argument nodes
        if node.type == "keyword_argument":
            for child in node.children:
                if child.type == "identifier":
                    return self._decode_node_text(child)
            # Check parent
            return self._find_identifier_in_node(getattr(node, "parent", None))

        # Handle argument_list nodes
        elif node.type == "argument_list":
            for child in node.children:
                if child.type == "keyword_argument":
                    for grandchild in child.children:
                        if grandchild.type == "identifier":
                            return self._decode_node_text(grandchild)
            # Check parent
            return self._find_identifier_in_node(getattr(node, "parent", None))

        # Handle identifier nodes
        elif node.type == "identifier":
            return self._decode_node_text(node)

        # Check parent
        return self._find_identifier_in_node(getattr(node, "parent", None))

    def _decode_node_text(self, node: Any) -> str:
        """Safely decode node text."""
        try:
            if hasattr(node, "text"):
                return str(node.text.decode("utf8"))
            return ""
        except Exception:
            return ""

    def _calculate_hover_range(self, node: Any) -> Optional[types.Range]:
        """Calculate the range for the hover based on the node position."""
        try:
            start_point = node.start_point
            end_point = node.end_point

            return types.Range(
                start=types.Position(line=start_point[0], character=start_point[1]),
                end=types.Position(line=end_point[0], character=end_point[1]),
            )

        except Exception as e:
            debug_logger.error(f"Error calculating hover range: {e}")
            return None

    def _get_workspace_root_from_uri(self, uri: str) -> Optional[str]:
        """
        Extract workspace root from document URI.

        Args:
            uri: The document URI

        Returns:
            Workspace root path or None if not found
        """
        if not uri.startswith("file://"):
            return None

        # Extract file path from URI
        file_path = uri.replace("file://", "")

        # Find the workspace root by looking for Django project files
        import os

        current_dir = os.path.dirname(file_path)

        # Look for manage.py or settings.py to identify Django project root
        while current_dir and current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, "manage.py")) or os.path.exists(
                os.path.join(current_dir, "settings.py")
            ):
                return str(current_dir)
            current_dir = os.path.dirname(current_dir)

        # Fallback: use the directory containing the file
        return str(os.path.dirname(file_path))

    def update_config(self, config: Dict[str, Any]) -> None:
        """Update the feature configuration."""
        self.config = config
        debug_logger.debug("Hover feature config updated")
