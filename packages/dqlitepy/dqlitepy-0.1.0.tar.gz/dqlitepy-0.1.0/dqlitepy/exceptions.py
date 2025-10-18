# Copyright 2025 Vantage Compute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Comprehensive exception hierarchy for dqlitepy.

This module provides a rich exception hierarchy to handle various error conditions
that can occur when working with dqlite, including segfaults, assertion failures,
and resource cleanup issues.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from enum import Enum
from typing import Any, Callable, Generator, Optional, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generic error handling decorators
T = TypeVar("T")


class ErrorCode(Enum):
    """Common dqlite error codes and their meanings."""

    SUCCESS = 0
    NOMEM = 1  # Out of memory
    INVALID = 2  # Invalid parameter
    NOTFOUND = 3  # Node not found
    MISUSE = 4  # Library misused
    NOLEADER = 5  # No leader available
    SHUTDOWN = 6  # Node is shutting down
    STOPPED = 7  # Node is stopped
    INTERNAL = 8  # Internal error
    UNKNOWN = -1  # Unknown error

    @classmethod
    def from_code(cls, code: int) -> "ErrorCode":
        """Get ErrorCode from integer code."""
        try:
            return cls(code)
        except ValueError:
            return cls.UNKNOWN


class ErrorSeverity(Enum):
    """Severity levels for dqlite errors."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"  # Unrecoverable, requires process restart


# ============================================================================
# Base Exception Classes
# ============================================================================


class DqliteError(RuntimeError):
    """Base exception for all dqlite errors.

    This is the base class for all dqlite-related exceptions. It provides
    context about the operation that failed and supports error recovery.
    """

    severity: ErrorSeverity = ErrorSeverity.ERROR
    recoverable: bool = True

    def __init__(
        self,
        code: int,
        context: str,
        message: Optional[str] = None,
        cause: Optional[BaseException] = None,
    ) -> None:
        self.code = code
        self.error_code = ErrorCode.from_code(code)
        self.context = context
        self.message = message
        self.cause = cause

        details = f"{context} failed with code {code} ({self.error_code.name})"
        if message:
            details = f"{details}: {message}"
        if cause:
            details = f"{details}\nCaused by: {cause}"

        super().__init__(details)
        logger.log(self._severity_to_log_level(), details, exc_info=cause is not None)

    def _severity_to_log_level(self) -> int:
        """Convert severity to logging level."""
        mapping = {
            ErrorSeverity.DEBUG: logging.DEBUG,
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.FATAL: logging.CRITICAL,
        }
        return mapping.get(self.severity, logging.ERROR)


class DqliteLibraryNotFound(DqliteError):
    """Raised when libdqlitepy cannot be located on the system."""

    severity = ErrorSeverity.FATAL
    recoverable = False

    def __init__(self, attempts: list[tuple[str, str]]) -> None:
        message_lines = ["Unable to locate libdqlitepy. Tried the following paths:"]
        for path, reason in attempts:
            if reason:
                message_lines.append(f"  - {path} ({reason})")
            else:
                message_lines.append(f"  - {path}")
        super().__init__(-1, "dlopen", "\n".join(message_lines))
        self.attempts = attempts


# ============================================================================
# Node-specific Exceptions
# ============================================================================


class NodeError(DqliteError):
    """Base exception for node-related errors.

    Raised when operations on a dqlite Node fail, such as starting,
    stopping, or communicating with the node.

    Attributes:
        node_id: Unique identifier of the node (if known).
        node_address: Network address of the node (if known).

    Example:
        >>> try:
        ...     node.start()
        ... except NodeError as e:
        ...     print(f"Node {e.node_id} failed: {e}")
    """

    def __init__(
        self,
        code: int,
        context: str,
        message: Optional[str] = None,
        node_id: Optional[int] = None,
        node_address: Optional[str] = None,
    ) -> None:
        self.node_id = node_id
        self.node_address = node_address
        details = message or ""
        if node_id is not None:
            details = f"Node {node_id}: {details}" if details else f"Node {node_id}"
        if node_address:
            details = f"{details} ({node_address})" if details else node_address
        super().__init__(code, context, details)


class NodeStartError(NodeError):
    """Raised when a node fails to start.

    This can occur due to:
    - Port already in use
    - Invalid data directory
    - Corrupted database files
    - Permission issues

    Example:
        >>> try:
        ...     node = Node("127.0.0.1:9001", "/data")
        ...     node.start()
        ... except NodeStartError as e:
        ...     print(f"Failed to start node: {e}")
        ...     # Check port availability, permissions, etc.
    """

    severity = ErrorSeverity.ERROR


class NodeStopError(NodeError):
    """Raised when a node fails to stop cleanly.

    This exception is marked as WARNING severity because stop failures
    are often not critical - the process may be exiting anyway.
    """

    severity = ErrorSeverity.WARNING
    recoverable = True  # Can continue with forceful cleanup


class NodeAlreadyRunningError(NodeError):
    """Raised when attempting to start an already-running node."""

    severity = ErrorSeverity.WARNING


class NodeNotRunningError(NodeError):
    """Raised when attempting to stop a node that's not running."""

    severity = ErrorSeverity.INFO


class NodeShutdownError(NodeError):
    """Raised during graceful shutdown when cleanup fails.

    This is expected during shutdown and should be handled gracefully.
    """

    severity = ErrorSeverity.WARNING
    recoverable = True


class NodeAssertionError(NodeError):
    """Raised when the underlying C library hits an assertion failure.

    This indicates a bug in dqlite or incorrect usage. These are typically
    not recoverable and may require process restart.
    """

    severity = ErrorSeverity.FATAL
    recoverable = False


# ============================================================================
# Client-specific Exceptions
# ============================================================================


class ClientError(DqliteError):
    """Base exception for client-related errors.

    Raised when Client operations fail, such as connecting to the cluster,
    adding nodes, or querying cluster state.

    Example:
        >>> try:
        ...     client = Client(["127.0.0.1:9001", "127.0.0.1:9002"])
        ...     leader = client.leader()
        ... except ClientError as e:
        ...     print(f"Client operation failed: {e}")
    """

    pass


class ClientConnectionError(ClientError):
    """Raised when unable to connect to the cluster."""

    severity = ErrorSeverity.CRITICAL


class ClientClosedError(ClientError):
    """Raised when attempting to use a closed client."""

    severity = ErrorSeverity.ERROR


class NoLeaderError(ClientError):
    """Raised when the cluster has no elected leader.

    This can happen temporarily during:
    - Leader election after a node failure
    - Network partitions
    - Cluster startup before quorum is achieved

    Operations should be retried after a brief delay (typically 1-5 seconds).

    Example:
        >>> import time
        >>> from dqlitepy.exceptions import NoLeaderError
        >>>
        >>> max_retries = 5
        >>> for attempt in range(max_retries):
        ...     try:
        ...         leader = client.leader()
        ...         break
        ...     except NoLeaderError:
        ...         if attempt < max_retries - 1:
        ...             time.sleep(1)
        ...         else:
        ...             raise
    """

    severity = ErrorSeverity.WARNING
    recoverable = True  # Can retry after election


# ============================================================================
# Cluster-specific Exceptions
# ============================================================================


class ClusterError(DqliteError):
    """Base exception for cluster management errors."""

    pass


class ClusterJoinError(ClusterError):
    """Raised when a node fails to join the cluster."""

    severity = ErrorSeverity.CRITICAL


class ClusterConfigurationError(ClusterError):
    """Raised when cluster configuration is invalid."""

    severity = ErrorSeverity.ERROR


class ClusterQuorumLostError(ClusterError):
    """Raised when the cluster loses quorum.

    This is critical but may be recoverable if nodes come back online.
    """

    severity = ErrorSeverity.CRITICAL
    recoverable = True


# ============================================================================
# Resource Management Exceptions
# ============================================================================


class ResourceError(DqliteError):
    """Base exception for resource management errors."""

    pass


class ResourceLeakWarning(ResourceError, Warning):
    """Warning raised when resources may not have been properly released."""

    severity = ErrorSeverity.WARNING

    def __init__(self, resource_type: str, details: str) -> None:
        super().__init__(
            -1,
            "resource_cleanup",
            f"Potential {resource_type} leak: {details}",
        )


class MemoryError(ResourceError):
    """Raised when memory allocation fails."""

    severity = ErrorSeverity.CRITICAL


# ============================================================================
# Signal Handling Exceptions
# ============================================================================


class SegmentationFault(DqliteError):
    """Raised when a segmentation fault is detected.

    This is a fatal error that indicates memory corruption or undefined
    behavior in the C library.
    """

    severity = ErrorSeverity.FATAL
    recoverable = False

    def __init__(self, context: str, signal_info: Optional[str] = None) -> None:
        message = "Segmentation fault detected"
        if signal_info:
            message = f"{message}: {signal_info}"
        super().__init__(-11, context, message)


# ============================================================================
# Error Handler Utilities
# ============================================================================


class SafeErrorHandler:
    """Context manager for safe error handling with cleanup guarantees."""

    def __init__(
        self,
        context: str,
        cleanup_fn: Optional[Callable[[], None]] = None,
        suppress_errors: bool = False,
    ) -> None:
        self.context = context
        self.cleanup_fn = cleanup_fn
        self.suppress_errors = suppress_errors
        self.error: Optional[BaseException] = None

    def __enter__(self) -> "SafeErrorHandler":
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> bool:
        # Always run cleanup, even if there was an error
        if self.cleanup_fn:
            try:
                self.cleanup_fn()
            except Exception as cleanup_error:
                logger.warning(
                    f"Cleanup failed in {self.context}: {cleanup_error}",
                    exc_info=True,
                )
                # If we already had an error, log cleanup failure but don't replace it
                if exc_val is None:
                    self.error = cleanup_error

        # Store the original error
        if exc_val is not None:
            self.error = exc_val

        # Suppress errors if requested
        return self.suppress_errors


@contextmanager
def safe_operation(
    context: str,
    suppress_errors: bool = False,
    default_return: Any = None,
) -> Generator[None, None, None]:
    """Context manager for wrapping risky operations with error handling.

    Args:
        context: Description of the operation for error messages
        suppress_errors: Whether to suppress exceptions (returns default_return)
        default_return: Value to return if errors are suppressed

    Example:
        >>> with safe_operation("node_cleanup", suppress_errors=True):
        ...     node.stop()  # Won't raise even if it fails
    """
    try:
        yield
    except Exception as exc:
        logger.error(f"Error in {context}: {exc}", exc_info=True)
        if not suppress_errors:
            # Re-wrap in DqliteError if not already
            if isinstance(exc, DqliteError):
                raise
            raise DqliteError(-1, context, str(exc), cause=exc) from exc


def safe_cleanup(fn: Callable[[], T], context: str, default: T = None) -> T:
    """Execute a cleanup function safely, logging but not propagating errors.

    Args:
        fn: Cleanup function to call
        context: Description for error messages
        default: Value to return if cleanup fails

    Returns:
        Result of fn() or default if it fails

    Example:
        >>> safe_cleanup(lambda: node.stop(), "node_stop")
    """
    try:
        return fn()
    except Exception as exc:
        logger.warning(
            f"Cleanup operation '{context}' failed: {exc}",
            exc_info=True,
        )
        return default


def handle_c_errors(lib: Any, rc: int, context: str, **kwargs: Any) -> None:
    """Handle error codes from C library calls.

    This centralizes error handling and exception raising based on return codes.

    Args:
        lib: The FFI library handle
        rc: Return code from C function
        context: Description of the operation
        **kwargs: Additional context (node_id, node_address, etc.)

    Raises:
        Appropriate DqliteError subclass based on error code and context
    """
    if rc == 0:
        return  # Success

    # Import here to avoid circular dependency
    from ._ffi import ffi, string_from_c

    # Get error message from library
    message_ptr = lib.dqlitepy_last_error()
    message: Optional[str] = None
    if message_ptr not in (None, ffi.NULL):
        try:
            message = string_from_c(message_ptr)
        finally:
            lib.dqlitepy_free(message_ptr)

    error_code = ErrorCode.from_code(rc)

    # Determine appropriate exception class based on context and error code
    if "node" in context.lower():
        if "start" in context.lower():
            raise NodeStartError(rc, context, message, **kwargs)
        elif "stop" in context.lower() or "shutdown" in context.lower():
            raise NodeStopError(rc, context, message, **kwargs)
        elif "assertion" in (message or "").lower():
            raise NodeAssertionError(rc, context, message, **kwargs)
        else:
            raise NodeError(rc, context, message, **kwargs)

    elif "client" in context.lower():
        if error_code == ErrorCode.NOLEADER:
            raise NoLeaderError(rc, context, message)
        elif "connect" in context.lower() or "create" in context.lower():
            raise ClientConnectionError(rc, context, message)
        else:
            raise ClientError(rc, context, message)

    elif "cluster" in context.lower():
        if "join" in context.lower():
            raise ClusterJoinError(rc, context, message)
        elif "quorum" in (message or "").lower():
            raise ClusterQuorumLostError(rc, context, message)
        else:
            raise ClusterError(rc, context, message)

    elif error_code == ErrorCode.NOMEM:
        raise MemoryError(rc, context, message)

    else:
        # Generic fallback
        raise DqliteError(rc, context, message)


# ============================================================================
# Shutdown Safety Utilities
# ============================================================================


class ShutdownSafetyGuard:
    """Guard to ensure safe shutdown even with C library issues.

    This class wraps shutdown operations to handle known issues like
    assertion failures in dqlite_node_stop.
    """

    def __init__(self, resource_name: str) -> None:
        self.resource_name = resource_name
        self.shutdown_attempted = False
        self.shutdown_succeeded = False

    def attempt_shutdown(self, shutdown_fn: Callable[[], None]) -> bool:
        """Attempt shutdown with error recovery.

        Args:
            shutdown_fn: Function to call for shutdown

        Returns:
            True if shutdown succeeded, False otherwise
        """
        self.shutdown_attempted = True

        try:
            with safe_operation(
                f"{self.resource_name}_shutdown", suppress_errors=False
            ):
                shutdown_fn()
            self.shutdown_succeeded = True
            return True

        except NodeStopError as exc:
            # Known shutdown issue - log but don't fail
            logger.warning(
                f"Shutdown of {self.resource_name} encountered known issue: {exc}. "
                "This is a known dqlite assertion failure and can be safely ignored."
            )
            # Consider it a partial success
            self.shutdown_succeeded = True
            return True

        except DqliteError as exc:
            if not exc.recoverable:
                logger.error(f"Fatal error during {self.resource_name} shutdown: {exc}")
                raise
            logger.warning(
                f"Recoverable error during {self.resource_name} shutdown: {exc}"
            )
            return False

        except Exception as exc:
            logger.error(
                f"Unexpected error during {self.resource_name} shutdown: {exc}",
                exc_info=True,
            )
            return False

    def force_cleanup(self, cleanup_fn: Callable[[], None]) -> None:
        """Force cleanup regardless of shutdown state.

        This should be called if normal shutdown fails.

        Args:
            cleanup_fn: Function to call for cleanup
        """
        if self.shutdown_succeeded:
            return  # Already cleaned up

        logger.info(f"Forcing cleanup of {self.resource_name}")
        safe_cleanup(cleanup_fn, f"{self.resource_name}_force_cleanup")


__all__ = [
    # Enums
    "ErrorCode",
    "ErrorSeverity",
    # Base exceptions
    "DqliteError",
    "DqliteLibraryNotFound",
    # Node exceptions
    "NodeError",
    "NodeStartError",
    "NodeStopError",
    "NodeAlreadyRunningError",
    "NodeNotRunningError",
    "NodeShutdownError",
    "NodeAssertionError",
    # Client exceptions
    "ClientError",
    "ClientConnectionError",
    "ClientClosedError",
    "NoLeaderError",
    # Cluster exceptions
    "ClusterError",
    "ClusterJoinError",
    "ClusterConfigurationError",
    "ClusterQuorumLostError",
    # Resource exceptions
    "ResourceError",
    "ResourceLeakWarning",
    "MemoryError",
    # Signal exceptions
    "SegmentationFault",
    # Utilities
    "SafeErrorHandler",
    "safe_operation",
    "safe_cleanup",
    "handle_c_errors",
    "ShutdownSafetyGuard",
]
