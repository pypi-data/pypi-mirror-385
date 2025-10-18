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

import os
import platform
import threading
from ctypes.util import find_library
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence, Tuple

from cffi import FFI  # type: ignore[import]

# Import exceptions - but keep backward compatibility exports
from .exceptions import DqliteError, DqliteLibraryNotFound


ffi: Any = FFI()
ffi.cdef(
    """
    typedef unsigned long long dqlitepy_node_id;
    typedef unsigned long long dqlitepy_handle;

    // Node management functions
    int dqlitepy_node_create(dqlitepy_node_id id, const char *address, const char *data_dir, dqlitepy_handle *handle_out);
    int dqlitepy_node_create_with_cluster(dqlitepy_node_id id, const char *address, const char *data_dir, const char *cluster_csv, dqlitepy_handle *handle_out);
    void dqlitepy_node_destroy(dqlitepy_handle handle);
    int dqlitepy_node_set_bind_address(dqlitepy_handle handle, const char *address);
    int dqlitepy_node_set_auto_recovery(dqlitepy_handle handle, int enabled);
    int dqlitepy_node_set_busy_timeout(dqlitepy_handle handle, unsigned msecs);
    int dqlitepy_node_set_snapshot_compression(dqlitepy_handle handle, int enabled);
    int dqlitepy_node_set_network_latency_ms(dqlitepy_handle handle, unsigned milliseconds);
    int dqlitepy_node_start(dqlitepy_handle handle);
    int dqlitepy_node_handover(dqlitepy_handle handle);
    int dqlitepy_node_stop(dqlitepy_handle handle);

    // Database operations (using dqlite driver for replication)
    int dqlitepy_node_open_db(dqlitepy_handle handle, const char *db_name);
    int dqlitepy_node_exec(dqlitepy_handle handle, const char *sql, int64_t *last_insert_id_out, int64_t *rows_affected_out);
    int dqlitepy_node_query(dqlitepy_handle handle, const char *sql, char **json_out);

    // Client management functions
    int dqlitepy_client_create(const char *addresses_csv, dqlitepy_handle *handle_out);
    int dqlitepy_client_close(dqlitepy_handle handle);
    int dqlitepy_client_add(dqlitepy_handle handle, dqlitepy_node_id id, const char *address);
    int dqlitepy_client_remove(dqlitepy_handle handle, dqlitepy_node_id id);
    int dqlitepy_client_leader(dqlitepy_handle handle, char **address_out);
    int dqlitepy_client_cluster(dqlitepy_handle handle, char **json_out);

    // Utility functions
    const char *dqlitepy_last_error(void);
    void dqlitepy_free(void *ptr);

    dqlitepy_node_id dqlitepy_generate_node_id(const char *address);
    int dqlitepy_version_number(void);
    const char *dqlitepy_version_string(void);
    """
)


# Re-export exceptions for backward compatibility
__all__ = [
    "DqliteError",
    "DqliteLibraryNotFound",
    "configure",
    "ffi",
    "get_library",
    "get_version",
    "make_string",
    "make_string_array",
    "string_from_c",
    "_reset_for_tests",
]


_library_lock = threading.Lock()
_library = None
_library_path: Optional[str] = None


def configure(path: Optional[str]) -> None:
    """Force the bindings to load libdqlitepy from ``path``.

    Passing ``None`` clears the override and re-enables auto-discovery.
    """

    global _library_path, _library
    with _library_lock:
        _library = None
        _library_path = _normalize_path(path) if path else None


def get_library() -> Any:
    """Return a handle to ``libdqlitepy`` using the configured search strategy."""

    global _library, _library_path
    attempts: List[Tuple[str, str]] = []
    loaded_library: Optional[Any] = None
    with _library_lock:
        if _library is not None:
            return _library

        attempts.clear()
        seen: set[str] = set()
        for candidate in _candidate_paths():
            if not candidate:
                continue
            normalized = _normalize_path(candidate)
            if normalized in seen:
                continue
            seen.add(normalized)
            try:
                loaded_library = ffi.dlopen(normalized)
            except OSError as exc:  # pragma: no cover - platform dependent text
                attempts.append((normalized, str(exc)))
                continue

            _library = loaded_library
            _library_path = normalized
            break

    if loaded_library is not None:
        return loaded_library

    raise DqliteLibraryNotFound(attempts)


def _candidate_paths() -> Iterable[str]:
    """Yield possible filesystem locations for ``libdqlitepy``."""

    if _library_path:
        yield _library_path

    yield from _bundled_library_candidates()

    env_path = os.getenv("DQLITEPY_LIBRARY") or os.getenv("DQLITE_LIBRARY")
    if env_path:
        yield env_path

    discovered = find_library("dqlitepy") or find_library("dqlite")
    if discovered:
        yield discovered

    # OS-specific fallbacks ordered by commonness.
    yield from (
        "/usr/lib/libdqlitepy.so",
        "/usr/local/lib/libdqlitepy.so",
        "/usr/lib/x86_64-linux-gnu/libdqlitepy.so",
        "/opt/homebrew/lib/libdqlitepy.dylib",
        "/usr/lib64/libdqlitepy.so",
    )


def get_version() -> Tuple[int, str]:
    """Return the version number and string reported by the shim library."""

    lib = get_library()
    version_number = int(lib.dqlitepy_version_number())
    ptr = lib.dqlitepy_version_string()
    version_string = ffi.string(ptr).decode("utf-8") if ptr != ffi.NULL else ""
    return version_number, version_string


def make_string(value: Optional[str]) -> Optional[bytes]:
    if value is None:
        return None
    return value.encode("utf-8")


def make_string_array(values: Sequence[str]) -> Tuple[Any, List[Any]]:
    """Create a C array of const char* values and keep references alive."""

    if not values:
        return ffi.NULL, []
    items = [ffi.new("char[]", value.encode("utf-8")) for value in values]
    array = ffi.new("const char * []", items)
    return array, items


def string_from_c(pointer: Any) -> Optional[str]:
    if pointer == ffi.NULL:
        return None
    return ffi.string(pointer).decode("utf-8")


def _normalize_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path)) if path else path


def _bundled_library_candidates() -> Iterable[str]:
    package_dir = Path(__file__).resolve().parent
    arch = _platform_tag()
    if arch is None:
        return []
    library_name = _library_filename()
    bundled = package_dir / "_lib" / arch / library_name
    return [str(bundled)]


def _platform_tag() -> Optional[str]:
    system = platform.system().lower()
    machine = platform.machine().lower()

    lookup = {
        ("linux", "x86_64"): "linux-amd64",
        ("linux", "amd64"): "linux-amd64",
        ("linux", "aarch64"): "linux-arm64",
        ("linux", "arm64"): "linux-arm64",
        ("darwin", "x86_64"): "macos-x86_64",
        ("darwin", "arm64"): "macos-arm64",
        ("windows", "amd64"): "windows-amd64",
        ("windows", "x86_64"): "windows-amd64",
    }

    return lookup.get((system, machine))


def _library_filename() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "libdqlitepy.dylib"
    if system == "windows":
        return "dqlitepy.dll"
    return "libdqlitepy.so"


def _reset_for_tests() -> None:
    """Reset global state so tests can reconfigure the loader."""

    global _library, _library_path
    with _library_lock:
        _library = None
        _library_path = None


__all__ = [
    "DqliteError",
    "DqliteLibraryNotFound",
    "configure",
    "ffi",
    "get_library",
    "get_version",
    "make_string",
    "make_string_array",
    "string_from_c",
    "_reset_for_tests",
]
