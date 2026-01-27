# Contributing to llama-index-retrievers-digitalocean-gradientai

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/llama-index-retrievers-digitalocean-gradientai.git
   cd llama-index-retrievers-digitalocean-gradientai
   ```
3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

```bash
pytest
```

Integration tests require `DIGITALOCEAN_ACCESS_TOKEN` and `GRADIENT_KB_ID` environment variables and are skipped automatically if not set.

### Code Style

This project uses:
- **Black** for formatting (line length: 100)
- **Ruff** for linting
- **MyPy** for type checking

```bash
black .
ruff check . --fix
mypy llama_index/retrievers/digitalocean/gradientai
```

### Submitting Changes

1. Create a feature branch from `main`
2. Make your changes
3. Add or update tests as needed
4. Ensure all checks pass (`pytest`, `black --check .`, `ruff check .`)
5. Commit with a clear message
6. Open a pull request against `main`

## Reporting Issues

Open an issue on [GitHub Issues](https://github.com/digitalocean/llama-index-retrievers-digitalocean-gradientai/issues) with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and package versions

## Code of Conduct

Be respectful and constructive in all interactions.
