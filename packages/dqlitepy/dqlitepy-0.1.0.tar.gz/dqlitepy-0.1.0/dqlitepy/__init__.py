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

"""Python bindings for dqlite."""

from ._ffi import get_version
from .client import Client, NodeInfo
from . import dbapi
from .exceptions import (
    ClientClosedError,
    ClientConnectionError,
    ClientError,
    ClusterConfigurationError,
    ClusterError,
    ClusterJoinError,
    ClusterQuorumLostError,
    DqliteError,
    DqliteLibraryNotFound,
    ErrorCode,
    ErrorSeverity,
    MemoryError,
    NoLeaderError,
    NodeAlreadyRunningError,
    NodeAssertionError,
    NodeError,
    NodeNotRunningError,
    NodeShutdownError,
    NodeStartError,
    NodeStopError,
    ResourceError,
    ResourceLeakWarning,
    SafeErrorHandler,
    SegmentationFault,
    ShutdownSafetyGuard,
    handle_c_errors,
    safe_cleanup,
    safe_operation,
)
from .node import Node

__version__ = "0.2.0"

__all__ = [
    # Core classes
    "Node",
    "Client",
    "NodeInfo",
    # DB-API 2.0 module
    "dbapi",
    # Exceptions - Base
    "DqliteError",
    "DqliteLibraryNotFound",
    # Exceptions - Node
    "NodeError",
    "NodeStartError",
    "NodeStopError",
    "NodeAlreadyRunningError",
    "NodeNotRunningError",
    "NodeShutdownError",
    "NodeAssertionError",
    # Exceptions - Client
    "ClientError",
    "ClientConnectionError",
    "ClientClosedError",
    "NoLeaderError",
    # Exceptions - Cluster
    "ClusterError",
    "ClusterJoinError",
    "ClusterConfigurationError",
    "ClusterQuorumLostError",
    # Exceptions - Resources
    "ResourceError",
    "ResourceLeakWarning",
    "MemoryError",
    # Exceptions - Signals
    "SegmentationFault",
    # Error handling utilities
    "SafeErrorHandler",
    "safe_operation",
    "safe_cleanup",
    "handle_c_errors",
    "ShutdownSafetyGuard",
    # Enums
    "ErrorCode",
    "ErrorSeverity",
    # Utilities
    "get_version",
    "__version__",
]
