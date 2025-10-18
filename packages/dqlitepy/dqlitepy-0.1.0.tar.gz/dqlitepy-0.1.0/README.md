<div align="center">

# dqlitepy

Python bindings for dqlite - Distributed SQLite

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/dqlitepy.svg)](https://pypi.org/project/dqlitepy/)

![Build Status](https://img.shields.io/github/actions/workflow/status/vantagecompute/dqlitepy/ci.yaml?branch=main&label=build&logo=github&style=plastic)
![GitHub Issues](https://img.shields.io/github/issues/vantagecompute/dqlitepy?label=issues&logo=github&style=plastic)
![Pull Requests](https://img.shields.io/github/issues-pr/vantagecompute/dqlitepy?label=pull-requests&logo=github&style=plastic)
![GitHub Contributors](https://img.shields.io/github/contributors/vantagecompute/dqlitepy?logo=github&style=plastic)

</br>

</div>

Python bindings for the dqlite distributed SQLite engine. Ships with a self-contained Go shim that bundles the native runtime—no system dependencies required.

## 📚 Documentation

**[Full Documentation →](https://vantagecompute.github.io/dqlitepy)**

Complete guides, API reference, clustering setup, and examples.

## ✨ Features

- 🚀 **Node Management** - Create and manage dqlite nodes
- 🔗 **Cluster Support** - Programmatically form and manage clusters  
- 📦 **Self-Contained** - No system dependencies required
- 🔒 **Thread-Safe** - Safe for concurrent use
- 🐍 **DB-API 2.0** - Standard Python database interface
- 🎯 **SQLAlchemy Support** - Use with your favorite ORM

## 🚀 Quick Start

### Installation

```bash
pip install dqlitepy
```

### Basic Usage

```python
import dqlitepy

# Connect using DB-API 2.0
conn = dqlitepy.connect(
    address="127.0.0.1:9001",
    data_dir="/tmp/dqlite-data"
)

cursor = conn.cursor()
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
cursor.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
conn.commit()

cursor.execute("SELECT * FROM users")
print(cursor.fetchall())
conn.close()
```

### Node Management

```python
from dqlitepy import Node
from pathlib import Path

# Create and start a node
with Node(
    address="127.0.0.1:9001",
    data_dir=Path("/tmp/dqlite-data"),
) as node:
    print(f"Node {node.id} running at {node.address}")
```

### Clustering

```python
from dqlitepy import Node, Client

# Start bootstrap node
node1 = Node("127.0.0.1:9001", "/data/node1")
node1.start()

# Connect client and add more nodes
with Client(["127.0.0.1:9001"]) as client:
    node2 = Node("127.0.0.1:9002", "/data/node2")
    node2.start()
    client.add(node2.id, "127.0.0.1:9002")
    
    # Query cluster state
    leader = client.leader()
    nodes = client.cluster()
    print(f"Leader: {leader}")
    for n in nodes:
        print(f"  Node {n.id}: {n.address} ({n.role_name})")
```

## 📖 Learn More

- **[Getting Started Guide](https://vantagecompute.github.io/dqlitepy/docs/getting-started)** - Detailed tutorial
- **[API Reference](https://vantagecompute.github.io/dqlitepy/docs/api)** - Complete API documentation
- **[Clustering Guide](https://vantagecompute.github.io/dqlitepy/docs/clustering)** - Multi-node setup
- **[Examples](https://vantagecompute.github.io/dqlitepy/docs/examples)** - Code examples and patterns

## 🛠️ Development

### Building from Source

```bash
git clone https://github.com/vantagecompute/dqlitepy.git
cd dqlitepy

# Build native library using Docker
just build-lib

# Install in development mode
uv pip install -e .
```

### Running Tests

```bash
# Run test suite
just unit

# Run linting and type checking
just lint
just typecheck
```

### Project Commands

The project uses [just](https://github.com/casey/just) for task automation:

```bash
sudo snap install just --classic
```

- `just unit` - Run tests with coverage
- `just lint` - Check code style
- `just typecheck` - Run static type checking
- `just fmt` - Format code
- `just build-lib` - Build native library (Docker)
- `just docs-dev` - Start documentation dev server

See the [justfile](justfile) for all available commands.

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

Copyright 2025 Vantage Compute

## 🤝 Contributing

Contributions welcome! Please see our [Contributing Guide](https://vantagecompute.github.io/dqlitepy/docs/contributing) for details.

## 💬 Support

- [GitHub Issues](https://github.com/vantagecompute/dqlitepy/issues) - Bug reports and feature requests
- [Documentation](https://vantagecompute.github.io/dqlitepy) - Comprehensive guides and API reference
- [Examples](examples/) - Sample code and use cases
