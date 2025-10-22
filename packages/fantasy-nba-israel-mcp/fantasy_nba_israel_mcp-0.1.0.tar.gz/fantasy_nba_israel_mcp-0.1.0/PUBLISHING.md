# Publishing to PyPI

This guide explains how to publish the Fantasy NBA League MCP package to PyPI.

## Prerequisites

1. **Create a PyPI account**
   - Go to https://pypi.org/account/register/
   - Verify your email address

2. **Create a PyPI API token**
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token with scope: "Entire account"
   - Save the token securely (you'll only see it once)

3. **Install build tools**
   ```bash
   pip install build twine
   ```

## Publishing Steps

### 1. Update Version Number

Edit `fantasy_nba_israel_mcp/__init__.py` and `pyproject.toml` to update the version:

```python
# fantasy_nba_israel_mcp/__init__.py
__version__ = "0.1.1"  # Increment version
```

```toml
# pyproject.toml
[project]
version = "0.1.1"  # Match the version in __init__.py
```

### 2. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf dist/ build/ *.egg-info

# On Windows PowerShell:
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
```

### 3. Build the Package

```bash
python -m build
```

This creates two files in the `dist/` directory:
- A source distribution (`.tar.gz`)
- A wheel distribution (`.whl`)

### 4. Check the Package

```bash
# Check that the package is valid
twine check dist/*
```

### 5. Upload to TestPyPI (Optional but Recommended)

Test your package on TestPyPI first:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Enter your TestPyPI credentials when prompted
```

Then test installing from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ fantasy-nba-israel-mcp
```

### 6. Upload to PyPI

When everything looks good:

```bash
twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

### 7. Verify Installation

```bash
# Install from PyPI
pip install fantasy-nba-israel-mcp

# Or with uvx
uvx fantasy-nba-israel-mcp
```

## Versioning Guide

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.0.0): Incompatible API changes
- **MINOR** version (0.1.0): Add functionality (backwards-compatible)
- **PATCH** version (0.0.1): Bug fixes (backwards-compatible)

## Common Issues

### "File already exists"

You can't re-upload the same version. Increment the version number and rebuild.

### Import errors after installation

Make sure:
- Package name in `pyproject.toml` matches
- Folder structure is correct
- `__init__.py` exports are correct

### Missing files in distribution

Check `MANIFEST.in` includes all necessary files:

```
include README.md
include LICENSE
include pyproject.toml
recursive-include fantasy_nba_israel_mcp *.py
```

## Automation with GitHub Actions (Optional)

Create `.github/workflows/publish.yml` to automate publishing:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Then add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`.

## Quick Reference

```bash
# Complete publishing workflow
# 1. Update version
# 2. Clean
rm -rf dist/ build/ *.egg-info

# 3. Build
python -m build

# 4. Check
twine check dist/*

# 5. Upload
twine upload dist/*
```

