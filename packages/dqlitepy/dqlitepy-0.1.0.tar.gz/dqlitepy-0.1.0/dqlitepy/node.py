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

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from types import TracebackType
from typing import Any, Optional, Type

from ._ffi import ffi, get_library, make_string, string_from_c
from .exceptions import (
    NodeAlreadyRunningError,
    NodeNotRunningError,
    ShutdownSafetyGuard,
    handle_c_errors,
    safe_cleanup,
    safe_operation,
)

__all__ = ["Node"]

logger = logging.getLogger(__name__)

# Environment variable to bypass dqlite_node_stop (works around segfault bug)
_BYPASS_NODE_STOP = os.getenv("DQLITEPY_BYPASS_STOP", "").lower() in (
    "1",
    "true",
    "yes",
)


def _destroy_node(
    lib: Any, handle: int
) -> None:  # pragma: no cover - best effort cleanup
    """Best-effort cleanup of node handle.

    This is called by the weakref finalizer and should never raise.
    """
    if handle:
        safe_cleanup(
            lambda: lib.dqlitepy_node_destroy(handle),
            f"node_finalizer_{handle}",
        )


def _raise_node_error(lib: Any, rc: int, context: str, **kwargs: Any) -> None:
    """Raise appropriate exception for node errors.

    Args:
        lib: FFI library handle
        rc: Return code from C function
        context: Operation context
        **kwargs: Additional context (node_id, node_address)
    """
    message_ptr = lib.dqlitepy_last_error()
    if message_ptr not in (None, ffi.NULL):
        try:
            # Free the message pointer - error handling is centralized
            pass
        finally:
            lib.dqlitepy_free(message_ptr)

    # Use centralized error handling
    handle_c_errors(lib, rc, context, **kwargs)


class Node:
    """A dqlite node that participates in a distributed SQLite cluster.

    The Node class provides a Pythonic interface to the dqlite C library,
    enabling you to create distributed, fault-tolerant SQLite databases with
    Raft consensus. Each node can act as a standalone database or join a
    cluster for high availability and automatic replication.

    The node manages:
    - Raft consensus protocol for leader election
    - SQLite database operations with cluster-wide replication
    - Automatic failover and data consistency
    - Network communication with other cluster members

    Example:
        >>> # Single node
        >>> node = Node("127.0.0.1:9001", "/tmp/dqlite-data")
        >>> node.start()
        >>> node.open_db("myapp.db")
        >>> node.exec("CREATE TABLE users (id INTEGER, name TEXT)")
        >>>
        >>> # Cluster node
        >>> node = Node(
        ...     address="172.20.0.11:9001",
        ...     data_dir="/data/node1",
        ...     cluster=["172.20.0.11:9001", "172.20.0.12:9001", "172.20.0.13:9001"]
        ... )
        >>> node.start()  # Automatically joins or forms cluster

    Note:
        Always use specific IP addresses, not 0.0.0.0, for cluster communication.
        The node must be started before performing database operations.
    """

    def __init__(
        self,
        address: str,
        data_dir: str | Path,
        *,
        node_id: Optional[int] = None,
        bind_address: Optional[str] = None,
        cluster: Optional[list[str]] = None,
        auto_recovery: Optional[bool] = True,
        busy_timeout_ms: Optional[int] = None,
        snapshot_compression: Optional[bool] = None,
        network_latency_ms: Optional[int] = None,
    ) -> None:
        """Initialize a dqlite node.

        Creates a new dqlite node that can operate standalone or as part of a cluster.
        The node is created but not started - call start() to begin operations.

        Args:
            address: Network address for cluster communication in "IP:PORT" format.
                    Must be reachable by other cluster members. Example: "192.168.1.10:9001"
            data_dir: Directory path for storing Raft logs, snapshots, and cluster state.
                     Will be created if it doesn't exist.
            node_id: Unique identifier for this node (auto-generated from address if None).
                    Use consistent IDs when restarting nodes.
            bind_address: Optional specific address to bind to if different from address.
                         Useful for NAT/docker scenarios.
            cluster: List of all cluster member addresses including this node.
                    Example: ["172.20.0.11:9001", "172.20.0.12:9001", "172.20.0.13:9001"]
                    If empty/None, node runs standalone.
            auto_recovery: Enable automatic recovery from transient failures (default: True).
            busy_timeout_ms: Milliseconds to wait when database is locked (SQLite PRAGMA).
            snapshot_compression: Enable compression for Raft snapshots to save disk space.
            network_latency_ms: Expected network latency hint for Raft timing optimization.

        Raises:
            NodeError: If node creation fails (invalid parameters, directory issues, etc.)

        Example:
            >>> # Standalone node
            >>> node = Node("127.0.0.1:9001", "/tmp/dqlite")
            >>>
            >>> # Cluster node with options
            >>> node = Node(
            ...     address="192.168.1.10:9001",
            ...     data_dir=Path("/var/lib/dqlite"),
            ...     cluster=["192.168.1.10:9001", "192.168.1.11:9001"],
            ...     auto_recovery=True,
            ...     snapshot_compression=True
            ... )
        """
        # Initialize critical attributes FIRST so __del__ won't fail if __init__ raises
        self._lib = get_library()
        self._lock = threading.RLock()
        self._handle = 0
        self._started = False
        self._finalizer = None  # Will be set after handle creation

        # Now initialize remaining attributes
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._address = address
        self._cluster = cluster or []
        self._shutdown_guard = ShutdownSafetyGuard(f"node_{address}")

        encoded_address = address.encode("utf-8")
        encoded_data_dir = str(self._data_dir).encode("utf-8")

        if node_id is None:
            node_id = int(self._lib.dqlitepy_generate_node_id(encoded_address))
        self._id = node_id

        handle_p = ffi.new("dqlitepy_handle *")

        # Use cluster-aware creation if cluster addresses are provided
        if cluster:
            cluster_csv = ",".join(cluster).encode("utf-8")
            rc = self._lib.dqlitepy_node_create_with_cluster(
                node_id, encoded_address, encoded_data_dir, cluster_csv, handle_p
            )
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_create_with_cluster",
                    node_id=node_id,
                    node_address=address,
                )
        else:
            rc = self._lib.dqlitepy_node_create(
                node_id, encoded_address, encoded_data_dir, handle_p
            )
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_create",
                    node_id=node_id,
                    node_address=address,
                )

        self._handle = int(handle_p[0])
        # NOTE: Disabling finalizer to work around upstream segfault in dqlite C library.
        # The dqlitepy_node_destroy() function triggers segfaults during cleanup.
        # This means nodes won't be automatically cleaned up on garbage collection,
        # but explicit close() calls won't cause segfaults either.
        # See: https://github.com/canonical/go-dqlite/issues
        # self._finalizer = weakref.finalize(self, _destroy_node, self._lib, self._handle)
        self._finalizer = None
        # _started already initialized to False at the top of __init__

        if bind_address:
            rc = self._lib.dqlitepy_node_set_bind_address(
                self._handle, bind_address.encode("utf-8")
            )
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_set_bind_address",
                    node_id=node_id,
                    node_address=address,
                )
            self._bind_address = bind_address
        else:
            self._bind_address = None

        if auto_recovery is not None:
            rc = self._lib.dqlitepy_node_set_auto_recovery(
                self._handle, int(bool(auto_recovery))
            )
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_set_auto_recovery",
                    node_id=node_id,
                    node_address=address,
                )

        if busy_timeout_ms is not None:
            rc = self._lib.dqlitepy_node_set_busy_timeout(
                self._handle, int(busy_timeout_ms)
            )
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_set_busy_timeout",
                    node_id=node_id,
                    node_address=address,
                )

        if snapshot_compression is not None:
            rc = self._lib.dqlitepy_node_set_snapshot_compression(
                self._handle, int(bool(snapshot_compression))
            )
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_set_snapshot_compression",
                    node_id=node_id,
                    node_address=address,
                )

        if network_latency_ms is not None:
            rc = self._lib.dqlitepy_node_set_network_latency_ms(
                self._handle, int(network_latency_ms)
            )
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_set_network_latency_ms",
                    node_id=node_id,
                    node_address=address,
                )

    @property
    def id(self) -> int:
        """Get the unique identifier for this node.

        Returns:
            int: The node's unique ID (uint64 internally).
        """
        return self._id

    @property
    def address(self) -> str:
        """Get the cluster communication address for this node.

        Returns:
            str: Address in "IP:PORT" format.
        """
        return self._address

    @property
    def bind_address(self) -> Optional[str]:
        """Get the bind address if different from the cluster address.

        Returns:
            Optional[str]: Bind address or None if using cluster address.
        """
        return self._bind_address

    @property
    def data_dir(self) -> Path:
        """Get the data directory path.

        Returns:
            Path: Directory containing Raft logs and snapshots.
        """
        return self._data_dir

    @property
    def is_running(self) -> bool:
        """Check if the node is currently running.

        Returns:
            bool: True if node has been started and not stopped.
        """
        return self._started

    def start(self) -> None:
        """Start the dqlite node.

        Raises:
            NodeAlreadyRunningError: If node is already running
            NodeStartError: If node fails to start
        """
        with self._lock:
            if self._started:
                raise NodeAlreadyRunningError(
                    -1,
                    "node_start",
                    "Node is already running",
                    node_id=self._id,
                    node_address=self._address,
                )
            rc = self._lib.dqlitepy_node_start(self._handle)
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_start",
                    node_id=self._id,
                    node_address=self._address,
                )
            self._started = True
            logger.info(f"Node {self._id} started at {self._address}")

    def handover(self) -> None:
        """Gracefully hand over leadership to another node.

        Raises:
            NodeNotRunningError: If node is not running
            NodeError: If handover fails
        """
        with self._lock:
            if not self._started:
                raise NodeNotRunningError(
                    -1,
                    "node_handover",
                    "Node is not running",
                    node_id=self._id,
                    node_address=self._address,
                )
            rc = self._lib.dqlitepy_node_handover(self._handle)
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_handover",
                    node_id=self._id,
                    node_address=self._address,
                )
            logger.info(f"Node {self._id} handed over leadership")

    def stop(self) -> None:
        """Stop the dqlite node using safe shutdown guard.

        This method uses the ShutdownSafetyGuard to handle known issues
        like assertion failures in dqlite_node_stop.

        Set DQLITEPY_BYPASS_STOP=1 to skip calling the C stop function entirely,
        which avoids the segfault bug at the cost of not doing graceful shutdown.

        Raises:
            NodeStopError: If node fails to stop (only if unrecoverable)
        """
        with self._lock:
            if not self._started:
                logger.debug(f"Node {self._id} already stopped")
                return

            # Option 1: Bypass the C stop() call entirely (avoids segfault)
            if _BYPASS_NODE_STOP:
                logger.info(
                    f"Node {self._id} stop bypassed (DQLITEPY_BYPASS_STOP=1). "
                    "The C library will be cleaned up when the process exits."
                )
                self._started = False
                return

            # Option 2: Try normal stop with error recovery
            def _stop() -> None:
                rc = self._lib.dqlitepy_node_stop(self._handle)
                if rc != 0:
                    _raise_node_error(
                        self._lib,
                        rc,
                        "dqlitepy_node_stop",
                        node_id=self._id,
                        node_address=self._address,
                    )

            # Use safety guard to handle known shutdown issues
            if self._shutdown_guard.attempt_shutdown(_stop):
                self._started = False
                logger.info(f"Node {self._id} stopped successfully")
            else:
                logger.warning(
                    f"Node {self._id} stop encountered issues, forcing cleanup"
                )
                self._started = False

    def close(self) -> None:
        """Close the node and release resources.

        This method ensures safe cleanup even if stop() encounters issues.
        """
        with self._lock:
            # NOTE: Not calling stop() here due to upstream segfault in dqlite C library.
            # The finalizer will handle cleanup when the node is garbage collected.
            # See: https://github.com/canonical/go-dqlite/issues
            # if getattr(self, '_started', False):
            #     with safe_operation("node_stop_in_close", suppress_errors=True):
            #         self.stop()

            finalizer = getattr(self, "_finalizer", None)
            if finalizer is not None and finalizer.alive:
                with safe_operation("node_finalizer", suppress_errors=True):
                    # Detach finalizer and manually invoke it to prevent double-free
                    # detach() returns (obj, func, args, kwargs)
                    obj, func, args, kwargs = finalizer.detach()
                    if func is not None and self._handle != 0:
                        func(*args, **kwargs)
                        self._handle = 0
            elif self._handle != 0:
                # If finalizer already ran or doesn't exist, just clear the handle
                self._handle = 0
            if hasattr(self, "_id"):
                logger.debug(f"Node {self._id} closed")

    def open_db(self, db_name: str = "db.sqlite") -> None:
        """Open a database connection using the dqlite driver.

        This opens a connection that uses dqlite's Raft-based replication
        for all SQL operations, ensuring data is replicated across the cluster.

        Args:
            db_name: Name of the database file (default: "db.sqlite")

        Raises:
            NodeNotRunningError: If node is not started
            DatabaseError: If database fails to open
        """
        with self._lock:
            if not self._started:
                raise NodeNotRunningError(
                    -1,
                    "node_open_db",
                    "Node is not running",
                    node_id=self._id,
                    node_address=self._address,
                )

            db_name_c = make_string(db_name)
            rc = self._lib.dqlitepy_node_open_db(self._handle, db_name_c)
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_open_db",
                    node_id=self._id,
                    node_address=self._address,
                )
            logger.info(f"Node {self._id} opened database: {db_name}")

    def exec(self, sql: str) -> tuple[int, int]:
        """Execute SQL statement that doesn't return rows (INSERT, UPDATE, DELETE, etc.).

        Uses dqlite's distributed protocol to ensure the operation is replicated
        across all nodes in the cluster via Raft consensus.

        Args:
            sql: SQL statement to execute

        Returns:
            Tuple of (last_insert_id, rows_affected)

        Raises:
            DatabaseError: If SQL execution fails
        """
        with self._lock:
            sql_c = make_string(sql)
            last_insert_id = ffi.new("int64_t *")
            rows_affected = ffi.new("int64_t *")

            rc = self._lib.dqlitepy_node_exec(
                self._handle, sql_c, last_insert_id, rows_affected
            )
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_exec",
                    node_id=self._id,
                    node_address=self._address,
                )

            return (int(last_insert_id[0]), int(rows_affected[0]))

    def query(self, sql: str) -> list[dict[str, Any]]:
        """Execute SQL query that returns rows (SELECT).

        Uses dqlite's distributed protocol to query data that has been
        replicated across the cluster.

        Args:
            sql: SQL query to execute

        Returns:
            List of dictionaries, one per row, with column names as keys

        Raises:
            DatabaseError: If query execution fails
        """
        import json

        with self._lock:
            sql_c = make_string(sql)
            json_out = ffi.new("char **")

            rc = self._lib.dqlitepy_node_query(self._handle, sql_c, json_out)
            if rc != 0:
                _raise_node_error(
                    self._lib,
                    rc,
                    "dqlitepy_node_query",
                    node_id=self._id,
                    node_address=self._address,
                )

            # Parse JSON result
            json_str = string_from_c(json_out[0])
            self._lib.dqlitepy_free(json_out[0])

            if not json_str:
                return []

            return json.loads(json_str)

    def begin(self) -> None:
        """Begin an explicit transaction.

        Executes BEGIN TRANSACTION to start a transaction block.
        All subsequent operations will be part of this transaction until
        commit() or rollback() is called.

        Raises:
            DatabaseError: If BEGIN fails
        """
        self.exec("BEGIN TRANSACTION")
        logger.debug(f"Node {self._id}: Transaction started")

    def commit(self) -> None:
        """Commit the current transaction.

        Executes COMMIT to commit all changes made in the current transaction.

        Raises:
            DatabaseError: If COMMIT fails
        """
        self.exec("COMMIT")
        logger.debug(f"Node {self._id}: Transaction committed")

    def rollback(self) -> None:
        """Roll back the current transaction.

        Executes ROLLBACK to undo all changes made in the current transaction.

        Raises:
            DatabaseError: If ROLLBACK fails
        """
        self.exec("ROLLBACK")
        logger.debug(f"Node {self._id}: Transaction rolled back")

    def __enter__(self) -> "Node":
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Context manager exit with safe cleanup."""
        try:
            if exc is None:
                # Only try handover if no exception occurred
                with safe_operation("node_handover_on_exit", suppress_errors=True):
                    self.handover()
        finally:
            # Always close, even if handover fails
            with safe_operation("node_close_on_exit", suppress_errors=True):
                self.close()

    def __del__(self) -> None:  # pragma: no cover - destructor safety
        """Destructor with guaranteed safe cleanup."""
        try:
            with safe_operation("node_destructor", suppress_errors=True):
                self.close()
        except Exception:
            # Absolutely never let destructor raise
            pass
