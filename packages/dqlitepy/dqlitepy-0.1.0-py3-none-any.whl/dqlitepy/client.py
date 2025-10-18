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

"""Dqlite cluster client for managing nodes and executing queries."""

from __future__ import annotations

import json
import logging
import threading
import weakref
from types import TracebackType
from typing import Any, List, Optional, Type

from ._ffi import ffi, get_library, string_from_c
from .exceptions import (
    ClientClosedError,
    ClientError,
    handle_c_errors,
    safe_cleanup,
    safe_operation,
)

__all__ = ["Client", "NodeInfo"]

logger = logging.getLogger(__name__)


class NodeInfo:
    """Information about a node in the dqlite cluster."""

    def __init__(self, id: int, address: str, role: int):
        self.id = id
        self.address = address
        self.role = role  # 0=Voter, 1=StandBy, 2=Spare

    @property
    def role_name(self) -> str:
        """Get the human-readable role name."""
        return {0: "Voter", 1: "StandBy", 2: "Spare"}.get(self.role, "Unknown")

    def __repr__(self) -> str:
        return (
            f"NodeInfo(id={self.id}, address='{self.address}', role={self.role_name})"
        )


def _destroy_client(lib: Any, handle: int) -> None:  # pragma: no cover
    """Best effort cleanup of client handle.

    This is called by the weakref finalizer and should never raise.
    """
    if handle:
        safe_cleanup(
            lambda: lib.dqlitepy_client_close(handle),
            f"client_finalizer_{handle}",
        )


def _raise_client_error(lib: Any, rc: int, context: str) -> None:
    """Raise appropriate exception for client errors.

    Args:
        lib: FFI library handle
        rc: Return code from C function
        context: Operation context
    """
    message_ptr = lib.dqlitepy_last_error()
    if message_ptr not in (None, ffi.NULL):
        try:
            # Free the message pointer - error handling is centralized
            pass
        finally:
            lib.dqlitepy_free(message_ptr)

    # Use centralized error handling
    handle_c_errors(lib, rc, context)


class Client:
    """Client for connecting to and managing a dqlite cluster.

    The client connects to a cluster of dqlite nodes and provides methods
    for cluster management (adding/removing nodes) and querying the cluster state.

    Example:
        >>> from dqlitepy import Client
        >>> client = Client(["127.0.0.1:9001", "127.0.0.1:9002"])
        >>> leader = client.leader()
        >>> print(f"Current leader: {leader}")
        >>> client.add(3, "127.0.0.1:9003")
        >>> nodes = client.cluster()
        >>> for node in nodes:
        ...     print(f"Node {node.id}: {node.address} ({node.role_name})")
    """

    def __init__(self, cluster: List[str]):
        """Connect to a dqlite cluster.

        Args:
            cluster: List of node addresses in format ["host:port", ...]
                    The client will connect to the leader node.

        Raises:
            DqliteError: If unable to connect to the cluster.
        """
        self._lib = get_library()
        self._lock = threading.RLock()
        self._cluster = cluster
        self._handle = 0

        # Join cluster addresses with commas for the C API
        addresses_csv = ",".join(cluster).encode("utf-8")

        handle_p = ffi.new("dqlitepy_handle *")
        rc = self._lib.dqlitepy_client_create(addresses_csv, handle_p)
        if rc != 0:
            _raise_client_error(self._lib, rc, "dqlitepy_client_create")

        self._handle = int(handle_p[0])
        self._finalizer = weakref.finalize(
            self, _destroy_client, self._lib, self._handle
        )
        logger.info(f"Client connected to cluster: {cluster}")

    @property
    def cluster_addresses(self) -> List[str]:
        """Get the list of cluster addresses this client knows about."""
        return self._cluster.copy()

    def leader(self) -> str:
        """Get the address of the current cluster leader.

        Returns:
            The address of the leader node (e.g., "127.0.0.1:9001")

        Raises:
            ClientClosedError: If client is closed
            ClientError: If unable to determine the leader.
        """
        with self._lock:
            if not self._handle:
                raise ClientClosedError(-1, "client_leader", "Client is closed")

            address_p = ffi.new("char **")
            rc = self._lib.dqlitepy_client_leader(self._handle, address_p)
            if rc != 0:
                _raise_client_error(self._lib, rc, "dqlitepy_client_leader")

            try:
                address_str = string_from_c(address_p[0])
                if address_str is None:
                    raise ClientError(
                        -1, "client_leader", "Failed to get leader address"
                    )
                return address_str
            finally:
                self._lib.dqlitepy_free(address_p[0])

    def add(self, node_id: int, address: str) -> None:
        """Add a node to the cluster.

        The node must already be running (via Node class) before adding it to the cluster.

        Args:
            node_id: Unique identifier for the node
            address: Network address of the node (e.g., "127.0.0.1:9002")

        Raises:
            ClientClosedError: If client is closed
            ClientError: If unable to add the node.

        Example:
            >>> from dqlitepy import Node, Client
            >>> node2 = Node("127.0.0.1:9002", "/data/node2", node_id=2)
            >>> node2.start()
            >>> client = Client(["127.0.0.1:9001"])
            >>> client.add(2, "127.0.0.1:9002")
        """
        with self._lock:
            if not self._handle:
                raise ClientClosedError(-1, "client_add", "Client is closed")

            encoded_address = address.encode("utf-8")
            rc = self._lib.dqlitepy_client_add(self._handle, node_id, encoded_address)
            if rc != 0:
                _raise_client_error(self._lib, rc, "dqlitepy_client_add")
            logger.info(f"Added node {node_id} at {address} to cluster")

    def remove(self, node_id: int) -> None:
        """Remove a node from the cluster.

        Args:
            node_id: Unique identifier of the node to remove

        Raises:
            ClientClosedError: If client is closed
            ClientError: If unable to remove the node.

        Note:
            You cannot remove the leader node. Transfer leadership first or
            let the cluster elect a new leader.
        """
        with self._lock:
            if not self._handle:
                raise ClientClosedError(-1, "client_remove", "Client is closed")

            rc = self._lib.dqlitepy_client_remove(self._handle, node_id)
            if rc != 0:
                _raise_client_error(self._lib, rc, "dqlitepy_client_remove")
            logger.info(f"Removed node {node_id} from cluster")

    def cluster(self) -> List[NodeInfo]:
        """Get information about all nodes in the cluster.

        Returns:
            List of NodeInfo objects describing each node in the cluster.

        Raises:
            ClientClosedError: If client is closed
            ClientError: If unable to query cluster information.

        Example:
            >>> client = Client(["127.0.0.1:9001"])
            >>> nodes = client.cluster()
            >>> for node in nodes:
            ...     print(f"Node {node.id}: {node.address} - {node.role_name}")
            Node 1: 127.0.0.1:9001 - Voter
            Node 2: 127.0.0.1:9002 - Voter
        """
        with self._lock:
            if not self._handle:
                raise ClientClosedError(-1, "client_cluster", "Client is closed")

            json_p = ffi.new("char **")
            rc = self._lib.dqlitepy_client_cluster(self._handle, json_p)
            if rc != 0:
                _raise_client_error(self._lib, rc, "dqlitepy_client_cluster")

            try:
                json_str = string_from_c(json_p[0])
                if json_str is None:
                    raise ClientError(
                        -1, "client_cluster", "Failed to get cluster info"
                    )
                data = json.loads(json_str)
                return [
                    NodeInfo(node["id"], node["address"], node["role"]) for node in data
                ]
            finally:
                self._lib.dqlitepy_free(json_p[0])

    def close(self) -> None:
        """Close the client connection with safe cleanup.

        After calling this method, the client cannot be used anymore.
        This is called automatically when the client is garbage collected.
        """
        with self._lock:
            if self._finalizer.alive:
                with safe_operation("client_finalizer", suppress_errors=True):
                    self._finalizer()
            self._handle = 0
            logger.debug("Client closed")

    def __enter__(self) -> "Client":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Context manager exit with safe cleanup."""
        with safe_operation("client_close_on_exit", suppress_errors=True):
            self.close()

    def __del__(self) -> None:  # pragma: no cover
        """Destructor - best effort cleanup that never raises."""
        try:
            with safe_operation("client_destructor", suppress_errors=True):
                self.close()
        except Exception:
            # Absolutely never let destructor raise
            pass

    def __repr__(self) -> str:
        """String representation."""
        status = "open" if self._handle else "closed"
        return f"Client(cluster={self._cluster}, status={status})"
