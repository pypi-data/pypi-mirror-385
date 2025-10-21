# Publishing Guide for SAM Mask CLI

This guide covers how to publish the SAM Mask CLI package to PyPI using `uv`.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) installed
- PyPI account (create at [pypi.org](https://pypi.org/account/register/))
- TestPyPI account (create at [test.pypi.org](https://test.pypi.org/account/register/))
- API tokens for both PyPI and TestPyPI

## Setup API Tokens

### 1. Create PyPI API Tokens

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Click "Add API token"
3. Give it a name like "sam-mask-cli"
4. Set scope to "Entire account" (or specific project if it exists)
5. Copy the token (starts with `pypi-`)

### 2. Create TestPyPI API Token

1. Go to [TestPyPI Account Settings](https://test.pypi.org/manage/account/)
2. Follow the same steps as above

### 3. Configure Credentials

Create or update `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-actual-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-actual-testpypi-token-here
```

## Pre-Publishing Checklist

### 1. Version Management

Update version in `pyproject.toml`:

```toml
[project]
name = "sam-mask-cli"
version = "0.1.1"  # Increment this
```

Follow [Semantic Versioning](https://semver.org/):
- **PATCH** (0.1.0 → 0.1.1): Bug fixes
- **MINOR** (0.1.0 → 0.2.0): New features, backward compatible
- **MAJOR** (0.1.0 → 1.0.0): Breaking changes

### 2. Update Documentation

- Update `README.md` with new features/changes
- Update `CHANGELOG.md` (if you have one)
- Ensure all examples in documentation work

### 3. Quality Checks

Run all quality checks:

```bash
make check-all
```

Or manually:

```bash
uv run black --check sam_mask_cli/
uv run isort --check sam_mask_cli/
uv run mypy sam_mask_cli/
uv run flake8 sam_mask_cli/
```

### 4. Test Installation

Test the package works correctly:

```bash
# Clean install in new environment
rm -rf .venv dist/ *.egg-info
uv venv
uv pip install -e .
sam-mask-cli --version
make run-example
```

## Publishing Process

### Step 1: Clean and Build

```bash
make clean
make build
```

Or manually:

```bash
rm -rf dist/ *.egg-info
uv build
```

### Step 2: Verify Build Contents

Check what's in the distribution:

```bash
tar -tzf dist/sam-mask-cli-*.tar.gz
unzip -l dist/sam_mask_cli-*-py3-none-any.whl
```

### Step 3: Test on TestPyPI First

Install twine if not already available:

```bash
uv tool install twine
```

Upload to TestPyPI:

```bash
uv tool run twine upload --repository testpypi dist/*
```

### Step 4: Test Installation from TestPyPI

Test installing from TestPyPI in a fresh environment:

```bash
# Create fresh environment
python -m venv test_env
source test_env/bin/activate  # On Unix/macOS
# test_env\Scripts\activate   # On Windows

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ sam-mask-cli

# Test it works
sam-mask-cli --version
```

### Step 5: Publish to PyPI

If TestPyPI installation worked correctly:

```bash
uv tool run twine upload dist/*
```

### Step 6: Verify PyPI Publication

1. Check the package page: `https://pypi.org/project/sam-mask-cli/`
2. Test installation: `pip install sam-mask-cli`
3. Verify functionality: `sam-mask-cli --version`

## Post-Publication

### 1. Create Git Tag

Tag the release in your repository:

```bash
git tag v0.1.1
git push origin v0.1.1
```

### 2. GitHub Release (Optional)

If using GitHub, create a release:
1. Go to your repository
2. Click "Releases" → "Create a new release"
3. Tag version: `v0.1.1`
4. Release title: `SAM Mask CLI v0.1.1`
5. Describe the changes
6. Attach the wheel file if desired

### 3. Update Development Version

Consider updating to a development version:

```toml
[project]
version = "0.1.2.dev0"
```

## Using Make Commands

The Makefile provides shortcuts for common publishing tasks:

```bash
# Build the package
make build

# Publish to TestPyPI
make publish-test

# Publish to PyPI
make publish

# Clean build artifacts
make clean
```

## Troubleshooting

### Common Issues

**Authentication errors:**
- Verify API tokens are correct
- Check `~/.pypirc` configuration
- Ensure tokens have correct permissions

**Package name conflicts:**
- Choose a unique package name
- Check availability on PyPI before building

**Version conflicts:**
- Increment version number in `pyproject.toml`
- You cannot overwrite existing versions on PyPI

**Build failures:**
- Check `pyproject.toml` syntax with `uv build --verbose`
- Ensure all required files are included
- Verify MANIFEST.in includes necessary files

**Import errors after installation:**
- Check package structure matches `pyproject.toml`
- Ensure `__init__.py` files are present
- Verify entry points are correctly defined

### Debug Commands

Check package metadata:

```bash
uv tool run twine check dist/*
```

Verbose build output:

```bash
uv build --verbose
```

List package contents:

```bash
python -c "import sam_mask_cli; print(sam_mask_cli.__file__)"
```

## Best Practices

### Before Each Release

1. **Test thoroughly** - Run the CLI with various inputs
2. **Update version** - Follow semantic versioning
3. **Document changes** - Update README and changelog
4. **Clean build** - Always build from clean state
5. **Test on TestPyPI first** - Catch issues before production

### Security

- Never commit API tokens to version control
- Use project-scoped tokens when possible
- Regularly rotate API tokens
- Keep `~/.pypirc` permissions restricted (`chmod 600`)

### Automation

Consider setting up GitHub Actions for automated publishing:

1. On tag push, automatically build and test
2. On release creation, automatically publish to PyPI
3. Run quality checks on all pull requests

## Quick Reference

```bash
# Complete publishing workflow
make clean
make build
make publish-test    # Test on TestPyPI first
make publish        # Publish to PyPI

# Manual workflow
uv build
uv tool run twine upload --repository testpypi dist/*
uv tool run twine upload dist/*
```

## Support

For publishing issues:
1. Check [PyPI Help](https://pypi.org/help/)
2. Review [twine documentation](https://twine.readthedocs.io/)
3. Check [uv documentation](https://github.com/astral-sh/uv)