"""
Django LSP server using standard pygls pattern.

This module implements the Django ORM Language Server Protocol server
using the standard pygls decorator pattern with proper type annotations.
"""

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from lsprotocol import types
from pygls.server import LanguageServer

from .core import DjangoSetup, ModelLoader
from .features import CompletionFeature, HoverFeature
from .utils.document_cache import DocumentCache
from .utils.logging import (
    get_debug_logger,
    get_logger,
    set_lsp_server,
    set_server_for_all_loggers,
    setup_logging,
)
from .utils.parser_cache import (
    get_parser_cache,
)

# Set up logging
setup_logging()
lsp_logger = get_logger("server", use_lsp=True)
debug_logger = get_debug_logger("server")

# Initialize the Language Server
server = LanguageServer("django-lsp", "v0.1")


@dataclass
class ServerConfig:
    """Server configuration with proper type safety."""

    django_settings_module: Optional[str] = None
    workspace_roots: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.workspace_roots is None:
            self.workspace_roots = []


@dataclass
class ServerState:
    """Server state management."""

    config: ServerConfig
    background_tasks: set[asyncio.Task[Any]] = field(default_factory=set)
    django_setup: Optional[DjangoSetup] = None
    model_loader: Optional[ModelLoader] = None
    document_cache: Optional[DocumentCache] = None
    completion_feature: Optional[CompletionFeature] = None
    hover_feature: Optional[HoverFeature] = None

    def __post_init__(self) -> None:
        # Initialize core components
        self.django_setup = DjangoSetup()
        self.model_loader = ModelLoader()

        # Initialize document cache for efficient model loading
        self.document_cache = DocumentCache(self.model_loader)

        # Features will be initialized after Django setup


class ServerInitializer:
    """Handles server initialization logic."""

    def __init__(self, state: ServerState):
        self.state = state

    def initialize_server(
        self, ls: LanguageServer, params: types.InitializeParams
    ) -> types.InitializeResult:
        """Initialize the LSP server."""
        try:
            # Set up logging infrastructure
            self._setup_logging(ls)

            # Extract configuration
            self._extract_configuration(params)

            # Set up workspaces
            self._setup_workspaces(params, ls)

            # Configure server capabilities
            capabilities = self._configure_capabilities()

            return types.InitializeResult(capabilities=capabilities)

        except Exception as e:
            debug_logger.error(f"Server initialization failed: {e}", exc_info=True)
            # Return minimal capabilities on failure
            return types.InitializeResult(
                capabilities=types.ServerCapabilities(
                    text_document_sync=types.TextDocumentSyncOptions(
                        open_close=True,
                        change=types.TextDocumentSyncKind.Incremental,
                    )
                )
            )

    def _setup_logging(self, ls: LanguageServer) -> None:
        """Set up logging infrastructure."""
        set_lsp_server(ls)
        set_server_for_all_loggers(ls)

        # Enable debug logging if environment variable is set
        if os.environ.get("DJANGO_LSP_DEBUG", "").lower() in ("true", "1", "yes"):
            debug_logger.debug("Debug logging enabled via environment variable")

        debug_logger.debug("Logging infrastructure initialized")

    def _extract_configuration(self, params: types.InitializeParams) -> None:
        """Extract configuration from initialization parameters."""
        if params.initialization_options:
            # Enable debug logging if requested
            debug_enabled = params.initialization_options.get("debug", False)
            if debug_enabled:
                os.environ["DJANGO_LSP_DEBUG"] = "true"
                # Update config to reflect the new environment variable
                from .config import config

                config.update_from_environment()
                debug_logger.debug("Debug logging enabled via initialization options")

            django_settings_module = params.initialization_options.get(
                "djangoSettingsModule"
            )
            if django_settings_module:
                self.state.config.django_settings_module = django_settings_module
                os.environ["DJANGO_SETTINGS_MODULE"] = django_settings_module
                debug_logger.debug(
                    f"Django settings module configured: {django_settings_module}"
                )

    def _setup_workspaces(
        self, params: types.InitializeParams, ls: LanguageServer
    ) -> None:
        """Set up Django for workspaces with improved error handling."""
        workspace_roots = self._extract_workspace_roots(params, ls)

        debug_logger.debug(
            f"Setting up Django for {len(workspace_roots)} workspace(s): {workspace_roots}"
        )

        # If no workspace roots but we have Django settings module, try standalone setup
        if not workspace_roots and self.state.config.django_settings_module:
            debug_logger.debug(
                "No workspace roots found, attempting standalone Django setup"
            )
            try:
                if self.state.django_setup is not None:
                    success = self.state.django_setup.configure_django(
                        self.state.config.django_settings_module
                    )
                    if success:
                        debug_logger.debug("Standalone Django setup successful")

                        # Initialize features after Django is set up
                        try:
                            initialize_features()
                            debug_logger.debug("Features initialized successfully")
                        except Exception as e:
                            debug_logger.error(f"Failed to initialize features: {e}")

                        return
                    else:
                        lsp_logger.warning("Standalone Django setup failed")
            except Exception as e:
                debug_logger.error(f"Standalone Django setup error: {e}")
            return

        # Set up Django for each workspace
        for workspace_root in workspace_roots:
            try:
                debug_logger.debug(f"Setting up Django for workspace: {workspace_root}")
                if self.state.django_setup is not None:
                    success = self.state.django_setup.setup(workspace_root)
                    if success:
                        debug_logger.debug(
                            f"Django setup successful for: {workspace_root}"
                        )
                        # If we have a settings module, also configure it
                        if self.state.config.django_settings_module:
                            self.state.django_setup.configure_django(
                                self.state.config.django_settings_module
                            )
                        # Warm model cache for this workspace to avoid first-hit latency
                        try:
                            if self.state.document_cache is not None:
                                self.state.document_cache.get_models_for_workspace(
                                    workspace_root
                                )
                        except Exception as e:
                            debug_logger.debug(
                                f"Model preloading failed for {workspace_root}: {e}"
                            )

                        # Initialize features after Django is set up
                        try:
                            initialize_features()
                            debug_logger.debug("Features initialized successfully")
                        except Exception as e:
                            debug_logger.error(f"Failed to initialize features: {e}")

                        return  # Successfully set up, no need to try other workspaces
                    else:
                        lsp_logger.warning(f"Django setup failed for: {workspace_root}")
            except Exception as e:
                debug_logger.error(f"Django setup error for {workspace_root}: {e}")

        # If we get here, no workspace setup succeeded
        if workspace_roots:
            debug_logger.error(
                f"Failed to set up Django for any workspace: {workspace_roots}"
            )
        else:
            debug_logger.error("No workspace roots found and standalone setup failed")

    def _extract_workspace_roots(
        self, params: types.InitializeParams, ls: LanguageServer
    ) -> List[str]:
        """Extract workspace roots from various sources with improved VS Code support."""
        roots = []

        debug_logger.debug("Extracting workspace roots from params:")
        debug_logger.debug(f"  - workspace_folders: {params.workspace_folders}")
        debug_logger.debug(f"  - root_uri: {params.root_uri}")
        debug_logger.debug(f"  - root_path: {params.root_path}")
        debug_logger.debug(
            f"  - initialization_options: {params.initialization_options}"
        )

        # Handle workspace folders (multi-root workspaces) - VS Code standard
        if params.workspace_folders:
            for folder in params.workspace_folders:
                if folder.uri.startswith("file://"):
                    root = folder.uri.replace("file://", "")
                    roots.append(root)
                    debug_logger.debug(f"Added workspace folder: {root}")

        # Handle single workspace via root_uri
        elif params.root_uri and params.root_uri.startswith("file://"):
            root = params.root_uri.replace("file://", "")
            roots.append(root)
            debug_logger.debug(f"Added single workspace from root_uri: {root}")

        # Handle single workspace via root_path
        elif params.root_path:
            roots.append(params.root_path)
            debug_logger.debug(f"Added workspace from root_path: {params.root_path}")

        # Fallback to server workspace (pygls internal)
        if not roots:
            debug_logger.debug(
                "No workspace roots found in params, checking pygls workspace"
            )
            if hasattr(ls.workspace, "root_path") and ls.workspace.root_path:
                roots.append(ls.workspace.root_path)
                debug_logger.debug(
                    f"Added workspace from pygls root_path: {ls.workspace.root_path}"
                )
            elif hasattr(ls.workspace, "root_uri") and ls.workspace.root_uri:
                root = ls.workspace.root_uri.replace("file://", "")
                roots.append(root)
                debug_logger.debug(f"Added workspace from pygls root_uri: {root}")

        # Fallback to current working directory if no workspace roots found
        if not roots:
            debug_logger.debug(
                "No workspace roots found, checking current working directory"
            )
            import os

            cwd = os.getcwd()
            debug_logger.debug(f"Current working directory: {cwd}")

            # Check if current working directory looks like a Django project
            manage_py_path = os.path.join(cwd, "manage.py")
            if os.path.exists(manage_py_path):
                roots.append(cwd)
                debug_logger.debug(
                    f"Added workspace from current working directory: {cwd}"
                )
            else:
                debug_logger.debug(
                    f"Current working directory {cwd} does not contain manage.py"
                )

        # If still no roots, try to extract from initialization options
        if not roots and params.initialization_options:
            debug_logger.debug(
                "No workspace roots found, checking initialization options"
            )
            # Some clients might pass workspace info in initialization options
            workspace_info = params.initialization_options.get("workspace")
            if workspace_info:
                if isinstance(workspace_info, str):
                    roots.append(workspace_info)
                    debug_logger.debug(
                        f"Added workspace from init options: {workspace_info}"
                    )
                elif isinstance(workspace_info, dict):
                    workspace_path = workspace_info.get("path") or workspace_info.get(
                        "rootPath"
                    )
                    if workspace_path:
                        roots.append(workspace_path)
                        debug_logger.debug(
                            f"Added workspace from init options dict: {workspace_path}"
                        )

        # Final fallback: try standalone Django setup if we have settings module
        if not roots and self.state.config.django_settings_module:
            debug_logger.debug(
                "No workspace roots found, attempting standalone Django setup"
            )
            if (
                self.state.django_setup is not None
                and self.state.django_setup.configure_django(
                    self.state.config.django_settings_module
                )
            ):
                debug_logger.debug("Standalone Django setup successful")
                # Return empty list to indicate standalone mode
                return []

        debug_logger.debug(f"Final workspace roots: {roots}")
        return roots

    def _configure_capabilities(self) -> types.ServerCapabilities:
        """Configure server capabilities."""
        return types.ServerCapabilities(
            text_document_sync=types.TextDocumentSyncOptions(
                open_close=True,
                change=types.TextDocumentSyncKind.Incremental,
                will_save=False,
                will_save_wait_until=False,
                save=False,
            ),
            completion_provider=types.CompletionOptions(
                trigger_characters=["(", " ", "_", ".", "="], resolve_provider=True
            ),
            hover_provider=True,
            definition_provider=True,
            references_provider=True,
            document_symbol_provider=True,
            workspace_symbol_provider=True,
            code_action_provider=True,
            execute_command_provider=types.ExecuteCommandOptions(
                commands=[
                    "django-lsp.showModels",
                    "django-lsp.refreshModels",
                    "django-lsp.showFieldInfo",
                    "django-lsp.showLookupInfo",
                    "django-lsp.showCacheInfo",
                    "django-lsp.clearCache",
                    "django-lsp.showWorkspaceInfo",
                ]
            ),
            inlay_hint_provider=types.InlayHintOptions(resolve_provider=False),
            workspace=types.ServerCapabilitiesWorkspaceType(
                workspace_folders=types.WorkspaceFoldersServerCapabilities(
                    supported=True,
                    change_notifications=True,
                ),
            ),
        )


class CommandHandler:
    """Handles custom LSP commands."""

    def __init__(self, state: ServerState):
        self.state = state

    def handle_command(
        self, command: str, arguments: List[Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle custom commands."""
        debug_logger.debug(f"Executing command: {command}")

        command_handlers = {
            "django-lsp.showModels": self._show_models,
            "django-lsp.refreshModels": self._refresh_models,
            "django-lsp.showFieldInfo": self._show_field_info,
            "django-lsp.showLookupInfo": self._show_lookup_info,
            "django-lsp.showCacheInfo": self._show_cache_info,
            "django-lsp.clearCache": self._clear_cache,
            "django-lsp.showWorkspaceInfo": self._show_workspace_info,
        }

        handler = command_handlers.get(command)
        if handler:
            return handler(arguments)

        debug_logger.warning(f"Unknown command: {command}")
        return None

    def _show_models(self, arguments: List[Any]) -> Dict[str, Any]:
        """Show available Django models."""
        if self.state.model_loader is None:
            return {"models": [], "error": "Model loader not initialized"}
        models = self.state.model_loader.load_models()
        model_list = list(models.keys())
        return {"models": model_list}

    def _refresh_models(self, arguments: List[Any]) -> Dict[str, Any]:
        """Refresh the model cache."""
        if self.state.model_loader is None:
            return {"refreshed": False, "error": "Model loader not initialized"}
        self.state.model_loader.clear_cache()
        models = self.state.model_loader.load_models()
        return {"refreshed": True, "modelCount": len(models)}

    def _show_field_info(self, arguments: List[Any]) -> Optional[Dict[str, Any]]:
        """Show information about a specific field."""
        if not arguments or self.state.model_loader is None:
            return None

        model_name = arguments[0]
        field_name = arguments[1] if len(arguments) > 1 else None

        model_info = self.state.model_loader.get_model_info(model_name)
        if not model_info:
            return None

        if field_name:
            # Handle both dataclass and dict formats for backward compatibility
            if hasattr(model_info, "fields"):
                field_info = model_info.fields.get(field_name)
            else:
                # Handle dict format for backward compatibility
                fields_dict = (
                    model_info.get("fields", {}) if isinstance(model_info, dict) else {}
                )
                field_info = fields_dict.get(field_name)

            if field_info:
                field_type_value = (
                    getattr(field_info, "type", None)
                    if not isinstance(field_info, dict)
                    else field_info.get("type")
                )
                lookups_value = (
                    getattr(field_info, "lookups", [])
                    if not isinstance(field_info, dict)
                    else field_info.get("lookups", [])
                )
                return {
                    "model": model_name,
                    "field": field_name,
                    "type": field_type_value,
                    "lookups": lookups_value,
                }

        # Return field list
        if hasattr(model_info, "fields"):
            field_names = list(model_info.fields.keys())
        else:
            field_names = (
                list(model_info.get("fields", {}).keys())
                if isinstance(model_info, dict)
                else []
            )

        return {"model": model_name, "fields": field_names}

    def _show_lookup_info(self, arguments: List[Any]) -> Dict[str, Any]:
        """Show information about field lookups."""
        if not arguments:
            return {"error": "No lookup name provided"}

        lookup_name = arguments[0]
        field_type = arguments[1] if len(arguments) > 1 else "Field"

        return {
            "lookup": lookup_name,
            "fieldType": field_type,
            "description": f"Lookup '{lookup_name}' for {field_type}",
        }

    def _show_cache_info(self, arguments: List[Any]) -> Dict[str, Any]:
        """Show information about the current cache."""
        if self.state.model_loader is None:
            return {"cacheInfo": {}, "error": "Model loader not initialized"}
        cache_info = self.state.model_loader.get_cache_info()
        return {"cacheInfo": cache_info}

    def _clear_cache(self, arguments: List[Any]) -> Dict[str, Any]:
        """Clear the model cache."""
        if self.state.model_loader is None:
            return {"cleared": False, "error": "Model loader not initialized"}
        workspace_root = arguments[0] if arguments else None
        self.state.model_loader.clear_cache(workspace_root)
        return {"cleared": True}

    def _show_workspace_info(self, arguments: List[Any]) -> Dict[str, Any]:
        """Show information about the current workspace."""
        if self.state.django_setup is None:
            return {"workspaceInfo": {}, "error": "Django setup not initialized"}
        workspace_info = self.state.django_setup.get_workspace_info()
        return {"workspaceInfo": workspace_info}


# Initialize server state
server_state = ServerState(config=ServerConfig())
server_initializer = ServerInitializer(server_state)
command_handler = CommandHandler(server_state)


# Initialize features after server state is created
# This avoids circular dependencies during initialization
def initialize_features() -> None:
    """Initialize features after server state is created."""
    if server_state.django_setup is None or server_state.model_loader is None:
        debug_logger.error(
            "Cannot initialize features: django_setup or model_loader is None"
        )
        return

    server_state.completion_feature = CompletionFeature(
        server_state.django_setup,
        server_state.model_loader,
        server,
        server_state.document_cache,
    )
    server_state.hover_feature = HoverFeature(
        server_state.django_setup, server_state.model_loader, server
    )


@server.feature(types.INITIALIZE)
async def initialize(
    ls: LanguageServer, params: types.InitializeParams
) -> types.InitializeResult:
    # Basic logging that doesn't depend on LSP server setup
    debug_logger.info("=== SERVER INITIALIZATION START ===")
    debug_logger.info(f"Client info: {params.client_info}")
    debug_logger.info(f"Client capabilities: {params.capabilities}")
    debug_logger.info(f"Workspace folders: {params.workspace_folders}")
    debug_logger.info(f"Root URI: {params.root_uri}")
    debug_logger.info(f"Root path: {params.root_path}")

    try:
        # Initialize the server
        initializer = ServerInitializer(server_state)
        result = initializer.initialize_server(ls, params)

        debug_logger.info("=== SERVER INITIALIZATION END ===")
        return result

    except Exception as e:
        debug_logger.error(f"Server initialization failed: {e}", exc_info=True)
        # Return minimal capabilities on failure
        return types.InitializeResult(
            capabilities=types.ServerCapabilities(
                text_document_sync=types.TextDocumentSyncOptions(
                    open_close=True,
                    change=types.TextDocumentSyncKind.Full,
                ),
                hover_provider=True,
            )
        )


@server.feature(types.INITIALIZED)
async def initialized(ls: LanguageServer, params: types.InitializedParams) -> None:
    """Handle server initialized event."""
    debug_logger.info("Server initialized")
    initialize_features()


@server.feature(types.WORKSPACE_DID_CHANGE_WORKSPACE_FOLDERS)
async def did_change_workspace_folders(
    ls: LanguageServer, params: types.DidChangeWorkspaceFoldersParams
) -> None:
    """Handle workspace folder changes."""
    debug_logger.info("Workspace folders changed")

    try:
        # Handle added workspace folders
        for folder in params.event.added:
            folder_path = folder.uri.replace("file://", "")
            debug_logger.info(f"Added workspace folder: {folder_path}")

            if folder_path not in (server_state.config.workspace_roots or []):
                if server_state.config.workspace_roots is None:
                    server_state.config.workspace_roots = []
                server_state.config.workspace_roots.append(folder_path)

                # Set up Django for the new workspace
                if server_state.django_setup:
                    server_state.django_setup.setup(folder_path)

        # Handle removed workspace folders
        for folder in params.event.removed:
            folder_path = folder.uri.replace("file://", "")
            debug_logger.info(f"Removed workspace folder: {folder_path}")

            if folder_path in (server_state.config.workspace_roots or []):
                if server_state.config.workspace_roots is not None:
                    server_state.config.workspace_roots.remove(folder_path)

                # Clean up Django setup for the removed workspace
                if server_state.django_setup:
                    server_state.django_setup.reset_workspace(folder_path)

                # Clear caches for the removed workspace
                if server_state.document_cache:
                    server_state.document_cache.clear_workspace(folder_path)

    except Exception as e:
        debug_logger.error(f"Error handling workspace folder changes: {e}")


@server.feature(types.WORKSPACE_DID_CHANGE_CONFIGURATION)
async def did_change_configuration(
    ls: LanguageServer, params: types.DidChangeConfigurationParams
) -> None:
    """Handle configuration changes."""
    debug_logger.info("Configuration changed")

    try:
        # Re-extract configuration from the new settings
        if server_state.django_setup and server_state.config.workspace_roots:
            for workspace_root in server_state.config.workspace_roots:
                server_state.django_setup.setup(workspace_root)

    except Exception as e:
        debug_logger.error(f"Error handling configuration change: {e}")


@server.feature(types.TEXT_DOCUMENT_COMPLETION)
async def completions(
    ls: LanguageServer, params: types.CompletionParams
) -> types.CompletionList:
    """Handle completion requests."""

    # Django should already be set up by now
    if not server_state.completion_feature:
        # This should never happen - server is broken
        lsp_logger.error("Completion feature not initialized - server setup failed")
        return types.CompletionList(is_incomplete=False, items=[])

    try:
        # Get the document source
        document = ls.workspace.get_text_document(params.text_document.uri)
        if not document:
            debug_logger.debug(f"Document not found: {params.text_document.uri}")
            return types.CompletionList(is_incomplete=False, items=[])

        # Get completions from the completion feature
        result = server_state.completion_feature.handle_completion(params)

        # Extract completion items and is_incomplete flag
        completion_items = result.get("items", [])
        is_incomplete = result.get("is_incomplete", False)

        # Return the completion list with proper is_incomplete flag
        return types.CompletionList(is_incomplete=is_incomplete, items=completion_items)

    except Exception as e:
        lsp_logger.error(f"Error in completion handler: {e}")
        return types.CompletionList(is_incomplete=False, items=[])


@server.feature(types.COMPLETION_ITEM_RESOLVE)
async def resolve_completion_item(
    ls: LanguageServer, params: types.CompletionItem
) -> types.CompletionItem:
    """Resolve completion items."""
    if server_state.completion_feature is None:
        return params

    return server_state.completion_feature.resolve_completion_item(params)


@server.feature(types.TEXT_DOCUMENT_HOVER)
async def hover(ls: LanguageServer, params: types.HoverParams) -> Optional[types.Hover]:
    """Handle hover requests."""
    debug_logger.info(
        f"🔍 Hover request received for {params.text_document.uri} at position {params.position.line}:{params.position.character}"
    )

    if server_state.hover_feature is None:
        debug_logger.warning("❌ Hover feature is None")
        return None

    try:
        document = ls.workspace.get_text_document(params.text_document.uri)
        if not document:
            debug_logger.warning("❌ No document found for hover request")
            return None

        debug_logger.info("✅ Found document, calling hover feature handler")
        result = server_state.hover_feature.handle_hover(params, document)

        if result:
            debug_logger.info(
                f"✅ Hover feature returned result with contents: {result.contents}"
            )
        else:
            debug_logger.info("❌ Hover feature returned None")

        return result
    except Exception as e:
        debug_logger.error(f"❌ Hover request failed: {e}", exc_info=True)
        return None


@server.feature(types.TEXT_DOCUMENT_INLAY_HINT)
async def inlay_hints(
    ls: LanguageServer, params: types.InlayHintParams
) -> List[types.InlayHint]:
    """Handle inlay hint requests."""
    # TODO: Implement inlay hints feature
    return []


@server.feature(types.INLAY_HINT_RESOLVE)
async def resolve_inlay_hint(
    ls: LanguageServer, params: types.InlayHint
) -> types.InlayHint:
    """Resolve inlay hint details."""
    # TODO: Implement inlay hint resolution
    return params


@server.feature(types.WORKSPACE_EXECUTE_COMMAND)
async def execute_command(
    ls: LanguageServer, params: types.ExecuteCommandParams
) -> Optional[Dict[str, Any]]:
    """Handle custom commands."""
    return command_handler.handle_command(params.command, params.arguments or [])


async def _parse_document_background(document_uri: str, source: str) -> None:
    """Background task to parse document and cache ORM operations."""
    try:
        debug_logger.debug(f"Background parsing document: {document_uri}")

        workspace_root = _get_workspace_root_from_uri(document_uri)
        if not workspace_root or not server_state.document_cache:
            return

        # Get the tree-sitter parser for this workspace
        parser_cache = get_parser_cache()
        parser = parser_cache.get_parser(workspace_root)

        if not parser:
            debug_logger.debug(
                f"No tree-sitter parser available for workspace: {workspace_root}"
            )
            return

        # Extract ORM operations with position ranges using tree-sitter
        debug_logger.debug(f"Extracting ORM operations from document: {document_uri}")
        orm_operations_raw = parser.extract_orm_operations_with_ranges(source)

        if orm_operations_raw:
            debug_logger.debug(
                f"Found {len(orm_operations_raw)} ORM operations in {document_uri}"
            )

            # Convert raw ORM operations to ORMOperation objects
            from .utils.document_cache import ORMOperation

            orm_operations = []
            for op in orm_operations_raw:
                try:
                    # Resolve 'self' to actual class name if needed
                    model_name = op.get("model_name", "")
                    if model_name == "self":
                        # Get the line number where this ORM operation occurs
                        line_number = op.get("range_start_line", 0)
                        resolved_model_name = parser.resolve_model_name_if_self(
                            model_name, source, line_number
                        )
                        if resolved_model_name and resolved_model_name != "self":
                            model_name = resolved_model_name
                            debug_logger.debug(
                                f"Resolved 'self' to '{model_name}' at line {line_number}"
                            )

                    orm_op = ORMOperation(
                        range_start_line=op.get("range_start_line", 0),
                        range_start_character=op.get("range_start_character", 0),
                        range_end_line=op.get("range_end_line", 0),
                        range_end_character=op.get("range_end_character", 0),
                        model_name=model_name,
                        manager_name=op.get("manager_name", "objects"),
                        operation_name=op.get("operation_name", ""),
                        context_type=op.get("context_type", "unknown"),
                        field_name=op.get("field_name"),
                        lookup_name=op.get("lookup_name"),
                    )
                    orm_operations.append(orm_op)
                except Exception as e:
                    debug_logger.debug(f"Failed to create ORMOperation: {e}")
                    continue

            # Cache the ORM operations in the document cache
            if orm_operations:
                server_state.document_cache.cache_orm_operations(
                    document_uri, orm_operations
                )
                debug_logger.debug(
                    f"Cached {len(orm_operations)} ORM operations for {document_uri}"
                )
        else:
            debug_logger.debug(f"No ORM operations found in {document_uri}")

        debug_logger.debug(f"Background parsing completed for {document_uri}")

    except Exception as e:
        debug_logger.debug(f"Background parsing failed for {document_uri}: {e}")


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: LanguageServer, params: types.DidOpenTextDocumentParams) -> None:
    """Handle document open events."""
    debug_logger.debug(f"Document opened: {params.text_document.uri}")

    # Validate that the document is a Python file
    if not params.text_document.uri.endswith(".py"):
        debug_logger.debug(f"Skipping non-Python document: {params.text_document.uri}")
        return

    try:
        # The document is automatically added to the workspace by pygls
        # We can perform any initialization needed for this document
        document = ls.workspace.get_text_document(params.text_document.uri)
        if document and server_state.document_cache:
            debug_logger.debug(
                f"Document added to workspace: {params.text_document.uri}"
            )

            # Cache the document source immediately (fast)
            server_state.document_cache.cache_document_source(
                document.uri, document.source
            )

            # Queue background parsing using asyncio (non-blocking)
            task = asyncio.create_task(
                _parse_document_background(document.uri, document.source)
            )

            # Add task to the set. This creates a strong reference.
            server_state.background_tasks.add(task)

            # To prevent keeping references to finished tasks forever,
            # make each task remove its own reference from the set after
            # completion:
            task.add_done_callback(server_state.background_tasks.discard)

            # Check if this is a Django model file and invalidate cache if needed
            if _is_likely_django_model_file(params.text_document.uri):
                workspace_root = _get_workspace_root_from_uri(params.text_document.uri)
                if workspace_root:
                    debug_logger.debug(
                        f"Invalidating model cache for workspace: {workspace_root}"
                    )
                    server_state.document_cache.invalidate_workspace_models(
                        workspace_root
                    )

    except Exception as e:
        debug_logger.error(
            f"Error handling document open for {params.text_document.uri}: {e}"
        )


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
async def did_change(
    ls: LanguageServer, params: types.DidChangeTextDocumentParams
) -> None:
    """Handle document change events."""
    debug_logger.debug(f"Document changed: {params.text_document.uri}")

    # Validate that the document is a Python file
    if not params.text_document.uri.endswith(".py"):
        debug_logger.debug(f"Skipping non-Python document: {params.text_document.uri}")
        return

    try:
        # Get the updated document content
        document = ls.workspace.get_text_document(params.text_document.uri)
        if not document or not server_state.document_cache:
            debug_logger.debug(f"Document not found: {params.text_document.uri}")
            return

        # Update cached document source immediately (fast)
        server_state.document_cache.cache_document_source(document.uri, document.source)

        # Queue background parsing for the updated document (non-blocking)
        task = asyncio.create_task(
            _parse_document_background(document.uri, document.source)
        )

        # Add task to the set. This creates a strong reference.
        server_state.background_tasks.add(task)

        # To prevent keeping references to finished tasks forever,
        # make each task remove its own reference from the set after
        # completion:
        task.add_done_callback(server_state.background_tasks.discard)

        # Check if this is a Django model file and invalidate cache if needed
        if _is_likely_django_model_file(params.text_document.uri):
            workspace_root = _get_workspace_root_from_uri(params.text_document.uri)
            if workspace_root:
                debug_logger.debug(
                    f"Invalidating model cache for workspace: {workspace_root}"
                )
                server_state.document_cache.invalidate_workspace_models(workspace_root)

    except Exception as e:
        debug_logger.debug(f"Error handling document change: {e}")


@server.feature(types.TEXT_DOCUMENT_DID_CLOSE)
async def did_close(
    ls: LanguageServer, params: types.DidCloseTextDocumentParams
) -> None:
    """Handle document close events."""
    debug_logger.debug(f"Document closed: {params.text_document.uri}")

    try:
        # The document is automatically removed from the workspace by pygls
        # We can perform any cleanup needed for this document
        if server_state.document_cache:
            # Invalidate cached data for this document
            server_state.document_cache.invalidate_document(params.text_document.uri)
            debug_logger.debug(
                f"Invalidated cache for closed document: {params.text_document.uri}"
            )

    except Exception as e:
        debug_logger.debug(f"Error handling document close: {e}")


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls: LanguageServer, params: types.DidSaveTextDocumentParams) -> None:
    """Handle document save events."""
    debug_logger.debug(f"Document saved: {params.text_document.uri}")

    # Validate that the document is a Python file
    if not params.text_document.uri.endswith(".py"):
        debug_logger.debug(f"Skipping non-Python document: {params.text_document.uri}")
        return

    try:
        # Get the saved document content
        document = ls.workspace.get_text_document(params.text_document.uri)
        if not document or not server_state.document_cache:
            debug_logger.debug(f"Document not found: {params.text_document.uri}")
            return

        # Update cached document source immediately (fast)
        server_state.document_cache.cache_document_source(document.uri, document.source)

        # Queue background parsing for the saved document (non-blocking)
        task = asyncio.create_task(
            _parse_document_background(document.uri, document.source)
        )

        # Add task to the set. This creates a strong reference.
        server_state.background_tasks.add(task)

        # To prevent keeping references to finished tasks forever,
        # make each task remove its own reference from the set after
        # completion:
        task.add_done_callback(server_state.background_tasks.discard)

        # Check if this is a Django model file and invalidate cache if needed
        if _is_likely_django_model_file(params.text_document.uri):
            workspace_root = _get_workspace_root_from_uri(params.text_document.uri)
            if workspace_root:
                debug_logger.debug(
                    f"Invalidating model cache for workspace: {workspace_root}"
                )
                server_state.document_cache.invalidate_workspace_models(workspace_root)

    except Exception as e:
        debug_logger.debug(f"Error handling document save: {e}")


def _get_workspace_root_from_uri(uri: str) -> Optional[str]:
    """Extract workspace root from document URI."""
    if not uri.startswith("file://"):
        return None

    file_path = uri.replace("file://", "")

    # Find the workspace root by looking for manage.py
    current_dir = file_path
    while current_dir and current_dir != "/":
        if os.path.exists(os.path.join(current_dir, "manage.py")):
            return current_dir
        current_dir = os.path.dirname(current_dir)

    return None


def _is_likely_django_model_file(uri: str) -> bool:
    """Check if the file is likely a Django model file."""
    if not uri.endswith(".py"):
        return False

    file_path = uri.replace("file://", "")
    file_name = os.path.basename(file_path)

    # Common Django model file patterns
    model_patterns = ["models.py", "models/", "model.py", "django_models.py"]

    # Check if the file name matches any model patterns
    for pattern in model_patterns:
        if pattern in file_name or pattern in file_path:
            return True

    # Check if the file contains Django model imports
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            # Look for common Django model patterns
            django_indicators = [
                "from django.db import models",
                "class Meta:",
                "models.Model",
                "models.CharField",
                "models.IntegerField",
                "models.ForeignKey",
                "models.ManyToManyField",
            ]

            for indicator in django_indicators:
                if indicator in content:
                    return True
    except Exception:
        # If we can't read the file, assume it's not a model file
        pass

    return False


def start_server() -> None:
    """Start the LSP server."""
    lsp_logger.info("Starting Django LSP server...")
    server.start_io()


if __name__ == "__main__":
    start_server()
