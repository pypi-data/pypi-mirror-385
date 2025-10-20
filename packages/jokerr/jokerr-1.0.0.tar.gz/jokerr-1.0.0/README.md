# EzDB B-Class (Basic) - Free & Open Source Vector Database

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/ezdb)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)](PRODUCT_TIERS.md)

EzDB is a lightweight, easy-to-use vector database built in Python for semantic search and AI applications.

> **📦 This is EzDB B-Class (Basic)** - The free, open-source version.
> For production features, see [EzDB Professional](PRODUCT_TIERS.md#-ezdb-professional-class) and [EzDB Enterprise](PRODUCT_TIERS.md#-ezdb-enterprise-class).

## ⚡ Quick Links

- 📖 **[Getting Started Guide](GETTING_STARTED.md)** - Learn the basics
- 🚀 **[API Documentation](API.md)** - Complete API reference
- 🐳 **[Docker Quick Start](DOCKER_QUICKSTART.md)** - Deploy in 60 seconds
- 📦 **[Docker Guide](DOCKER.md)** - Complete Docker documentation
- 🏗️ **[Product Tiers](PRODUCT_TIERS.md)** - B-Class, Professional, Enterprise
- 🚀 **[Deployment Guide](DEPLOYMENT.md)** - Production deployment

## Features

- **Vector Storage**: Store and search high-dimensional vectors efficiently
- **Multiple Metrics**: Cosine similarity, Euclidean distance, Dot product
- **Fast Indexing**: HNSW (Hierarchical Navigable Small World) for ANN search
- **Metadata Filtering**: Search with metadata constraints
- **Persistence**: Save/load databases to disk
- **Dual Mode**: Use as embedded library OR REST API server
- **REST API**: Full HTTP API with Python/JavaScript/Go clients
- **Collections**: Manage multiple isolated vector collections
- **Docker Ready**: Easy deployment with Docker and docker-compose

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Embedded Mode (Python Library)

```python
from ezdb import EzDB

# Create a new database
db = EzDB(dimension=384)

# Insert vectors with metadata
db.insert(
    vector=[0.1, 0.2, 0.3, ...],
    metadata={"text": "Hello world", "category": "greeting"}
)

# Search for similar vectors
results = db.search(query_vector=[0.1, 0.2, 0.3, ...], top_k=5)

# Save and load
db.save("my_database.ezdb")
db = EzDB.load("my_database.ezdb")
```

### REST API Server (Network Access)

**Start Server:**
```bash
pip install -r requirements-server.txt
python -m uvicorn ezdb.server.app:app --host 0.0.0.0 --port 8000
```

**Use Client:**
```python
from ezdb.client import EzDBClient

client = EzDBClient("http://localhost:8000")
client.insert(vector=[0.1, 0.2, 0.3, ...], metadata={"text": "Hello"})
results = client.search(vector=[0.1, 0.2, 0.3, ...], top_k=5)
```

**Interactive API Docs:** http://localhost:8000/docs

See [API.md](API.md) for complete API documentation.

## Architecture

- **Storage Engine**: Efficient in-memory vector storage with metadata
- **Indexing**: HNSW (Hierarchical Navigable Small World) for fast ANN search
- **Similarity**: Cosine, Euclidean, and Dot Product metrics
- **Persistence**: JSON-based serialization for easy inspection

## Use Cases

- Semantic search
- Recommendation systems
- RAG (Retrieval Augmented Generation)
- Document similarity
- Image search
- Anomaly detection
