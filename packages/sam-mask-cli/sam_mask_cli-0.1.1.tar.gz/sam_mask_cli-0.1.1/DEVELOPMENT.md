# Development Guide for SAM Mask CLI

This guide covers development workflow using `uv` for package management and publishing.

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Development Setup

### 1. Install in Development Mode

Install the package in editable mode with all dependencies:

```bash
uv pip install -e .
```

Install with development dependencies:

```bash
uv pip install -e ".[dev]"
```

### 2. Sync Dependencies

To ensure all dependencies are up to date:

```bash
uv pip sync uv.lock
```

### 3. Add New Dependencies

Add a runtime dependency:

```bash
uv add numpy
```

Add a development dependency:

```bash
uv add --dev pytest
```

## Development Workflow

### Running the CLI During Development

After installing in development mode, you can run the CLI directly:

```bash
sam-mask-cli input.jpg "100,50,300,250" output/ mask.png
```

Or run the module directly:

```bash
python -m sam_mask_cli.cli input.jpg "100,50,300,250" output/ mask.png
```

### Code Quality Tools

Run formatting with black:

```bash
uv run black sam_mask_cli/
```

Run import sorting:

```bash
uv run isort sam_mask_cli/
```

Run type checking:

```bash
uv run mypy sam_mask_cli/
```

Run linting:

```bash
uv run flake8 sam_mask_cli/
```

### Testing

Run tests (when implemented):

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=sam_mask_cli
```

## Building and Publishing

### 1. Build the Package

Build wheel and source distribution:

```bash
uv build
```

This creates files in the `dist/` directory:
- `sam_mask_cli-0.1.0-py3-none-any.whl`
- `sam_mask_cli-0.1.0.tar.gz`

### 2. Check the Build

Verify the package contents:

```bash
tar -tzf dist/sam-mask-cli-0.1.0.tar.gz
```

### 3. Test the Built Package

Test installation from the built wheel:

```bash
uv pip install dist/sam_mask_cli-0.1.0-py3-none-any.whl
```

### 4. Publish to PyPI

First, install twine if not already available:

```bash
uv tool install twine
```

Upload to TestPyPI first (recommended):

```bash
uv tool run twine upload --repository testpypi dist/*
```

Upload to PyPI:

```bash
uv tool run twine upload dist/*
```

## Environment Management

### Create a New Virtual Environment

```bash
uv venv
```

### Activate the Environment

```bash
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

### Install Project in Clean Environment

```bash
uv pip install -e .
```

## Updating Dependencies

### Update All Dependencies

```bash
uv lock --upgrade
```

### Update Specific Dependencies

```bash
uv lock --upgrade-package numpy
```

## Release Workflow

1. **Update Version**: Update version in `pyproject.toml`

2. **Update Changelog**: Document changes (if you have a CHANGELOG.md)

3. **Run Tests**: Ensure all tests pass
   ```bash
   uv run pytest
   ```

4. **Code Quality Check**: Run all linting tools
   ```bash
   uv run black --check sam_mask_cli/
   uv run isort --check sam_mask_cli/
   uv run mypy sam_mask_cli/
   uv run flake8 sam_mask_cli/
   ```

5. **Build Package**: 
   ```bash
   uv build
   ```

6. **Test Package**: Install and test the built package
   ```bash
   uv pip install dist/sam_mask_cli-*.whl
   sam-mask-cli --version
   ```

7. **Publish**: Upload to PyPI
   ```bash
   uv tool run twine upload dist/*
   ```

## Useful uv Commands

### Project Information

```bash
uv pip list                    # List installed packages
uv pip show sam-mask-cli      # Show package information
uv pip check                  # Check for dependency conflicts
```

### Dependency Management

```bash
uv add package-name           # Add runtime dependency
uv add --dev package-name     # Add development dependency
uv remove package-name        # Remove dependency
uv lock                       # Generate lock file
uv sync                       # Install from lock file
```

### Running Scripts

```bash
uv run python script.py       # Run Python script in project environment
uv run --with package cmd     # Run command with additional package
```

## Troubleshooting

### Common Issues

**Import errors after installation:**
- Ensure you're using the correct environment
- Try reinstalling: `uv pip install --force-reinstall -e .`

**Build failures:**
- Check `pyproject.toml` syntax
- Ensure all required files are included in MANIFEST.in

**Publishing errors:**
- Verify PyPI credentials
- Check package name availability
- Ensure version number is incremented

### Clean Reset

To start fresh:

```bash
rm -rf .venv dist/ *.egg-info
uv venv
uv pip install -e .
```

### Model Cache Management

SAM models are automatically cached to avoid polluting working directories:

**Cache Location:**
- Linux/macOS: `~/.cache/ultralytics/`
- Windows: `%USERPROFILE%\.cache\ultralytics\`

**Benefits:**
- Models shared across all installations (pip, pipx, uvx)
- No `.pt` files in your working directory
- Faster subsequent runs after initial download

**Clear Model Cache (if needed):**
```bash
rm -rf ~/.cache/ultralytics/
```

## Configuration Files

- `pyproject.toml` - Package configuration and dependencies
- `uv.lock` - Locked dependency versions (commit this)
- `.python-version` - Python version specification
- `MANIFEST.in` - Additional files to include in distribution

## Best Practices

1. Always use `uv.lock` for reproducible builds
2. Test builds in clean environments before publishing
3. Use semantic versioning (MAJOR.MINOR.PATCH)
4. Keep development dependencies separate from runtime dependencies
5. Run code quality tools before committing
6. Test the CLI functionality after each change