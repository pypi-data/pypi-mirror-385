# Worker Core Library

Core library for worker services in the Mesh-Sync platform.

## Overview

This is a Python library that provides shared functionality for worker services, including:
- BullMQ integration
- Storage providers (S3, Google Drive, SFTP)
- Authentication and credentials management
- Database utilities
- Common utility functions

## Installation

### From Source

```bash
pip install -e .
```

### From GitHub Container Registry (GHCR)

The Docker image is automatically built and published to GHCR:

```bash
docker pull ghcr.io/mesh-sync/worker-core-lib:latest
```

## Development

### Building Locally

Build the Python package:
```bash
pip install build
python -m build
```

Build the Docker image:
```bash
docker build -t worker-core-lib:local .
```

### Running Tests

```bash
pip install -e .
pytest
```

## CI/CD Pipeline

This repository uses GitHub Actions for continuous integration and deployment:

### Workflow: Build, Test, and Deploy to GHCR

**Location**: `.github/workflows/docker-publish.yml`

**Triggers**:
- Push to `master` or `main` branches
- Pull requests to `master` or `main` branches
- Release published

**Jobs**:
1. **Build and Test**:
   - Sets up Python 3.10 (matching Dockerfile)
   - Installs dependencies
   - Runs pytest (if tests exist)
   - Builds Python package
   - Builds Docker image
   - Pushes to GHCR (only on push/release, not PRs)

**Container Registry**: Images are published to GitHub Container Registry (GHCR) at `ghcr.io/mesh-sync/worker-core-lib`

**Tags**:
- `latest` - Latest build from default branch
- `<branch>` - Branch-specific builds
- `<branch>-<sha>` - Build with commit SHA
- `v<version>` - Semantic version tags (on releases)

### Accessing Container Images

Images are publicly available from GHCR:

```bash
# Pull latest
docker pull ghcr.io/mesh-sync/worker-core-lib:latest

# Pull specific version
docker pull ghcr.io/mesh-sync/worker-core-lib:v0.0.1

# Pull specific branch
docker pull ghcr.io/mesh-sync/worker-core-lib:master
```

## Usage

See the example in `main.py` for a complete demonstration of using the core libraries.

## License

MIT License