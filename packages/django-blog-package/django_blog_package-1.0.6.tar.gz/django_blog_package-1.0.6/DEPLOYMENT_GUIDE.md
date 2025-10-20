# Django Blog Package - Deployment Guide

This guide explains how to use the enhanced deployment script for publishing new versions of the Django Blog Package to PyPI.

## Overview

The deployment script (`deploy_to_pypi.sh`) provides automatic version management with support for major, minor, and patch version increments. It handles the entire deployment process including version updates, package building, verification, and PyPI upload.

## Quick Start

### Basic Usage (Auto-increment patch version)
```bash
./deploy_to_pypi.sh
```

This will:
- Auto-increment the patch version (e.g., 1.0.5 → 1.0.6)
- Update both `setup.py` and `pyproject.toml`
- Build the package distributions
- Verify the package integrity
- Upload to PyPI (after confirmation)

## Installation Requirements

Before using the deployment script, ensure you have:

1. **Python packages**:
   ```bash
   pip install twine wheel setuptools
   ```

2. **PyPI credentials**:
   - Create a `.pypirc` file in your home directory with your PyPI credentials
   - Or use environment variables for authentication

3. **Script permissions**:
   ```bash
   chmod +x deploy_to_pypi.sh
   ```

## Command Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--major` | `-m` | Increment major version (X.0.0) | `1.0.5 → 2.0.0` |
| `--minor` | `-n` | Increment minor version (0.X.0) | `1.0.5 → 1.1.0` |
| `--patch` | `-p` | Increment patch version (0.0.X) | `1.0.5 → 1.0.6` |
| `--dry-run` | `-d` | Build and verify without uploading | `./deploy_to_pypi.sh -d` |
| `--force` | `-f` | Skip confirmation prompts | `./deploy_to_pypi.sh -f` |
| `--help` | `-h` | Show help message | `./deploy_to_pypi.sh -h` |

## Version Management

### Semantic Versioning

The script follows semantic versioning principles:

- **Major version (X.0.0)**: Breaking changes, incompatible API changes
- **Minor version (0.X.0)**: New features, backward-compatible
- **Patch version (0.0.X)**: Bug fixes, minor improvements, backward-compatible

### Automatic Version Detection

The script automatically detects the current version from:
1. `setup.py` (primary)
2. `pyproject.toml` (fallback)

### Version Update Examples

```bash
# Current version: 1.2.3

./deploy_to_pypi.sh           # → 1.2.4 (patch)
./deploy_to_pypi.sh --minor   # → 1.3.0 (minor)  
./deploy_to_pypi.sh --major   # → 2.0.0 (major)
./deploy_to_pypi.sh --patch   # → 1.2.4 (patch)
```

## Deployment Workflow

### 1. Pre-deployment Checklist

Before deploying, ensure:

- [ ] All tests pass: `python manage.py test blog`
- [ ] Documentation is updated
- [ ] README.md is current and comprehensive
- [ ] Version-specific changes are documented
- [ ] No sensitive data in distributions

### 2. Dry Run (Recommended)

Always test with a dry run first:

```bash
./deploy_to_pypi.sh --dry-run
```

This will:
- Show the version update that would occur
- Build the package distributions
- Verify package integrity
- **Not upload** to PyPI

### 3. Actual Deployment

```bash
# For patch releases (most common)
./deploy_to_pypi.sh

# For minor releases (new features)
./deploy_to_pypi.sh --minor

# For major releases (breaking changes)
./deploy_to_pypi.sh --major
```

### 4. Post-deployment Steps

After successful deployment:

1. **Create git tag**:
   ```bash
   git tag -a v1.0.6 -m "Release version 1.0.6"
   git push origin main --tags
   ```

2. **Update release notes** on GitHub
3. **Verify installation**:
   ```bash
   pip install django-blog-package==1.0.6
   ```

## Advanced Usage

### Force Deployment (Skip Confirmations)

```bash
./deploy_to_pypi.sh --force --minor
```

### Combined Options

```bash
# Dry run with minor version increment
./deploy_to_pypi.sh --dry-run --minor

# Force patch version update
./deploy_to_pypi.sh --force --patch
```

### Manual Version Override

If you need to set a specific version (not recommended for regular use):

1. Manually update `setup.py` and `pyproject.toml`
2. Run deployment script normally

## Troubleshooting

### Common Issues

**"setup.py or pyproject.toml not found"**
- Ensure you're running the script from the package root directory
- Verify both files exist

**"Invalid version format"**
- Check that version numbers follow `X.Y.Z` format
- Ensure no extra characters in version strings

**Twine authentication errors**
- Verify `.pypirc` file configuration
- Check PyPI API token permissions
- Ensure you're using the correct PyPI repository

**Package verification failures**
- Check for syntax errors in Python files
- Verify all required files are included in MANIFEST.in
- Ensure no binary files accidentally included

### Debug Mode

For detailed debugging, run with:

```bash
bash -x deploy_to_pypi.sh
```

## Best Practices

### Version Strategy

1. **Use patch versions** for bug fixes and minor improvements
2. **Use minor versions** for new features and enhancements
3. **Use major versions** for breaking changes only
4. **Always test** with dry run before actual deployment

### Release Frequency

- **Patch releases**: As needed for bug fixes
- **Minor releases**: Every 2-4 weeks for feature updates
- **Major releases**: Only for significant architectural changes

### Quality Assurance

- Always run tests before deployment
- Verify package builds correctly locally
- Test installation in a clean environment
- Check that all documentation files are included

## Script Features

- ✅ Automatic version detection and increment
- ✅ Support for major/minor/patch version updates
- ✅ Dry run mode for testing
- ✅ Force mode for automated deployments
- ✅ Package verification with twine check
- ✅ Git tag suggestions post-deployment
- ✅ Color-coded output for better readability
- ✅ Error handling and validation

## Security Considerations

- Never commit PyPI credentials to version control
- Use API tokens instead of passwords when possible
- Verify package contents before upload
- Keep deployment scripts in secure locations

## Support

If you encounter issues with the deployment script:

1. Check this guide for common solutions
2. Run with `--help` to see available options
3. Use dry run mode to test without uploading
4. Check the script output for specific error messages

---

**Remember**: Always test with `--dry-run` first and verify the package builds correctly before uploading to PyPI.