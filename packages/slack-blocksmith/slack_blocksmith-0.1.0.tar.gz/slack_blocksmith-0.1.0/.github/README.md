# 🚀 GitHub Actions CI/CD Pipeline

This repository includes automated CI/CD workflows for testing, building, and publishing the `slack-block-kit-builder` package to PyPI.

## 📁 Workflow Files

### 1. **Test Workflow** (`.github/workflows/test.yml`)
- **Triggers**: Push to any branch, Pull Requests
- **Purpose**: Run tests, linting, type checking, and build verification
- **No secrets required** ✅

### 2. **Release Workflow** (`.github/workflows/release.yml`)
- **Triggers**: GitHub Release published
- **Purpose**: Publish to PyPI automatically
- **Requires**: `PYPI_API_TOKEN` secret

### 3. **Full CI/CD Workflow** (`.github/workflows/ci-cd.yml`)
- **Triggers**: Push to main/develop, Pull Requests, Releases
- **Purpose**: Complete testing and publishing pipeline
- **Requires**: `PYPI_API_TOKEN` and `TEST_PYPI_API_TOKEN` secrets

## 🎯 Quick Start

### Option 1: Test Only (Recommended for first setup)
1. **Push your code** - The test workflow will run automatically
2. **Check the Actions tab** - See test results
3. **Fix any issues** - Push again to re-run tests

### Option 2: Full Automation
1. **Add PyPI secrets** (see setup guide below)
2. **Create a release** - Automatically publishes to PyPI
3. **Your package is live!** 🎉

## 🔐 Setup Secrets (For Publishing)

### Required Secrets:
- `PYPI_API_TOKEN` - Your PyPI API token
- `TEST_PYPI_API_TOKEN` - Your TestPyPI API token (optional)

### How to Add Secrets:
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact names above

### How to Get API Tokens:
1. **PyPI**: [https://pypi.org/manage/account/](https://pypi.org/manage/account/)
2. **TestPyPI**: [https://test.pypi.org/manage/account/](https://test.pypi.org/manage/account/)

## 📊 Workflow Status

| Workflow | Trigger | Status | Purpose |
|----------|---------|--------|---------|
| **Test** | Push/PR | ✅ Ready | Run tests, linting, type checking |
| **Release** | Release | 🔐 Needs secrets | Publish to PyPI |
| **CI/CD** | Push/PR/Release | 🔐 Needs secrets | Full pipeline |

## 🚀 Release Process

### Automatic Release (Recommended)
1. **Update version** in `pyproject.toml`
2. **Commit and push** changes
3. **Create a GitHub release**:
   - Go to **Releases** → **Create a new release**
   - Choose a tag (e.g., `v0.1.0`)
   - Add release notes
   - Click **Publish release**
4. **Workflow automatically**:
   - Runs all tests
   - Builds the package
   - Publishes to PyPI
   - Verifies installation

### Manual Release
```bash
# Update version in pyproject.toml
# Then push to main branch
git push origin main
```

## 🛠️ Local Testing

You can test the workflows locally:

```bash
# Test package build
python -m build
twine check dist/*

# Test package installation
pip install dist/slack_block_kit_builder-*.whl
python -c "from slack_block_kit_builder import Message; print('Success!')"

# Run tests
pytest --cov=slack_block_kit_builder
```

## 📈 Benefits

- **🔄 Automated Testing**: Every change tested across Python 3.8-3.12
- **🛡️ Quality Assurance**: Linting, type checking, coverage reports
- **🚀 Easy Releases**: One-click releases to PyPI
- **🔒 Safe Publishing**: TestPyPI for testing before production
- **👀 Visibility**: Clear status indicators for contributors

## 🔧 Troubleshooting

### Common Issues:

1. **"Secret not found"**:
   - Check secret names are exactly: `PYPI_API_TOKEN`
   - Ensure secrets are added to the correct repository

2. **"Package already exists"**:
   - Update version in `pyproject.toml`
   - Create a new release with new version

3. **"Tests failing"**:
   - Check the Actions tab for detailed error logs
   - Fix issues locally first
   - Push fixes to trigger new workflow run

### Debug Commands:
```bash
# Check package locally
python -m build
twine check dist/*

# Test installation
pip install dist/slack_block_kit_builder-*.whl

# Verify package works
python -c "from slack_block_kit_builder import Message; print('Success!')"
```

## 🎉 Success!

Once configured, your package will be automatically:
- ✅ Tested on every push
- 🏗️ Built and validated
- 📦 Published to PyPI on releases
- 🔍 Verified to work correctly

Your users can install it with:
```bash
pip install slack-block-kit-builder
```

## 📚 Next Steps

1. **Push your code** to trigger the first test run
2. **Add PyPI secrets** when ready to publish
3. **Create a release** to publish to PyPI
4. **Monitor the Actions tab** for workflow status

Happy publishing! 🚀
