"""
Unified logging utilities for Django LSP.

This module provides a single logging system that can work in both modes:
- Console mode: Standard Python logging for development and standalone use
- LSP mode: Integrated with LSP protocol for user-facing notifications

Usage:
    # For console logging (default)
    logger = get_logger("my_component")
    logger.info("This goes to console")

    # For LSP logging (when server is available)
    logger = get_logger("my_component", use_lsp=True)
    logger.info("This goes through LSP to user")

    # Debug logging (always console, never LSP)
    debug_logger = get_debug_logger("my_component")
    debug_logger.debug("This is for developers only")
"""

import logging
import sys
from typing import TYPE_CHECKING, List, Optional

from lsprotocol import types

if TYPE_CHECKING:
    from pygls.server import LanguageServer

from ..config import config


class UnifiedLogger:
    """Unified logger that can work in both console and LSP modes."""

    def __init__(self, name: str, use_lsp: bool = False):
        self.name = name
        self.use_lsp = use_lsp
        self.server: Optional[LanguageServer] = None

        # Console logger as fallback
        self._console_logger = logging.getLogger(f"django-qs-lsp.{name}")
        self._console_logger.setLevel(config.get_user_log_level())

    def set_server(self, server: "LanguageServer") -> None:
        """Set the LSP server instance for LSP mode logging."""
        self.server = server

    def _send_lsp_message(self, message_type: types.MessageType, message: str) -> None:
        """Send message through LSP if available and enabled."""
        if not self.use_lsp or not config.enable_lsp_logging:
            # Fallback to console logging
            self._console_logger.log(self._get_log_level(message_type), message)
            return

        if self.server:
            try:
                self.server.show_message_log(message, message_type)
            except Exception:
                # Fallback to console if LSP fails
                self._console_logger.log(self._get_log_level(message_type), message)
        else:
            # Fallback to console if no server
            self._console_logger.log(self._get_log_level(message_type), message)

    def _get_log_level(self, message_type: types.MessageType) -> int:
        """Convert LSP MessageType to logging level."""
        return {
            types.MessageType.Error: logging.ERROR,
            types.MessageType.Warning: logging.WARNING,
            types.MessageType.Info: logging.INFO,
            types.MessageType.Log: logging.DEBUG,
        }.get(message_type, logging.INFO)

    def info(self, message: str) -> None:
        """Log an info message."""
        if self.use_lsp:
            self._send_lsp_message(types.MessageType.Log, f"[Django LSP] {message}")
        else:
            self._console_logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        if self.use_lsp:
            self._send_lsp_message(types.MessageType.Warning, f"[Django LSP] {message}")
        else:
            self._console_logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        if self.use_lsp:
            self._send_lsp_message(types.MessageType.Error, f"[Django LSP] {message}")
        else:
            self._console_logger.error(message)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        if self.use_lsp:
            self._send_lsp_message(
                types.MessageType.Error, f"[Django LSP] CRITICAL: {message}"
            )
        else:
            self._console_logger.critical(message)

    def important(self, message: str) -> None:
        """Log an important message that should be shown to the user (LSP modal)."""
        if self.use_lsp and self.server and config.enable_lsp_logging:
            try:
                self.server.show_message(
                    f"[Django LSP] {message}", types.MessageType.Info
                )
            except Exception:
                self._console_logger.info(f"[Django LSP] {message}")
        else:
            self._console_logger.info(f"[Django LSP] {message}")


class DebugLogger:
    """Logger for debug information (always console, never LSP)."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(f"django-qs-lsp.debug.{name}")
        self.logger.setLevel(config.get_debug_log_level())

    def debug(self, message: str) -> None:
        """Log debug information."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log debug info level."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log debug warnings."""
        self.logger.warning(message)

    def error(self, message: str, exc_info: Optional[bool] = None) -> None:
        """Log debug errors."""
        self.logger.error(message, exc_info=exc_info)


# Global LSP logger instance for backward compatibility
_lsp_logger = UnifiedLogger("lsp", use_lsp=True)


def setup_logging() -> None:
    """Set up unified logging configuration."""
    # Configure root logger
    root_logger = logging.getLogger("django-qs-lsp")
    root_logger.setLevel(logging.DEBUG)  # Allow all logs to pass through

    # Create formatters
    user_formatter = logging.Formatter("[DJANGO-QS-LSP] %(levelname)s: %(message)s")
    debug_formatter = logging.Formatter(
        "[DJANGO-QS-LSP-DEBUG] %(name)s: %(levelname)s: %(message)s"
    )

    # Create handlers - use stderr to avoid interfering with LSP stdout protocol
    user_handler = logging.StreamHandler(sys.stderr)
    user_handler.setLevel(config.get_user_log_level())
    user_handler.setFormatter(user_formatter)

    debug_handler = logging.StreamHandler(sys.stderr)
    debug_handler.setLevel(config.get_debug_log_level())
    debug_handler.setFormatter(debug_formatter)

    # Add handlers to root logger
    root_logger.addHandler(user_handler)
    root_logger.addHandler(debug_handler)

    # Prevent duplicate logs
    root_logger.propagate = False


def get_logger(name: str, use_lsp: bool = False) -> UnifiedLogger:
    """Get a unified logger for the given name.

    Args:
        name: Logger name
        use_lsp: Whether to use LSP integration (default: False for console mode)
    """
    return UnifiedLogger(name, use_lsp=use_lsp)


def get_debug_logger(name: str) -> DebugLogger:
    """Get a debug logger for the given name (always console mode)."""
    return DebugLogger(name)


# Backward compatibility functions
def get_user_logger(name: str) -> UnifiedLogger:
    """Get a user logger for the given name (console mode)."""
    return UnifiedLogger(name, use_lsp=False)


def get_lsp_logger() -> UnifiedLogger:
    """Get the global LSP logger instance (for backward compatibility)."""
    return _lsp_logger


def set_lsp_server(server: "LanguageServer") -> None:
    """Set the LSP server for the global logger (for backward compatibility)."""
    _lsp_logger.set_server(server)


# Global registry of loggers for server setting
_logger_registry: List[UnifiedLogger] = []


def register_logger(logger: UnifiedLogger) -> None:
    """Register a logger to receive server updates."""
    _logger_registry.append(logger)


def set_server_for_all_loggers(server: "LanguageServer") -> None:
    """Set the server instance for all registered loggers."""
    for logger in _logger_registry:
        logger.set_server(server)
