# PyPI Publishing Checklist

## ✅ Current Folder Structure

Your package is properly structured for PyPI publication:

```
fantasyNBALeagueMCP/
├── fantasy_nba_israel_mcp/      # Main package (note: underscores!)
│   ├── __init__.py              # Package initialization & exports
│   ├── __main__.py              # Entry point for CLI
│   └── server.py                # Main MCP server implementation
├── .gitignore                   # Git ignore file
├── LICENSE                      # MIT License
├── MANIFEST.in                  # Specifies files to include in distribution
├── PUBLISHING.md                # Publishing guide
├── pyproject.toml               # Package metadata & build configuration
├── README.md                    # Package documentation
└── uv.lock                      # UV lockfile (optional)
```

## ✅ Required Files (All Present)

- [x] `fantasy_nba_israel_mcp/__init__.py` - Exports mcp and tools
- [x] `fantasy_nba_israel_mcp/__main__.py` - CLI entry point
- [x] `fantasy_nba_israel_mcp/server.py` - Main implementation
- [x] `pyproject.toml` - Package configuration
- [x] `README.md` - Documentation
- [x] `LICENSE` - MIT License
- [x] `MANIFEST.in` - Distribution file list
- [x] `.gitignore` - Git exclusions

## 📋 Pre-Publishing Checklist

### Before First Publish

- [ ] **Update GitHub URLs** in `pyproject.toml`:
  ```toml
  [project.urls]
  Homepage = "https://github.com/YOUR_USERNAME/fantasynbaleaguemcp"
  Repository = "https://github.com/YOUR_USERNAME/fantasynbaleaguemcp"
  Issues = "https://github.com/YOUR_USERNAME/fantasynbaleaguemcp/issues"
  ```

- [ ] **Create PyPI account**: https://pypi.org/account/register/

- [ ] **Create PyPI API token**: https://pypi.org/manage/account/token/

- [ ] **Install build tools**:
  ```bash
  pip install build twine
  ```

### Before Each Publish

- [ ] **Test locally**:
  ```bash
  uv run mcp dev fantasy_nba_israel_mcp/server.py
  ```

- [ ] **Update version number** in BOTH:
  - `fantasy_nba_israel_mcp/__init__.py` → `__version__ = "0.1.X"`
  - `pyproject.toml` → `version = "0.1.X"`

- [ ] **Update CHANGELOG** (optional but recommended)

- [ ] **Clean old builds**:
  ```bash
  rm -rf dist/ build/ *.egg-info
  # or on Windows PowerShell:
  Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
  ```

- [ ] **Build package**:
  ```bash
  python -m build
  ```

- [ ] **Check package**:
  ```bash
  twine check dist/*
  ```

- [ ] **Test on TestPyPI** (recommended for first time):
  ```bash
  twine upload --repository testpypi dist/*
  pip install --index-url https://test.pypi.org/simple/ fantasynbaleaguemcp
  ```

- [ ] **Publish to PyPI**:
  ```bash
  twine upload dist/*
  ```

- [ ] **Test installation**:
  ```bash
  uvx fantasynbaleaguemcp
  ```

- [ ] **Tag release in Git**:
  ```bash
  git tag v0.1.0
  git push origin v0.1.0
  ```

## 🔧 Configuration Details

### Package Name vs Module Name

- **PyPI Package Name**: `fantasynbaleaguemcp` (no underscores/hyphens)
- **Python Module Name**: `fantasy_nba_israel_mcp` (underscores for imports)
- **Install command**: `pip install fantasynbaleaguemcp`
- **Import statement**: `from fantasy_nba_israel_mcp import mcp`

This is intentional and follows Python conventions!

### Entry Points

The package can be run in multiple ways:

1. **As MCP server** (recommended):
   ```bash
   uvx fantasynbaleaguemcp
   ```

2. **As Python module**:
   ```bash
   python -m fantasy_nba_israel_mcp
   ```

3. **Direct command** (after installation):
   ```bash
   fantasynbaleaguemcp
   ```

All three methods work because of the configuration in `pyproject.toml`:
```toml
[project.scripts]
fantasynbaleaguemcp = "fantasy_nba_israel_mcp.__main__:main"
```

## 📦 What Gets Published

The following files will be included in your PyPI distribution:

- All `.py` files in `fantasy_nba_israel_mcp/`
- `README.md`
- `LICENSE`
- `pyproject.toml`
- `PUBLISHING.md`

Excluded (via `.gitignore`):
- `__pycache__/`
- `*.pyc`
- `build/`
- `dist/`
- `.venv/`
- `.env` files

## 🚀 Quick Publish Command

```bash
# One-liner for experienced users (after version bump)
rm -rf dist/ build/ *.egg-info && python -m build && twine check dist/* && twine upload dist/*
```

## 🔒 Security Notes

- ✅ Backend URL is in source code (public, but backend should have rate limiting)
- ✅ No secrets or API keys in the code
- ✅ `.env` files are gitignored
- ✅ Users can override URL with environment variables if needed

## 📚 Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Publishing Tutorial](https://packaging.python.org/tutorials/packaging-projects/)
- [Semantic Versioning](https://semver.org/)
- [MCP Documentation](https://modelcontextprotocol.io/)

## ❓ Common Issues

### "Package already exists"
You can't use the same package name if someone else has it. Check: https://pypi.org/project/fantasynbaleaguemcp/

If taken, change the name in `pyproject.toml`:
```toml
name = "fantasy-nba-israel"  # or another unique name
```

### "File already exists"
You can't re-upload the same version. Increment version number and rebuild.

### Import errors
Make sure:
- Folder name: `fantasy_nba_israel_mcp` (underscores)
- Import: `from fantasy_nba_israel_mcp import mcp`
- Package name in PyPI: `fantasynbaleaguemcp` (can be different)

## 🎉 After Publishing

1. Share with your league:
   ```
   Hey team! Install our Fantasy NBA stats:
   
   uvx fantasynbaleaguemcp
   
   Then add to Claude Desktop config. Done! 🏀
   ```

2. Update GitHub with:
   - Release notes
   - Tag for the version
   - Updated README with install instructions

3. Monitor PyPI stats: https://pypi.org/project/fantasynbaleaguemcp/

