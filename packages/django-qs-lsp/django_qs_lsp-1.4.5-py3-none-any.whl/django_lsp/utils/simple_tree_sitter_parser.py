"""
Simplified Tree-sitter based ORM parser for Django LSP.

This module provides a clean, elegant implementation using Tree-sitter's
built-in APIs for parsing Python code and detecting Django ORM operations.
Only handles complete, valid syntax - broken code is not our problem.
"""

from typing import Any, Dict, List, Optional, Set

from tree_sitter import Language, Node, Parser, Query
from tree_sitter_python import language as python_language

from ..utils.logging import get_debug_logger

debug_logger = get_debug_logger("tree_sitter_parser")


class TreeSitterParser:
    """
    Simplified Tree-sitter parser that leverages built-in APIs.

    This parser focuses on Django ORM pattern detection using a single
    comprehensive query. Only handles complete, valid syntax.
    """

    def __init__(self) -> None:
        """Initialize the Tree-sitter parser."""
        self.language: Optional[Language] = None
        self.parser: Optional[Parser] = None
        self.orm_query: Optional[Query] = None

        self._setup_language()
        self._setup_queries()

    def _setup_language(self) -> None:
        """Setup Tree-sitter Python language."""
        try:
            self.language = Language(python_language())
            self.parser = Parser()
            self.parser.language = self.language
            debug_logger.debug("Tree-sitter Python language loaded successfully")
        except Exception as e:
            debug_logger.warning(f"Could not load Tree-sitter Python language: {e}")
            self.language = None
            self.parser = None

    def _setup_queries(self) -> None:
        """Setup a single comprehensive query for ORM detection."""
        if not self.language:
            return

        try:
            # Single comprehensive query for complete ORM patterns only
            self.orm_query = self.language.query("""
                ; Complete ORM calls: Model.manager.operation(args)
                (call
                  function: (attribute
                    object: (attribute
                      object: (identifier) @model
                      attribute: (identifier) @manager)
                    attribute: (identifier) @operation)
                  arguments: (argument_list) @args)

                ; Chained operations: Model.manager.operation().operation()
                (call
                  function: (attribute
                    object: (call
                      function: (attribute
                        object: (attribute
                          object: (identifier) @model
                          attribute: (identifier) @manager)
                        attribute: (identifier) @operation1)
                      arguments: (argument_list) @args1)
                    attribute: (identifier) @operation2)
                  arguments: (argument_list) @args2)

                ; Self-referencing ORM calls: self.manager.operation(args)
                (call
                  function: (attribute
                    object: (attribute
                      object: (identifier) @self_model
                      attribute: (identifier) @manager)
                    attribute: (identifier) @operation)
                  arguments: (argument_list) @args)
            """)

            debug_logger.debug("Tree-sitter ORM query setup completed successfully")
        except Exception as e:
            debug_logger.warning(f"Could not setup Tree-sitter ORM query: {e}")

    def parse(self, source: str) -> Optional[Node]:
        """Parse source code and return root node."""
        if not self.parser:
            return None

        try:
            # Tree-sitter parser expects bytes, but nodes return strings
            source_bytes = bytes(source, "utf8")
            tree = self.parser.parse(source_bytes)
            return tree.root_node
        except Exception as e:
            debug_logger.error(f"Error parsing source: {e}")
            return None

    def get_completion_context(
        self, source: str, cursor_line: int, cursor_col: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get completion context at the given position.

        Args:
            source: Python source code
            cursor_line: 1-based line number
            cursor_col: 0-based column number

        Returns:
            Dictionary with ORM context or None
        """
        try:
            root_node = self.parse(source)
            if not root_node:
                return None

            # Convert to Tree-sitter coordinates (0-based)
            ts_line = cursor_line - 1
            ts_col = cursor_col

            # Find any ORM call that contains the cursor position
            orm_operations = self.extract_orm_operations_with_ranges(source)
            debug_logger.debug(
                f"Found {len(orm_operations)} ORM operations: {[op.get('model_name', '?') + '.' + op.get('operation_name', '?') for op in orm_operations]}"
            )

            for orm_op in orm_operations:
                call_node = orm_op.get("call_node")
                if call_node:
                    start_line, start_col = call_node.start_point
                    end_line, end_col = call_node.end_point
                    debug_logger.debug(
                        f"Checking ORM op {orm_op.get('model_name', '?')}.{orm_op.get('operation_name', '?')} at range ({start_line}, {start_col}) to ({end_line}, {end_col}) vs cursor ({ts_line}, {ts_col})"
                    )

                    # Check if cursor is within this ORM call
                    if (
                        start_line <= ts_line <= end_line
                        and (ts_line > start_line or ts_col >= start_col)
                        and (ts_line < end_line or ts_col <= end_col)
                    ):
                        context = {
                            "model_name": orm_op["model_name"],
                            "manager_name": orm_op["manager_name"],
                            "operation_name": orm_op["operation_name"],
                            "call_node": call_node,
                            "is_self": orm_op.get("is_self", False),
                            "context_type": "orm_call",
                            "cursor_line": cursor_line,
                            "cursor_col": cursor_col,
                        }
                        debug_logger.debug(f"Found ORM context: {context}")
                        return context

            debug_logger.debug(
                f"No ORM context found for cursor at ({ts_line}, {ts_col})"
            )
            return None

        except Exception as e:
            debug_logger.error(f"Error in get_completion_context: {e}")
            return None

    def extract_current_argument(
        self, source: str, cursor_line: int, cursor_col: int
    ) -> str:
        """
        Extract the text of the argument at the cursor position.

        Args:
            source: Source code as bytes
            cursor_line: 1-based line number
            cursor_col: 0-based column number

        Returns:
            The text of the current argument, or empty string if not in an argument
        """
        try:
            # Convert to Tree-sitter coordinates
            ts_line = cursor_line - 1
            ts_col = cursor_col

            # Find ORM operations
            orm_operations = self.extract_orm_operations_with_ranges(source)

            # Find the ORM operation that contains the cursor
            for orm_op in orm_operations:
                call_node = orm_op.get("call_node")
                if call_node:
                    start_line, start_col = call_node.start_point
                    end_line, end_col = call_node.end_point

                    # Check if cursor is within this ORM call
                    if (
                        start_line <= ts_line <= end_line
                        and (ts_line > start_line or ts_col >= start_col)
                        and (ts_line < end_line or ts_col <= end_col)
                    ):
                        # Find the argument_list node
                        argument_list = None
                        for child in call_node.children:
                            if child.type == "argument_list":
                                argument_list = child
                                break

                        if not argument_list:
                            return ""

                        # Check if cursor is inside any argument node
                        for child in argument_list.children:
                            if child.type in ["keyword_argument", "argument"]:
                                start_line, start_col = child.start_point
                                end_line, end_col = child.end_point

                                # Check if cursor is within this argument
                                if (
                                    start_line <= ts_line <= end_line
                                    and (ts_line > start_line or ts_col >= start_col)
                                    and (ts_line < end_line or ts_col <= end_col)
                                ):
                                    # Cursor is inside this argument, return its text
                                    if child.text:
                                        # child.text is already a string, no need to decode
                                        return str(child.text)
                                    return ""

                        # Cursor is not inside any argument, return empty string
                        return ""

            return ""

        except Exception as e:
            debug_logger.error(f"Error extracting current argument: {e}")
            return ""

    def extract_field_name_at_position(
        self, source: str, cursor_line: int, cursor_col: int
    ) -> str:
        """
        Extract just the field name part when the cursor is positioned after a field path ending with __.

        This method is specifically for field completion scenarios like:
        - "title__" -> returns "username__"
        - "author__username__" -> returns "author__"

        Args:
            source: Source code as string
            cursor_line: 1-based line number
            cursor_col: 0-based column number

        Returns:
            The field name part ending with __, or empty string if not applicable
        """
        try:
            # Convert to Tree-sitter coordinates
            ts_line = cursor_line - 1
            ts_col = cursor_col

            # Find ORM operations
            orm_operations = self.extract_orm_operations_with_ranges(source)

            # Find the ORM operation that contains the cursor
            for orm_op in orm_operations:
                call_node = orm_op.get("call_node")
                if call_node:
                    start_line, start_col = call_node.start_point
                    end_line, end_col = call_node.end_point

                    # Check if cursor is within this ORM call
                    if (
                        start_line <= ts_line <= end_line
                        and (ts_line > start_line or ts_col >= start_col)
                        and (ts_line < end_line or ts_col <= end_col)
                    ):
                        # Find the argument_list node
                        argument_list = None
                        for child in call_node.children:
                            if child.type == "argument_list":
                                argument_list = child
                                break

                        if not argument_list:
                            return ""

                        # Look for arguments that contain the cursor
                        for child in argument_list.children:
                            if child.type in ["keyword_argument", "argument"]:
                                start_line, start_col = child.start_point
                                end_line, end_col = child.end_point

                                # Check if cursor is within this argument
                                if (
                                    start_line <= ts_line <= end_line
                                    and (ts_line > start_line or ts_col >= start_col)
                                    and (ts_line < end_line or ts_col <= end_col)
                                ):
                                    # Get the argument text
                                    if not child.text:
                                        continue

                                    arg_text = child.text

                                    # Check if this looks like a field path ending with __
                                    if "__" in arg_text:
                                        # Find the position of the last __
                                        last_underscore_pos = arg_text.rfind("__")

                                        # Check if cursor is positioned after the last __
                                        # We need to calculate the relative position within the argument
                                        if ts_line == start_line:
                                            relative_col = ts_col - start_col
                                            if (
                                                relative_col > last_underscore_pos + 1
                                            ):  # +1 for the second underscore
                                                # Cursor is after the last __, return the field path
                                                return str(
                                                    arg_text[: last_underscore_pos + 2]
                                                )  # Include both underscores

                                        # For multi-line arguments, check if cursor is on a line after the __
                                        elif ts_line > start_line:
                                            # Cursor is on a later line, assume it's after the field path
                                            return str(
                                                arg_text[: last_underscore_pos + 2]
                                            )

                        return ""

            return ""

        except Exception as e:
            debug_logger.error(f"Error extracting field name at position: {e}")
            return ""

    def extract_orm_operations_with_ranges(self, source: str) -> List[Dict[str, Any]]:
        """
        Extract all ORM operations from source with their position ranges.

        Args:
            source: Python source code to analyze

        Returns:
            List of ORM operations with position ranges and context
        """
        try:
            root_node = self.parse(source)
            if not root_node:
                return []

            orm_operations = []
            # At this point, root_node is guaranteed to be not None
            assert root_node is not None

            if not self.orm_query:
                return []

            matches = self.orm_query.matches(root_node)

            for _match_id, captures in matches:
                orm_info = self._extract_orm_info_from_captures(captures)
                if orm_info:
                    call_node = orm_info.get("call_node")
                    if call_node:
                        # Find the argument_list node to get the range where users type
                        argument_list_node = None
                        for child in call_node.children:
                            if child.type == "argument_list":
                                argument_list_node = child
                                break

                        if argument_list_node:
                            # Use the argument_list node's range - this covers the area
                            # inside the parentheses where the user types
                            range_info = self._extract_node_range(argument_list_node)
                            if range_info:
                                orm_operations.append({**orm_info, **range_info})

            return orm_operations

        except Exception as e:
            debug_logger.error(f"Error extracting ORM operations: {e}")
            return []

    def analyze_imports(self, source: str) -> Dict[str, str]:
        """
        Analyze Python source code to detect available Django models.

        Args:
            source: Python source code to analyze

        Returns:
            Dictionary mapping model names to their full import paths
        """
        root_node = self.parse(source)
        if not root_node:
            return {}

        imports: Dict[str, str] = {}
        self._collect_imports_recursive(root_node, imports)
        self._collect_class_definitions(root_node, imports)
        return imports

    def get_defined_classes(self, source: str) -> Set[str]:
        """Return names of classes defined in the source."""
        result: Set[str] = set()
        root_node = self.parse(source)
        if not root_node:
            return result

        self._collect_class_definitions(root_node, result)
        return result

    def resolve_self_to_class_name(
        self, document_source: str, line_number: int
    ) -> Optional[str]:
        """
        Resolve 'self' to the enclosing class name using Tree-sitter.

        Args:
            document_source: The document source code
            line_number: Line number (0-based from LSP)

        Returns:
            Enclosing class name or None
        """
        try:
            tree_sitter_line = line_number + 1
            root_node = self.parse(document_source)
            if not root_node:
                return None

            cursor_node = root_node.named_descendant_for_point_range(
                (tree_sitter_line, 0), (tree_sitter_line, 0)
            )

            if not cursor_node:
                return None

            return self._find_enclosing_class_name(cursor_node)

        except Exception as e:
            debug_logger.debug(f"Tree-sitter self resolution failed: {e}")
            return None

    def resolve_model_name_if_self(
        self, model_name: str, document_source: str, line_number: int
    ) -> str:
        """
        Resolve model name to class name if it's 'self', otherwise return as-is.

        Args:
            model_name: The model name to resolve
            document_source: The document source code
            line_number: Line number (0-based)

        Returns:
            Resolved model name or original if not 'self'
        """
        if model_name == "self":
            resolved_model_name = self.resolve_self_to_class_name(
                document_source, line_number
            )
            if resolved_model_name:
                return resolved_model_name
            else:
                return model_name
        else:
            return model_name

    def _find_orm_context_upward(self, node: Node) -> Optional[Dict[str, Any]]:
        """Find ORM context by walking up the tree from a given node."""
        current: Optional[Node] = node

        while current:
            if current.type == "call":
                orm_info = self._extract_orm_info_from_call_node(current)
                if orm_info:
                    return orm_info

            if current.type == "class_definition":
                class_name = self._get_class_name(current)
                if class_name in ["Meta", "Options"]:
                    current = current.parent
                    continue

            current = current.parent

        return None

    def _extract_orm_info_from_call_node(
        self, call_node: Node
    ) -> Optional[Dict[str, Any]]:
        """Extract ORM information from a call node."""
        try:
            if len(call_node.children) < 2:
                return None

            function_node = call_node.children[0]
            if function_node.type != "attribute":
                return None

            # Extract the attribute chain
            attr_chain = self._extract_attribute_chain(function_node)

            if len(attr_chain) < 3:
                return None

            # Check if it matches the ORM pattern: Model.manager.operation
            model_name = attr_chain[0]
            manager_attr = attr_chain[1]
            operation_name = attr_chain[2]

            # Check if this looks like a Django ORM operation
            if manager_attr == "objects" and operation_name in [
                "filter",
                "exclude",
                "get",
                "all",
                "count",
                "annotate",
                "order_by",
            ]:
                return {
                    "model_name": model_name,
                    "manager_name": manager_attr,
                    "operation_name": operation_name,
                    "call_node": call_node,
                    "is_self": model_name == "self",
                    "context_type": "orm_call",
                }

            return None

        except Exception as e:
            debug_logger.debug(f"Error extracting ORM info from call node: {e}")
            return None

    def _extract_orm_info_from_captures(
        self, captures: Dict[str, List[Node]]
    ) -> Optional[Dict[str, Any]]:
        """Extract ORM information from Tree-sitter query captures."""
        try:
            model_nodes = captures.get("model", []) or captures.get("self_model", [])
            if not model_nodes:
                return None
            model_name = (
                model_nodes[0].text.decode("utf-8") if model_nodes[0].text else ""
            )

            manager_nodes = captures.get("manager", [])
            if not manager_nodes:
                return None
            manager_name = (
                manager_nodes[0].text.decode("utf-8") if manager_nodes[0].text else ""
            )

            operation_nodes = (
                captures.get("operation", [])
                or captures.get("operation1", [])
                or captures.get("operation2", [])
            )
            if not operation_nodes:
                return None
            operation_name = (
                operation_nodes[0].text.decode("utf-8")
                if operation_nodes[0].text
                else ""
            )

            call_node = None
            if operation_nodes:
                current: Optional[Node] = operation_nodes[0]
                while current and current.type != "call":
                    current = current.parent
                if current and current.type == "call":
                    call_node = current

            if not call_node:
                return None

            return {
                "model_name": model_name,
                "manager_name": manager_name,
                "operation_name": operation_name,
                "call_node": call_node,
                "is_self": model_name == "self",
                "context_type": "orm_call",
            }

        except Exception as e:
            debug_logger.debug(f"Error extracting ORM info from captures: {e}")
            return None

    def _extract_attribute_chain(self, attr_node: Node) -> List[str]:
        """Extract the attribute chain from a Tree-sitter attribute node."""
        chain: List[str] = []
        current: Optional[Node] = attr_node

        while current and current.type == "attribute":
            if len(current.children) >= 3:
                object_node = current.children[0]
                attribute_name_node = current.children[2]

                if attribute_name_node and attribute_name_node.text:
                    attr_name = attribute_name_node.text.decode("utf-8")
                    chain.insert(0, attr_name)

                current = object_node if object_node else None
            else:
                break

        if current and current.type == "identifier" and current.text:
            base_name = current.text.decode("utf-8")
            chain.insert(0, base_name)

        return chain

    def _extract_node_range(self, node: Node) -> Optional[Dict[str, int]]:
        """Extract position range from a Tree-sitter node."""
        try:
            start_line, start_col = node.start_point
            end_line, end_col = node.end_point

            return {
                "range_start_line": start_line,
                "range_start_character": start_col,
                "range_end_line": end_line,
                "range_end_character": end_col,
            }
        except Exception as e:
            debug_logger.debug(f"Failed to extract node range: {e}")
            return None

    def _collect_imports_recursive(self, node: Node, imports: Dict[str, str]) -> None:
        """Recursively collect import statements from the AST."""
        if node.type == "import_statement":
            for child in node.children:
                if child.type == "dotted_name" and child.text:
                    module = (
                        child.text.decode("utf-8")
                        if isinstance(child.text, bytes)
                        else str(child.text)
                    )
                    imports[module] = module
                elif child.type == "aliased_import":
                    module_node = None
                    alias_node = None
                    for grandchild in child.children:
                        if grandchild.type == "dotted_name":
                            module_node = grandchild
                        elif grandchild.type == "identifier":
                            alias_node = grandchild

                    if (
                        module_node
                        and alias_node
                        and module_node.text
                        and alias_node.text
                    ):
                        module = (
                            module_node.text.decode("utf-8")
                            if isinstance(module_node.text, bytes)
                            else str(module_node.text)
                        )
                        alias = (
                            alias_node.text.decode("utf-8")
                            if isinstance(alias_node.text, bytes)
                            else str(alias_node.text)
                        )
                        imports[alias] = module

        elif node.type == "import_from_statement":
            from_module = None
            import_name = None

            for child in node.children:
                if child.type == "dotted_name":
                    if from_module is None:
                        from_module = (
                            child.text.decode("utf-8")
                            if isinstance(child.text, bytes)
                            else str(child.text)
                            if child.text
                            else ""
                        )
                    else:
                        import_name = (
                            child.text.decode("utf-8")
                            if isinstance(child.text, bytes)
                            else str(child.text)
                            if child.text
                            else ""
                        )

            if from_module and import_name:
                imports[import_name] = from_module

        for child in node.children:
            self._collect_imports_recursive(child, imports)

    def _collect_class_definitions(self, node: Node, result: Any) -> None:
        """Recursively collect class definitions from the AST."""
        if node.type == "class_definition":
            for child in node.children:
                if child.type == "identifier" and child.text:
                    class_name = (
                        child.text.decode("utf-8")
                        if isinstance(child.text, bytes)
                        else str(child.text)
                    )
                    if isinstance(result, dict):
                        result[class_name] = class_name
                    elif isinstance(result, set):
                        result.add(class_name)
                    break

        for child in node.children:
            self._collect_class_definitions(child, result)

    def _find_enclosing_class_name(self, node: Node) -> Optional[str]:
        """Find the name of the enclosing class by walking up the tree."""
        current: Optional[Node] = node

        while current:
            if current.type == "class_definition":
                class_name = self._get_class_name(current)
                if class_name and class_name not in ["Meta", "Options"]:
                    return class_name
            current = current.parent

        return None

    def _get_class_name(self, class_node: Node) -> Optional[str]:
        """Extract the class name from a class definition node."""
        if not class_node.children:
            return None

        # Find the first identifier child with text
        identifier_children = [
            child
            for child in class_node.children
            if child.type == "identifier" and child.text
        ]

        if not identifier_children:
            return None

        # Get the first matching child's text
        child = identifier_children[0]
        if isinstance(child.text, bytes):
            return child.text.decode("utf-8")
        else:
            return str(child.text)
