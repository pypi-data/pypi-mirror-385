# GitHub Actions Setup Guide

This guide explains how to configure GitHub Actions for automatic testing, building, and publishing your Python package to PyPI.

## 🔐 Required Secrets

You need to configure the following secrets in your GitHub repository:

### 1. PyPI API Token (Production)
- **Secret Name**: `PYPI_API_TOKEN`
- **How to get it**:
  1. Go to [https://pypi.org/manage/account/](https://pypi.org/manage/account/)
  2. Scroll down to "API tokens" section
  3. Click "Add API token"
  4. Give it a name like "slack-block-kit-builder-github"
  5. Set scope to "Entire account" (or create a project-specific token)
  6. Copy the token (starts with `pypi-`)

### 2. TestPyPI API Token (Testing)
- **Secret Name**: `TEST_PYPI_API_TOKEN`
- **How to get it**:
  1. Go to [https://test.pypi.org/manage/account/](https://test.pypi.org/manage/account/)
  2. Create an account if you don't have one
  3. Follow the same steps as above for PyPI
  4. Copy the TestPyPI token

## 🚀 How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the exact names above

## 📋 Workflow Triggers

The workflow will run automatically on:

### 🧪 Testing (Every Push/PR)
- **Trigger**: Push to any branch, Pull Requests
- **Actions**: 
  - Run tests on Python 3.8, 3.9, 3.10, 3.11, 3.12
  - Run linting (ruff)
  - Run type checking (mypy)
  - Run test suite (pytest)
  - Upload coverage reports

### 🏗️ Build (Main Branch/Releases)
- **Trigger**: Push to `main` branch, Release published
- **Actions**:
  - Build package (wheel + source distribution)
  - Check package integrity
  - Upload build artifacts

### 📦 Publish to TestPyPI (Develop Branch/PRs)
- **Trigger**: Push to `develop` branch, Pull Requests
- **Actions**:
  - Publish to TestPyPI for testing
  - Verify package can be installed

### 🚀 Publish to PyPI (Main Branch/Releases)
- **Trigger**: Push to `main` branch, Release published
- **Actions**:
  - Publish to production PyPI
  - Verify installation works

## 🔄 Release Process

### Automatic Release (Recommended)
1. **Create a release**:
   - Go to your repository on GitHub
   - Click **Releases** → **Create a new release**
   - Choose a tag (e.g., `v0.1.0`)
   - Add release notes
   - Click **Publish release**

2. **Workflow automatically**:
   - Runs all tests
   - Builds the package
   - Publishes to PyPI
   - Verifies installation

### Manual Release
1. **Push to main branch**:
   ```bash
   git push origin main
   ```
2. **Workflow automatically**:
   - Runs tests and builds
   - Publishes to PyPI

## 🛠️ Local Testing

You can test the workflow locally:

```bash
# Install act (GitHub Actions runner)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Test the workflow
act -j test
act -j build
```

## 📊 Workflow Status

- **Green checkmark** ✅: All tests passed, ready for release
- **Red X** ❌: Tests failed, fix issues before releasing
- **Yellow circle** 🟡: Workflow in progress

## 🔧 Troubleshooting

### Common Issues

1. **"Secret not found"**:
   - Check secret names are exactly: `PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN`
   - Ensure secrets are added to the correct repository

2. **"Package already exists"**:
   - Update version in `pyproject.toml`
   - Create a new release with new version

3. **"Tests failing"**:
   - Check the Actions tab for detailed error logs
   - Fix issues locally first
   - Push fixes to trigger new workflow run

### Debug Commands

```bash
# Check package locally
python -m build
twine check dist/*

# Test installation
pip install dist/slack_block_kit_builder-*.whl

# Verify package works
python -c "from slack_block_kit_builder import Message; print('Success!')"
```

## 📈 Benefits

- **Automated Testing**: Every change is tested across Python versions
- **Quality Assurance**: Linting, type checking, and coverage reports
- **Easy Releases**: One-click releases to PyPI
- **Rollback Safety**: TestPyPI for testing before production
- **Visibility**: Clear status indicators for contributors

## 🎯 Next Steps

1. **Add the secrets** to your GitHub repository
2. **Push your code** to trigger the first workflow run
3. **Create a release** to publish to PyPI
4. **Monitor the Actions tab** for workflow status

Your package will be automatically available on PyPI after a successful release! 🚀
