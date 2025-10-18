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

"""SQLAlchemy dialect for dqlite.

This module provides a SQLAlchemy dialect that allows using dqlite as a backend
for SQLAlchemy ORM and Core, with automatic replication across the cluster.

Usage:
    from dqlitepy import Node
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.orm import declarative_base, Session

    # Create and start a dqlite node
    node = Node("127.0.0.1:9001", "/data")
    node.start()

    # Create engine with dqlite dialect
    from dqlitepy.sqlalchemy import register_dqlite_node
    register_dqlite_node(node)

    engine = create_engine("dqlite:///mydb.sqlite")

    # Use SQLAlchemy as normal
    Base = declarative_base()

    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String)

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(User(name="Alice"))
        session.commit()
"""

import logging
from typing import Any, List, Optional

try:
    from sqlalchemy import types as sqltypes
    from sqlalchemy.engine import default
    from sqlalchemy.sql import compiler, text
except ImportError:
    raise ImportError(
        "SQLAlchemy is required to use the dqlite dialect. "
        "Install it with: pip install sqlalchemy"
    )

import json as json_module
from . import dbapi
from .node import Node

__all__ = [
    "DQLiteDialect",
    "register_dqlite_node",
    "get_registered_node",
    "JSON",
    "JSONB",
]

logger = logging.getLogger(__name__)

# Global registry for dqlite nodes (indexed by connection string)
_node_registry: dict[str, Node] = {}
_default_node: Optional[Node] = None


def register_dqlite_node(node: Node, name: str = "default") -> None:
    """Register a dqlite node for use with SQLAlchemy.

    This must be called before creating a SQLAlchemy engine with the dqlite dialect.

    Args:
        node: A running dqlite Node instance
        name: Name to register the node under (default: "default")

    Example:
        >>> node = Node("127.0.0.1:9001", "/data")
        >>> node.start()
        >>> register_dqlite_node(node)
        >>> engine = create_engine("dqlite:///mydb.sqlite")
    """
    global _default_node
    _node_registry[name] = node
    if name == "default":
        _default_node = node
    logger.info(f"Registered dqlite node as '{name}'")


def get_registered_node(name: str = "default") -> Node:
    """Get a registered dqlite node by name.

    Args:
        name: Name of the registered node (default: "default")

    Returns:
        The registered Node instance

    Raises:
        ValueError: If no node is registered with that name
    """
    if name not in _node_registry:
        raise ValueError(
            f"No dqlite node registered as '{name}'. Call register_dqlite_node() first."
        )
    return _node_registry[name]


class JSON(sqltypes.TypeDecorator):
    """SQLAlchemy type for JSON stored in SQLite TEXT column.

    Automatically serializes Python objects to JSON strings when storing,
    and deserializes JSON strings back to Python objects when loading.

    Example:
        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            metadata = Column(JSON)

        # Store
        user = User(metadata={"age": 30, "city": "NYC"})

        # Load
        print(user.metadata["age"])  # 30
    """

    impl = sqltypes.TEXT
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Optional[str]:
        """Convert Python value to JSON string for storage."""
        if value is None:
            return None
        return json_module.dumps(value)

    def process_result_value(self, value: Optional[str], dialect: Any) -> Any:
        """Convert JSON string from storage to Python value."""
        if value is None:
            return None
        return json_module.loads(value)


class JSONB(JSON):
    """Alias for JSON type (SQLite doesn't distinguish JSON vs JSONB)."""

    pass


class DQLiteCompiler(compiler.SQLCompiler):
    """SQL compiler for dqlite dialect.

    Handles dqlite-specific SQL generation.
    """

    pass


class DQLiteTypeCompiler(compiler.GenericTypeCompiler):
    """Type compiler for dqlite dialect.

    Maps SQLAlchemy types to dqlite/SQLite types.
    """

    pass


class DQLiteDialect(default.DefaultDialect):
    """SQLAlchemy dialect for dqlite.

    This dialect allows SQLAlchemy to work with dqlite databases,
    automatically replicating all operations across the cluster.
    """

    name = "dqlite"
    driver = "dqlitepy"

    # SQLAlchemy capabilities
    supports_alter = True
    supports_native_boolean = False
    supports_native_decimal = False
    supports_default_values = True
    supports_empty_insert = False
    supports_sequences = False
    supports_statement_cache = True

    # Transaction support
    supports_sane_rowcount = True
    supports_sane_multi_rowcount = False

    # Reflection capabilities
    supports_views = True

    # dqlite is based on SQLite
    default_paramstyle = "qmark"
    statement_compiler = DQLiteCompiler
    type_compiler = DQLiteTypeCompiler

    # Custom type mappings
    colspecs = {
        sqltypes.JSON: JSON,
    }

    @classmethod
    def dbapi(cls) -> Any:
        """Return the DB-API 2.0 module.

        Returns:
            The dqlitepy.dbapi module
        """
        return dbapi

    def create_connect_args(self, url: Any) -> tuple[list[Any], dict[str, Any]]:
        """Parse connection URL and return connection arguments.

        Args:
            url: SQLAlchemy URL object

        Returns:
            Tuple of (args, kwargs) for dbapi.connect()

        The URL format is: dqlite:///database.sqlite
        Or with a named node: dqlite+nodename:///database.sqlite
        """
        # Extract database name from URL
        database = url.database or "db.sqlite"

        # Extract node name from driver (e.g., "dqlitepy+mynode")
        node_name = "default"
        if "+" in (url.drivername or ""):
            parts = url.drivername.split("+", 1)
            if len(parts) > 1:
                node_name = parts[1]

        # Get the registered node
        try:
            node = get_registered_node(node_name)
        except ValueError as e:
            raise ValueError(
                f"Cannot create dqlite connection: {e}\n"
                f"Make sure to call register_dqlite_node() before creating the engine."
            ) from e

        # Return connection arguments
        return ([], {"node": node, "database": database})

    def do_rollback(self, dbapi_connection: Any) -> None:
        """Perform a rollback on the connection.

        Note: dqlite doesn't support explicit rollback yet.
        """
        # No-op for now
        pass

    def do_commit(self, dbapi_connection: Any) -> None:
        """Perform a commit on the connection.

        Note: dqlite commits are implicit via Raft consensus.
        """
        # No-op - dqlite handles commits automatically
        pass

    def do_close(self, dbapi_connection: Any) -> None:
        """Close the database connection."""
        dbapi_connection.close()

    def has_table(
        self, connection: Any, table_name: str, schema: Optional[str] = None, **kw: Any
    ) -> bool:
        """Check if a table exists in the database.

        Args:
            connection: SQLAlchemy connection
            table_name: Name of the table
            schema: Schema name (ignored for dqlite/SQLite)

        Returns:
            True if table exists, False otherwise
        """
        result = connection.execute(
            text(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            )
        )
        row = result.fetchone()
        return row is not None

    def get_table_names(
        self, connection: Any, schema: Optional[str] = None, **kw: Any
    ) -> list[str]:
        """Get list of table names in the database.

        Args:
            connection: SQLAlchemy connection
            schema: Schema name (ignored for dqlite/SQLite)
            **kw: Additional keyword arguments

        Returns:
            List of table names
        """
        result = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        )
        return [row[0] for row in result.fetchall()]

    def get_view_names(
        self, connection: Any, schema: Optional[str] = None, **kw: Any
    ) -> list[str]:
        """Get list of view names in the database.

        Args:
            connection: SQLAlchemy connection
            schema: Schema name (ignored for dqlite/SQLite)
            **kw: Additional keyword arguments

        Returns:
            List of view names
        """
        result = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        )
        return [row[0] for row in result.fetchall()]

    def get_columns(
        self, connection: Any, table_name: str, schema: Optional[str] = None, **kw: Any
    ) -> List[Any]:
        """Get column information for a table.

        Args:
            connection: SQLAlchemy connection
            table_name: Name of the table
            schema: Schema name (ignored for dqlite/SQLite)
            **kw: Additional keyword arguments

        Returns:
            List of column dictionaries
        """
        result = connection.execute(text(f"PRAGMA table_info({table_name})"))

        columns = []
        for row in result.fetchall():
            cid, name, type_, notnull, default, pk = row
            columns.append(
                {
                    "name": name,
                    "type": self._resolve_type(type_),
                    "nullable": not bool(notnull),
                    "default": default,
                    "primary_key": bool(pk),
                }
            )

        return columns

    def _resolve_type(self, type_string: str) -> sqltypes.TypeEngine:
        """Resolve SQLite type string to SQLAlchemy type.

        Args:
            type_string: SQLite type string (e.g., "INTEGER", "TEXT")

        Returns:
            SQLAlchemy type object
        """
        type_upper = type_string.upper()

        if "INT" in type_upper:
            return sqltypes.INTEGER()
        elif "CHAR" in type_upper or "CLOB" in type_upper or "TEXT" in type_upper:
            return sqltypes.TEXT()
        elif "BLOB" in type_upper:
            return sqltypes.BLOB()
        elif "REAL" in type_upper or "FLOAT" in type_upper or "DOUBLE" in type_upper:
            return sqltypes.REAL()
        elif "NUMERIC" in type_upper or "DECIMAL" in type_upper:
            return sqltypes.NUMERIC()
        else:
            return sqltypes.NullType()


# Register the dialect with SQLAlchemy
try:
    from sqlalchemy.dialects import registry

    registry.register("dqlite", "dqlitepy.sqlalchemy", "DQLiteDialect")
    logger.info("Registered dqlite SQLAlchemy dialect")
except ImportError:
    pass  # SQLAlchemy not available or old version
