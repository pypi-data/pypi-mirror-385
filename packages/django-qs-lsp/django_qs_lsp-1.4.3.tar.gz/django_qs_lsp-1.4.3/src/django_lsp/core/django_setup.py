"""
Django environment setup and configuration.

This module handles setting up the Django environment for the LSP,
including finding settings modules and configuring Django.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import django

from ..utils.logging import get_debug_logger, get_logger, register_logger

# Use unified logging system with LSP integration
logger = get_logger("django_setup", use_lsp=True)
debug_logger = get_debug_logger("django_setup")

# Register logger for server updates
register_logger(logger)


class DjangoSetup:
    """Handles Django environment setup and configuration for multiple workspaces."""

    def __init__(self) -> None:
        self.workspace_setups: Dict[str, bool] = {}
        self.settings_modules: Dict[str, str] = {}
        self.project_roots: Dict[str, Path] = {}
        self._global_setup: bool = False
        debug_logger.debug("DjangoSetup initialized")

    def setup(self, workspace_root: str) -> bool:
        """
        Set up Django environment by finding and loading settings.

        Args:
            workspace_root: Path to the workspace root

        Returns:
            True if successful, False otherwise
        """
        # Check if this workspace is already set up
        if self.workspace_setups.get(workspace_root, False):
            logger.info(f"Django already set up for workspace: {workspace_root}")
            return True

        logger.info(f"Setting up Django environment for workspace: {workspace_root}")
        debug_logger.debug(
            f"Current environment DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')}"
        )

        workspace_path = Path(workspace_root)
        debug_logger.debug(f"Workspace path: {workspace_path}")
        debug_logger.debug(f"Workspace path exists: {workspace_path.exists()}")
        debug_logger.debug(f"Workspace path is directory: {workspace_path.is_dir()}")

        # Find manage.py and project root
        project_root = self._find_project_root(workspace_path)
        if not project_root:
            logger.error(
                f"Could not find Django project root in workspace: {workspace_root}"
            )
            debug_logger.error(f"Searched for manage.py in: {workspace_path}")
            if workspace_path.exists():
                debug_logger.error(
                    f"Workspace contents: {list(workspace_path.iterdir())}"
                )
            return False

        self.project_roots[workspace_root] = project_root
        logger.info(f"Found project root at: {project_root}")

        # Add project root to Python path if not already there
        project_root_str = str(project_root)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
            debug_logger.debug(f"Added {project_root} to Python path")

        # Find or set settings module
        settings_module = self._get_settings_module(project_root)
        if not settings_module:
            logger.error(
                f"Failed to determine settings module for project root: {project_root}"
            )
            return False

        self.settings_modules[workspace_root] = settings_module

        # Configure and setup Django
        success = self._configure_django(settings_module, workspace_root)
        if success:
            self.workspace_setups[workspace_root] = True
            self._global_setup = True
            logger.info(f"Django setup successful for workspace: {workspace_root}")
        else:
            logger.error(f"Django setup failed for workspace: {workspace_root}")
            debug_logger.error(f"Settings module: {settings_module}")
            debug_logger.error(f"Project root: {project_root}")

        return success

    def is_setup_for_workspace(self, workspace_root: str) -> bool:
        """Check if Django is set up for a specific workspace."""
        return self.workspace_setups.get(workspace_root, False)

    @property
    def is_setup(self) -> bool:
        """Check if Django is set up for any workspace."""
        return self._global_setup

    def get_project_root(self, workspace_root: str) -> Optional[Path]:
        """Get the project root for a specific workspace."""
        return self.project_roots.get(workspace_root)

    def get_settings_module(self, workspace_root: str) -> Optional[str]:
        """Get the settings module for a specific workspace."""
        return self.settings_modules.get(workspace_root)

    def reset_workspace(self, workspace_root: str) -> None:
        """Reset Django setup for a specific workspace."""
        if workspace_root in self.workspace_setups:
            del self.workspace_setups[workspace_root]
        if workspace_root in self.settings_modules:
            del self.settings_modules[workspace_root]
        if workspace_root in self.project_roots:
            del self.project_roots[workspace_root]

        # Check if any workspaces are still set up
        if not self.workspace_setups:
            self._global_setup = False

        logger.info(f"Reset Django setup for workspace: {workspace_root}")

    def reset(self) -> None:
        """Reset all Django setup state."""
        self.workspace_setups.clear()
        self.settings_modules.clear()
        self.project_roots.clear()
        self._global_setup = False
        logger.info("Reset all Django setup state")

    def __enter__(self) -> "DjangoSetup":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        """Context manager exit - cleanup resources."""
        self.reset()

    def get_workspace_info(self) -> Dict[str, Any]:
        """Get information about all workspaces."""
        return {
            "workspaces": list(self.workspace_setups.keys()),
            "setup_workspaces": [
                ws for ws, setup in self.workspace_setups.items() if setup
            ],
            "settings_modules": self.settings_modules,
            "project_roots": {ws: str(path) for ws, path in self.project_roots.items()},
            "global_setup": self._global_setup,
            "total_workspaces": len(self.workspace_setups),
            "setup_count": sum(1 for setup in self.workspace_setups.values() if setup),
        }

    def configure_django(self, settings_module: str) -> bool:
        """
        Configure and setup Django with the given settings module without requiring a workspace root.

        This is a standalone method for cases where workspace context is not available.
        """
        return self._configure_django(settings_module, "standalone")

    def _find_project_root(self, workspace_path: Path) -> Optional[Path]:
        """
        Find the Django project root using the settings module's BASE_DIR.

        This method uses the Django settings module (from DJANGO_SETTINGS_MODULE)
        to get the authoritative project root via BASE_DIR.
        """
        debug_logger.debug(f"Searching for Django project root in: {workspace_path}")

        # Get settings module from environment
        settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
        if not settings_module:
            logger.warning(
                "DJANGO_SETTINGS_MODULE not set, falling back to manage.py discovery"
            )
            return self._find_project_root_by_manage_py(workspace_path)

        # Try to get project root from Django's BASE_DIR
        project_root = self._get_project_root_from_settings_module(settings_module)
        if project_root:
            debug_logger.debug(
                f"Found project root from Django settings BASE_DIR: {project_root}"
            )
            return project_root

        # Fall back to manage.py discovery
        debug_logger.debug(
            "Could not get BASE_DIR from settings module, falling back to manage.py discovery..."
        )
        return self._find_project_root_by_manage_py(workspace_path)

    def _get_project_root_from_settings_module(
        self, settings_module: str
    ) -> Optional[Path]:
        """
        Get the project root from Django's BASE_DIR by importing the settings module.

        This is the most reliable way to find the project root as it uses
        Django's own canonical reference to its project directory.
        """
        try:
            # Import the settings module
            import importlib

            settings = importlib.import_module(settings_module)

            # Get BASE_DIR from settings
            if hasattr(settings, "BASE_DIR"):
                base_dir: Any = settings.BASE_DIR
                debug_logger.debug(f"Found BASE_DIR in settings: {base_dir}")

                # Convert to Path if it's a string
                if isinstance(base_dir, str):
                    base_dir_path = Path(base_dir)
                elif isinstance(base_dir, Path):
                    base_dir_path = base_dir
                else:
                    debug_logger.warning(
                        f"BASE_DIR is not a string or Path: {type(base_dir)}"
                    )
                    return None

                # Validate that the BASE_DIR contains manage.py
                manage_py_path = base_dir_path / "manage.py"
                if manage_py_path.exists():
                    debug_logger.debug(
                        f"Validated BASE_DIR contains manage.py: {base_dir_path}"
                    )
                    return base_dir_path
                else:
                    debug_logger.warning(
                        f"BASE_DIR {base_dir_path} does not contain manage.py"
                    )
                    return None
            else:
                debug_logger.warning(
                    f"Settings module {settings_module} does not have BASE_DIR"
                )
                return None

        except ImportError as e:
            debug_logger.debug(
                f"Could not import settings module {settings_module}: {e}"
            )
            return None
        except Exception as e:
            debug_logger.debug(
                f"Error getting BASE_DIR from settings module {settings_module}: {e}"
            )
            return None

    def _find_project_root_by_manage_py(self, workspace_path: Path) -> Optional[Path]:
        """
        Find the Django project root by searching for manage.py files.

        This is the fallback method when Django settings are not available.
        """
        # Look for manage.py in workspace root
        manage_py = workspace_path / "manage.py"
        debug_logger.debug(f"Checking for manage.py at: {manage_py}")
        if manage_py.exists():
            debug_logger.debug(f"Found manage.py at workspace root: {manage_py}")
            return manage_py.parent

        # Try to find manage.py in subdirectories
        debug_logger.debug("Searching subdirectories for manage.py...")
        subdirs_checked = []
        for subdir in workspace_path.iterdir():
            if subdir.is_dir():
                subdirs_checked.append(subdir.name)
                potential_manage = subdir / "manage.py"
                debug_logger.debug(
                    f"Checking subdirectory {subdir.name}: {potential_manage}"
                )
                if potential_manage.exists():
                    debug_logger.debug(f"Found manage.py in subdirectory: {subdir}")
                    return potential_manage.parent

        logger.error(f"No manage.py found in workspace: {workspace_path}")
        debug_logger.error(f"Checked subdirectories: {subdirs_checked}")
        logger.error(
            "Make sure you're running the LSP from a Django project directory or set DJANGO_SETTINGS_MODULE manually"
        )
        return None

    def _get_settings_module(self, project_root: Path) -> Optional[str]:
        """Get the Django settings module from environment variable or LSP initialization parameters."""
        # Try to get from environment first
        settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
        if settings_module:
            debug_logger.debug(
                f"Using DJANGO_SETTINGS_MODULE from environment: {settings_module}"
            )
            return settings_module

        logger.error(
            "DJANGO_SETTINGS_MODULE environment variable must be set for the LSP to work."
        )
        logger.error(
            "Please set DJANGO_SETTINGS_MODULE to your Django project's settings module (e.g., 'myproject.settings')"
        )
        logger.error(
            "You can set this in your shell or in your editor's LSP configuration"
        )
        return None

    def _configure_django(self, settings_module: str, workspace_context: str) -> bool:
        """
        Configure and setup Django with the given settings module.

        Args:
            settings_module: The Django settings module to use
            workspace_context: Context for error reporting (workspace path or "standalone")
        """
        try:
            # Configure Django settings
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

            # Try to setup Django
            django.setup()
            logger.info(f"Django setup successful with settings: {settings_module}")
            debug_logger.debug(f"Django setup context: {workspace_context}")
            return True

        except ModuleNotFoundError as e:
            logger.error(f"Missing dependency for Django setup: {e!s}")
            logger.error(
                "The LSP server needs access to your Django project's dependencies"
            )
            logger.error("Solutions:")
            logger.error(
                "1. Run the LSP server from your Django project's virtual environment"
            )
            logger.error(
                "2. Install your project's dependencies in the LSP server's environment"
            )
            logger.error(
                "3. Use a tool like 'pipenv run' or 'poetry run' to run the LSP server"
            )
            debug_logger.error(
                f"ModuleNotFoundError context: {workspace_context}, settings: {settings_module}"
            )
            return False

        except ImportError as e:
            logger.error(f"Settings module '{settings_module}' import error: {e!s}")
            logger.error(
                "Please check that DJANGO_SETTINGS_MODULE points to a valid settings module"
            )
            debug_logger.error(
                f"ImportError context: {workspace_context}, settings: {settings_module}"
            )
            return False

        except Exception as e:
            logger.error(f"Failed to setup Django environment: {e!s}")
            logger.error(
                "This might be due to missing dependencies or configuration issues"
            )
            debug_logger.error(
                f"Unexpected error context: {workspace_context}, settings: {settings_module}, error: {e}"
            )
            return False
