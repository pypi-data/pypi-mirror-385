"""
Configuration settings for Django LSP.
"""

import logging
import os
from contextlib import suppress


class DjangoLSPConfig:
    """Configuration class for Django LSP settings."""

    def __init__(self) -> None:
        # Default settings
        self._max_lookup_depth = 5
        self._debug_mode = False
        self._log_level = "INFO"  # Default log level for user-relevant logs
        self._debug_log_level = "DEBUG"  # Default debug log level
        self._enable_lsp_logging = True  # Default to LSP logging enabled

    @property
    def max_lookup_depth(self) -> int:
        """Maximum depth for nested relationship traversal."""
        return self._max_lookup_depth

    @max_lookup_depth.setter
    def max_lookup_depth(self, value: int) -> None:
        """Set the maximum lookup depth."""
        if not isinstance(value, int) or value < 1:
            raise ValueError("max_lookup_depth must be a positive integer")
        self._max_lookup_depth = value

    @property
    def debug_mode(self) -> bool:
        """Whether debug logging is enabled."""
        return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        """Set debug mode."""
        self._debug_mode = bool(value)

    @property
    def log_level(self) -> str:
        """Log level for user-relevant logs."""
        return self._log_level

    @log_level.setter
    def log_level(self, value: str) -> None:
        """Set log level for user-relevant logs."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        self._log_level = value.upper()

    @property
    def debug_log_level(self) -> str:
        """Log level for debug logs."""
        return self._debug_log_level

    @debug_log_level.setter
    def debug_log_level(self, value: str) -> None:
        """Set log level for debug logs."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value.upper() not in valid_levels:
            raise ValueError(f"debug_log_level must be one of {valid_levels}")
        self._debug_log_level = value.upper()

    def get_user_log_level(self) -> int:
        """Get the numeric log level for user-relevant logs."""
        return int(getattr(logging, self.log_level))

    def get_debug_log_level(self) -> int:
        """Get the numeric log level for debug logs."""
        if self.debug_mode:
            return int(getattr(logging, self.debug_log_level))
        else:
            return int(logging.WARNING)  # Suppress debug logs when debug mode is off

    @property
    def enable_lsp_logging(self) -> bool:
        """Whether LSP logging is enabled."""
        return self._enable_lsp_logging

    @enable_lsp_logging.setter
    def enable_lsp_logging(self, value: bool) -> None:
        """Set LSP logging enabled."""
        self._enable_lsp_logging = bool(value)

    def load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        depth = os.getenv("DJANGO_LSP_MAX_DEPTH")
        if depth:
            with suppress(ValueError):
                self.max_lookup_depth = int(depth)

        debug = os.getenv("DJANGO_QS_LSP_DEBUG")
        if debug:
            self.debug_mode = debug.lower() == "true"

        log_level = os.getenv("DJANGO_LSP_LOG_LEVEL")
        if log_level:
            self.log_level = log_level

        debug_log_level = os.getenv("DJANGO_LSP_DEBUG_LOG_LEVEL")
        if debug_log_level:
            self.debug_log_level = debug_log_level

        lsp_logging = os.getenv("DJANGO_LSP_ENABLE_LSP_LOGGING")
        if lsp_logging:
            self.enable_lsp_logging = lsp_logging.lower() == "true"

    def update_from_environment(self) -> None:
        """Update configuration from environment variables (useful after env changes)."""
        self.load_from_environment()


# Global configuration instance
config = DjangoLSPConfig()
# Load environment variables on import
config.load_from_environment()
