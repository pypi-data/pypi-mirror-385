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

"""PEP 249 (DB-API 2.0) compliant interface for dqlite.

This module provides a DB-API 2.0 compliant interface that can be used
with SQLAlchemy and other Python database libraries.
"""

import logging
import threading
from typing import Any, Iterator, Optional, Sequence

from .node import Node

__all__ = [
    "connect",
    "Connection",
    "Cursor",
    "Error",
    "Warning",
    "InterfaceError",
    "DatabaseError",
    "DataError",
    "OperationalError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",
    "apilevel",
    "threadsafety",
    "paramstyle",
]

logger = logging.getLogger(__name__)

# DB-API 2.0 module globals
apilevel = "2.0"
threadsafety = 1  # Threads may share the module, but not connections
paramstyle = "qmark"  # Use ? for parameters


# DB-API 2.0 exceptions hierarchy
class Error(Exception):
    """Base class for all dqlite errors."""

    pass


class Warning(Exception):
    """Exception for important warnings."""

    pass


class InterfaceError(Error):
    """Error related to the database interface."""

    pass


class DatabaseError(Error):
    """Error related to the database."""

    pass


class DataError(DatabaseError):
    """Error due to problems with processed data."""

    pass


class OperationalError(DatabaseError):
    """Error related to database operation."""

    pass


class IntegrityError(DatabaseError):
    """Error when database relational integrity is affected."""

    pass


class InternalError(DatabaseError):
    """Error when database encounters an internal error."""

    pass


class ProgrammingError(DatabaseError):
    """Error related to SQL programming."""

    pass


class NotSupportedError(DatabaseError):
    """Error when using unsupported database feature."""

    pass


def connect(node: Node, database: str = "db.sqlite") -> "Connection":
    """Create a DB-API 2.0 connection to a dqlite database.

    Args:
        node: A running dqlite Node instance
        database: Name of the database (default: "db.sqlite")

    Returns:
        A Connection object

    Example:
        >>> from dqlitepy import Node
        >>> from dqlitepy.dbapi import connect
        >>> node = Node("127.0.0.1:9001", "/data")
        >>> node.start()
        >>> conn = connect(node, "mydb.sqlite")
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT * FROM users")
    """
    conn = Connection(node, database)
    return conn


class Connection:
    """DB-API 2.0 Connection object.

    This class provides a PEP 249 compliant interface for dqlite connections.
    All SQL operations are automatically replicated across the cluster via Raft.
    """

    def __init__(self, node: Node, database: str):
        """Initialize connection.

        Args:
            node: A running dqlite Node instance
            database: Name of the database
        """
        self.node = node
        self.database = database
        self._closed = False
        self._lock = threading.Lock()

        # Open the database connection
        try:
            self.node.open_db(database)
            logger.info(f"Opened dqlite database: {database}")
        except Exception as e:
            raise OperationalError(f"Failed to open database: {e}") from e

    def close(self) -> None:
        """Close the connection.

        The connection is unusable after this call.
        """
        with self._lock:
            if not self._closed:
                self._closed = True
                logger.info(f"Closed dqlite connection to: {self.database}")

    def begin(self) -> None:
        """Begin an explicit transaction.

        Starts a transaction block. All subsequent operations will be part
        of this transaction until commit() or rollback() is called.

        Example:
            conn.begin()
            cursor.execute("INSERT INTO users (name) VALUES ('Alice')")
            cursor.execute("INSERT INTO posts (title) VALUES ('Hello')")
            conn.commit()  # Both inserts committed atomically
        """
        self._check_closed()
        self.node.begin()

    def commit(self) -> None:
        """Commit any pending transaction.

        If an explicit transaction was started with BEGIN, this commits it.
        Otherwise, this is a no-op (dqlite auto-commits individual statements).
        """
        self._check_closed()
        try:
            self.node.commit()
        except Exception:
            # If no transaction is active, commit will fail - that's OK
            pass

    def rollback(self) -> None:
        """Roll back any pending transaction.

        If an explicit transaction was started with BEGIN, this rolls it back.
        Otherwise, raises NotSupportedError.
        """
        self._check_closed()
        try:
            self.node.rollback()
        except Exception as e:
            raise OperationalError(f"Failed to rollback transaction: {e}") from e

    def cursor(self) -> "Cursor":
        """Create a new cursor object using the connection.

        Returns:
            A new Cursor instance
        """
        self._check_closed()
        return Cursor(self)

    def _check_closed(self) -> None:
        """Check if connection is closed and raise if so."""
        if self._closed:
            raise InterfaceError("Connection is closed")

    def __enter__(self) -> "Connection":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is None:
            self.commit()
        else:
            try:
                self.rollback()
            except NotSupportedError:
                pass  # Rollback not supported yet
        self.close()


class Cursor:
    """DB-API 2.0 Cursor object.

    This class provides a PEP 249 compliant interface for executing SQL
    statements and fetching results.
    """

    def __init__(self, connection: Connection):
        """Initialize cursor.

        Args:
            connection: The parent Connection object
        """
        self.connection = connection
        self._closed = False
        self._results: list[dict[str, Any]] = []
        self._row_index = 0
        self._description: Optional[Sequence[Sequence[Any]]] = None
        self._column_order: list[str] = []  # Track column order from query results
        self._rowcount = -1
        self._lastrowid: Optional[int] = None
        self.arraysize = 1

    @property
    def description(self) -> Optional[Sequence[Sequence[Any]]]:
        """Column description of the last query result.

        Returns a sequence of 7-item sequences, each containing:
        (name, type_code, display_size, internal_size, precision, scale, null_ok)

        For dqlite, we only populate name and set others to None.
        """
        return self._description

    @property
    def rowcount(self) -> int:
        """Number of rows affected by last execute() for DML statements.

        Returns -1 if not applicable or not available.
        """
        return self._rowcount

    @property
    def lastrowid(self) -> Optional[int]:
        """Last row ID of an INSERT statement."""
        return self._lastrowid

    def close(self) -> None:
        """Close the cursor."""
        self._closed = True
        self._results = []
        self._description = None
        self._column_order = []

    def execute(
        self, operation: str, parameters: Optional[Sequence[Any]] = None
    ) -> "Cursor":
        """Execute a database operation (query or command).

        Args:
            operation: SQL statement to execute
            parameters: Optional sequence of parameters for ? placeholders

        Returns:
            self (for method chaining)

        Raises:
            ProgrammingError: If cursor is closed or SQL is invalid
        """
        self._check_closed()
        self.connection._check_closed()

        # Bind parameters if provided
        if parameters:
            operation = self._bind_parameters(operation, parameters)

        # Reset state
        self._results = []
        self._row_index = 0
        self._description = None
        self._rowcount = -1
        self._lastrowid = None

        # Determine if this is a query or command
        operation_upper = operation.strip().upper()
        is_query = operation_upper.startswith("SELECT") or operation_upper.startswith(
            "PRAGMA"
        )

        try:
            if is_query:
                # Execute query and get results
                self._results = self.connection.node.query(operation)
                self._rowcount = len(self._results)

                # Build description from first row if available
                if self._results:
                    first_row = self._results[0]
                    # IMPORTANT: Store the column order from the first result
                    # This order will be used to convert dicts to tuples
                    self._column_order = list(first_row.keys())
                    self._description = tuple(
                        (name, None, None, None, None, None, None)
                        for name in self._column_order
                    )
                else:
                    self._column_order = []
                    self._description = tuple()
            else:
                # Execute command (INSERT, UPDATE, DELETE, etc.)
                last_id, rows_affected = self.connection.node.exec(operation)
                self._lastrowid = last_id if last_id else None
                self._rowcount = rows_affected
        except Exception as e:
            raise ProgrammingError(f"Failed to execute SQL: {e}") from e

        return self

    def executemany(
        self, operation: str, seq_of_parameters: Sequence[Sequence[Any]]
    ) -> "Cursor":
        """Execute operation multiple times with different parameters.

        Args:
            operation: SQL statement to execute
            seq_of_parameters: Sequence of parameter sequences

        Returns:
            self (for method chaining)

        Raises:
            ProgrammingError: If execution fails
        """
        self._check_closed()

        # Execute each parameter set
        total_rowcount = 0
        last_lastrowid = None

        for parameters in seq_of_parameters:
            self.execute(operation, parameters)
            if self._rowcount > 0:
                total_rowcount += self._rowcount
            if self._lastrowid is not None:
                last_lastrowid = self._lastrowid

        # Update cursor state with totals
        self._rowcount = total_rowcount
        self._lastrowid = last_lastrowid

        return self

    def fetchone(self) -> Optional[tuple[Any, ...]]:
        """Fetch the next row of a query result set.

        Returns:
            A tuple of column values, or None when no more data is available
        """
        self._check_closed()

        if self._row_index >= len(self._results):
            return None

        row_dict = self._results[self._row_index]
        self._row_index += 1

        # Convert dict to tuple in column order
        if self._description:
            return tuple(row_dict.get(col[0]) for col in self._description)
        return tuple(row_dict.values())

    def fetchmany(self, size: Optional[int] = None) -> list[tuple[Any, ...]]:
        """Fetch the next set of rows of a query result.

        Args:
            size: Number of rows to fetch (default: arraysize)

        Returns:
            A list of tuples
        """
        self._check_closed()

        if size is None:
            size = self.arraysize

        results = []
        for _ in range(size):
            row = self.fetchone()
            if row is None:
                break
            results.append(row)

        return results

    def fetchall(self) -> list[tuple[Any, ...]]:
        """Fetch all remaining rows of a query result.

        Returns:
            A list of tuples
        """
        self._check_closed()

        results = []
        while True:
            row = self.fetchone()
            if row is None:
                break
            results.append(row)

        return results

    def setinputsizes(self, sizes: Sequence[Any]) -> None:
        """Predefine memory areas for parameters (no-op for dqlite)."""
        self._check_closed()
        pass

    def setoutputsize(self, size: int, column: Optional[int] = None) -> None:
        """Set column buffer size for fetches (no-op for dqlite)."""
        self._check_closed()
        pass

    def _bind_parameters(self, operation: str, parameters: Sequence[Any]) -> str:
        """Bind parameters to SQL statement using qmark style (? placeholders).

        Args:
            operation: SQL statement with ? placeholders
            parameters: Sequence of parameter values

        Returns:
            SQL statement with parameters substituted

        Raises:
            ProgrammingError: If parameter count doesn't match placeholder count
        """
        # Count placeholders
        placeholder_count = operation.count("?")
        param_count = len(parameters)

        if placeholder_count != param_count:
            raise ProgrammingError(
                f"Parameter count mismatch: expected {placeholder_count}, got {param_count}"
            )

        # Convert parameters to SQL literals
        def escape_value(value: Any) -> str:
            """Convert Python value to SQL literal."""
            if value is None:
                return "NULL"
            elif isinstance(value, bool):
                # SQLite uses 0/1 for boolean
                return "1" if value else "0"
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, str):
                # Escape single quotes by doubling them
                return "'" + value.replace("'", "''") + "'"
            elif isinstance(value, bytes):
                # SQLite BLOB literal format: X'hex'
                return "X'" + value.hex() + "'"
            else:
                # Try to convert to string
                return "'" + str(value).replace("'", "''") + "'"

        # Replace placeholders with escaped values
        result = operation
        for param in parameters:
            result = result.replace("?", escape_value(param), 1)

        return result

    def _check_closed(self) -> None:
        """Check if cursor is closed and raise if so."""
        if self._closed:
            raise InterfaceError("Cursor is closed")

    def __iter__(self) -> Iterator[tuple[Any, ...]]:
        """Make cursor iterable."""
        self._check_closed()
        return self

    def __next__(self) -> tuple[Any, ...]:
        """Get next row for iteration."""
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row

    def __enter__(self) -> "Cursor":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
