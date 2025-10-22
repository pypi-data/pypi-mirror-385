# Release Process

This document describes the automated release process for the Privacy-Preserving Similarity Search package.

## Overview

The package uses an automated release workflow that triggers on every merge to the `main` or `master` branch. The workflow automatically:

1. Bumps the version number (patch version by default)
2. Commits the version bump
3. Creates a Git tag
4. Builds Python packages for multiple platforms and architectures
5. Creates a GitHub Release with changelogs
6. Publishes packages to PyPI (when configured)

## Automated Release Workflow

### Trigger

The release workflow runs automatically when:
- A pull request is merged into `main` or `master`
- Changes are pushed directly to `main` or `master`

### Exclusions

The workflow does NOT run when only these files change:
- Markdown files (`**.md`)
- Documentation (`docs/**`)
- GitHub workflows (except `release.yml` itself)

### Version Bumping

By default, the workflow bumps the **patch version**:
- `0.1.0` → `0.1.1`
- `0.1.1` → `0.1.2`
- etc.

#### Manual Version Bumps

To bump a different version component, use bump2version locally before merging:

```bash
# Bump minor version (0.1.0 -> 0.2.0)
bump2version minor

# Bump major version (0.1.0 -> 1.0.0)
bump2version major

# Push the changes
git push && git push --tags
```

When you merge a PR with a manual version bump, the automated workflow will still run but will bump from your new version.

## Multi-Architecture Builds

The release workflow builds wheels for:

### Operating Systems
- **Ubuntu** (Linux)
- **macOS** (Darwin)
- **Windows**

### Python Versions
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11

### Architectures
- **x86_64** (Intel/AMD 64-bit) - All platforms
- **ARM64** (Apple Silicon) - macOS
- **aarch64** (ARM 64-bit) - Linux (via cibuildwheel if needed)

This ensures the package works on:
- Intel/AMD processors
- Apple M1/M2/M3 Macs
- ARM-based cloud instances (AWS Graviton, etc.)

## Package Distribution

### Source Distribution (sdist)
- Format: `.tar.gz`
- Contains all source code
- Works on any platform with a Python compiler

### Binary Wheels (bdist_wheel)
- Format: `.whl`
- Pre-compiled for specific platforms
- Faster installation (no compilation needed)
- Built for each OS × Python version combination

## GitHub Release

Each release includes:
- **Tag**: `vX.Y.Z` (e.g., `v0.1.1`)
- **Release Notes**: Auto-generated from CHANGELOG.md
- **Assets**:
  - Source distribution (`.tar.gz`)
  - Universal wheel (`.whl`)
  - Additional architecture-specific wheels

## PyPI Publishing

### Configuration

To enable automatic PyPI publishing:

1. Create a PyPI API token:
   - Go to https://pypi.org/manage/account/token/
   - Create a new token with "Upload packages" scope
   - Copy the token (starts with `pypi-`)

2. Add token to GitHub Secrets:
   - Go to repository Settings → Secrets → Actions
   - Create new secret: `PYPI_API_TOKEN`
   - Paste your PyPI token

3. Uncomment the publishing line in `.github/workflows/release.yml`:
   ```yaml
   # Change this:
   # twine upload dist/*

   # To this:
   twine upload dist/*
   ```

### First Release

For the first release to PyPI:

1. Ensure package name is available: https://pypi.org/project/privacy-similarity/
2. Configure PyPI token (see above)
3. Merge to main - the workflow will automatically publish

### Subsequent Releases

After the first release, every merge to main automatically:
- Bumps version
- Publishes to PyPI
- Users can install with `pip install privacy-similarity`

## Installation Methods

After release, users can install in several ways:

### From PyPI (Recommended)
```bash
pip install privacy-similarity
```

### Specific Version
```bash
pip install privacy-similarity==0.1.1
```

### Latest from GitHub
```bash
pip install git+https://github.com/alexandernicholson/python-similarity.git
```

### Specific Tag
```bash
pip install git+https://github.com/alexandernicholson/python-similarity.git@v0.1.1
```

## Versioning Strategy

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Incompatible API changes
- **MINOR** (0.X.0): New features, backwards compatible
- **PATCH** (0.0.X): Bug fixes, backwards compatible

### When to Bump

- **Patch** (0.1.0 → 0.1.1):
  - Bug fixes
  - Documentation updates
  - Performance improvements
  - Internal refactoring

- **Minor** (0.1.0 → 0.2.0):
  - New features
  - New privacy modes
  - New index types
  - Deprecations (with warnings)

- **Major** (0.1.0 → 1.0.0):
  - Breaking API changes
  - Removing deprecated features
  - Major architecture changes

## Changelog Management

### Updating CHANGELOG.md

Before merging to main, update `CHANGELOG.md`:

1. Move changes from `[Unreleased]` to a new version section
2. Add date and version number
3. Categorize changes:
   - **Added**: New features
   - **Changed**: Changes to existing functionality
   - **Deprecated**: Soon-to-be removed features
   - **Removed**: Removed features
   - **Fixed**: Bug fixes
   - **Security**: Security fixes

Example:
```markdown
## [Unreleased]

## [0.1.1] - 2025-10-22

### Added
- GPU acceleration for IVF indices

### Fixed
- Memory leak in HNSW index
- Threading issue in batch processing

### Changed
- Default epsilon from 1.0 to 0.8
```

## Rollback Procedure

If a release has issues:

### 1. Yank from PyPI
```bash
pip install twine
twine register privacy-similarity
# Mark version as yanked (users can still install explicitly)
```

### 2. Create Hotfix
```bash
# Create hotfix branch
git checkout -b hotfix/0.1.2 v0.1.1

# Fix the issue
# ... make changes ...

# Bump version
bump2version patch

# Merge hotfix to main
git checkout main
git merge hotfix/0.1.2
git push
```

### 3. Delete Bad Release (if necessary)
- Go to GitHub Releases
- Delete the problematic release
- Delete the tag: `git push --delete origin vX.Y.Z`

## Testing Releases

### Test PyPI

Before publishing to PyPI, test with TestPyPI:

1. Create TestPyPI account: https://test.pypi.org/
2. Get API token
3. Upload manually:
   ```bash
   python -m build
   twine upload --repository testpypi dist/*
   ```
4. Install and test:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ privacy-similarity
   ```

### Local Testing

Test the built packages locally:

```bash
# Build packages
python -m build

# Install in fresh virtualenv
python -m venv test_env
source test_env/bin/activate
pip install dist/privacy_similarity-0.1.0-py3-none-any.whl

# Test import
python -c "from privacy_similarity import PrivacyPreservingSimilaritySearch; print('OK')"
```

## Monitoring

After each release:

1. **Check PyPI**: Verify package appears at https://pypi.org/project/privacy-similarity/
2. **Test Installation**: `pip install privacy-similarity` in clean environment
3. **Check Downloads**: Monitor download stats on PyPI
4. **Watch Issues**: Monitor for installation or compatibility issues

## Release Checklist

Before merging to main:

- [ ] All tests pass in CI
- [ ] CHANGELOG.md updated
- [ ] Version bump committed (if manual)
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Migration guide written (for major versions)
- [ ] Security implications reviewed

## Troubleshooting

### Build Fails

**Issue**: Wheel build fails for specific platform

**Solution**:
1. Check `.github/workflows/release.yml` for build matrix
2. Add platform-specific dependencies
3. Update `pyproject.toml` or `setup.py`

### PyPI Upload Fails

**Issue**: `403 Forbidden` error

**Solution**:
- Check PYPI_API_TOKEN is set correctly
- Verify token has upload permissions
- Ensure version doesn't already exist

**Issue**: Version already exists

**Solution**:
- Cannot re-upload same version to PyPI
- Bump version and try again
- Use TestPyPI for testing

### Tag Already Exists

**Issue**: Git tag already exists

**Solution**:
```bash
# Delete local tag
git tag -d v0.1.1

# Delete remote tag
git push --delete origin v0.1.1

# Recreate tag
git tag v0.1.1
git push --tags
```

## References

- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PEP 440 - Version Identification](https://www.python.org/dev/peps/pep-0440/)
