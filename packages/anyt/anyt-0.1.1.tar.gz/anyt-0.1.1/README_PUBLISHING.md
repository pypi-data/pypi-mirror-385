# Publishing Summary for AnyTask CLI

## ✅ What We've Done

Your `anyt` CLI is now ready for distribution! Here's what's been set up:

### 1. **Package Configuration** (`pyproject.toml`)
   - ✅ Changed package name from `backend` to `anyt`
   - ✅ Added proper metadata (description, keywords, classifiers)
   - ✅ Added project URLs (homepage, docs, issues)
   - ✅ Configured entry point: `anyt` command
   - ✅ Added optional dependencies for CLI-only installation
   - ✅ Set up build system (hatchling)

### 2. **Legal & Documentation**
   - ✅ `LICENSE` - MIT License
   - ✅ `CHANGELOG.md` - Version history
   - ✅ `PUBLISHING.md` - Complete publishing guide
   - ✅ `INSTALL.md` - Installation instructions for users
   - ✅ `QUICKSTART.md` - 5-minute getting started guide
   - ✅ `MANIFEST.in` - Package manifest for source distributions

### 3. **Build Scripts**
   - ✅ `scripts/publish.sh` - Automated publishing workflow
   - ✅ `scripts/install_local.sh` - Local testing script

### 4. **Build System**
   - ✅ Successfully builds wheel: `anyt-0.1.0-py3-none-any.whl`
   - ✅ Successfully builds source dist: `anyt-0.1.0.tar.gz`
   - ✅ CLI entry point works correctly

## 🚀 How to Publish (Step by Step)

### Option 1: Quick Publish (Using the Script)

```bash
cd /Users/bsheng/work/AnyTaskBackend

# Run the publishing script
./scripts/publish.sh

# Follow the prompts:
# 1. Choose TestPyPI for testing
# 2. Choose PyPI for production
# 3. Choose Skip to just build
```

### Option 2: Manual Publish

```bash
cd /Users/bsheng/work/AnyTaskBackend

# 1. Update version numbers
# Edit: pyproject.toml and src/cli/__init__.py
# Bump version: 0.1.0 -> 0.1.1

# 2. Update CHANGELOG.md
# Add new version entry with changes

# 3. Run tests
make test
make lint

# 4. Build packages
rm -rf dist/
uv build

# 5. Test on TestPyPI
uv run twine upload --repository testpypi dist/*
# Enter credentials when prompted

# 6. Test installation
pip install --index-url https://test.pypi.org/simple/ anyt==0.1.1
anyt --help

# 7. Publish to PyPI
uv run twine upload dist/*

# 8. Create Git tag
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1

# 9. Create GitHub Release
# Go to https://github.com/yourusername/AnyTaskBackend/releases/new
# - Tag: v0.1.1
# - Title: AnyTask CLI v0.1.1
# - Description: Copy from CHANGELOG.md
# - Attach: dist/anyt-0.1.1-py3-none-any.whl and .tar.gz
```

## 📦 What Gets Published

Your package will be available on PyPI as:
- **Package name**: `anyt`
- **Command**: `anyt`
- **Homepage**: https://pypi.org/project/anyt/

Users can install it with:
```bash
pip install anyt
# or
pipx install anyt  # recommended for CLI tools
```

## 🧪 Testing Before Publishing

### Test Local Build

```bash
# Install from local wheel
cd /Users/bsheng/work/AnyTaskBackend
pip install dist/anyt-0.1.0-py3-none-any.whl

# Test it works
anyt --help
anyt env --help

# Uninstall
pip uninstall anyt
```

### Test on TestPyPI

```bash
# Upload to TestPyPI
uv run twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ anyt

# Test
anyt --help

# Uninstall
pip uninstall anyt
```

## 📋 Pre-Publishing Checklist

Before publishing to production PyPI:

- [ ] Version number updated in `pyproject.toml` and `src/cli/__init__.py`
- [ ] `CHANGELOG.md` updated with new version
- [ ] All tests passing: `make test`
- [ ] Linters passing: `make lint format`
- [ ] Documentation updated (README, CLI_USAGE.md)
- [ ] Built successfully: `uv build`
- [ ] Tested on TestPyPI
- [ ] Git committed: `git commit -am "Release v0.1.1"`
- [ ] Git tagged: `git tag v0.1.1`
- [ ] Pushed to GitHub: `git push && git push --tags`

## 🔐 Setting Up PyPI Credentials

### Create API Tokens

1. **PyPI**:
   - Go to https://pypi.org/manage/account/token/
   - Create new token with "Upload packages" permission
   - Save token securely

2. **TestPyPI** (for testing):
   - Go to https://test.pypi.org/manage/account/token/
   - Create new token
   - Save token securely

### Configure Credentials

#### Option 1: Use `.pypirc` file

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgENdGVzdC5weXBp...
```

Secure it:
```bash
chmod 600 ~/.pypirc
```

#### Option 2: Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-AgEIcHlwaS5vcmc..."
export TWINE_REPOSITORY="pypi"
```

#### Option 3: Pass credentials directly

```bash
uv run twine upload \
  --username __token__ \
  --password pypi-AgEIcHlwaS5vcmc... \
  dist/*
```

## 🤖 Automate with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    name: Build and publish to PyPI
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
```

Add PyPI token to GitHub:
1. Go to repository Settings → Secrets → Actions
2. Add new secret: `PYPI_TOKEN`
3. Paste your PyPI API token

Now publishing is automatic when you create a GitHub Release!

## 📊 After Publishing

Once published, your package will appear at:
- **PyPI**: https://pypi.org/project/anyt/
- **Install stats**: https://pypistats.org/packages/anyt

Monitor:
- Download statistics
- Issues and bug reports
- User feedback

## 🎯 Next Steps

1. **Test current build locally**:
   ```bash
   ./scripts/install_local.sh
   ```

2. **Update metadata** in `pyproject.toml`:
   - Replace "Your Name" with your actual name
   - Replace "your.email@example.com" with your email
   - Replace GitHub URLs with your actual repository URLs

3. **Create TestPyPI account**:
   - Sign up at https://test.pypi.org/

4. **Test publish to TestPyPI**:
   ```bash
   ./scripts/publish.sh
   # Choose option 1 (TestPyPI)
   ```

5. **Create PyPI account**:
   - Sign up at https://pypi.org/

6. **Publish to production**:
   ```bash
   ./scripts/publish.sh
   # Choose option 2 (PyPI)
   ```

7. **Announce**:
   - Create GitHub Release
   - Tweet about it
   - Post on relevant forums/communities
   - Update documentation

## 📚 Additional Resources

- **Python Packaging Guide**: https://packaging.python.org/
- **PyPI Help**: https://pypi.org/help/
- **Twine Documentation**: https://twine.readthedocs.io/
- **Semantic Versioning**: https://semver.org/

## 🆘 Common Issues

### Issue: "Package already exists"
**Solution**: Increment version number and rebuild.

### Issue: "Invalid credentials"
**Solution**: Regenerate API token and update `.pypirc`.

### Issue: "File size too large"
**Solution**: Add files to `.gitignore` and MANIFEST.in exclude list.

### Issue: "Missing dependencies"
**Solution**: Ensure all dependencies are listed in `pyproject.toml`.

### Issue: "Build fails"
**Solution**: Check build system in pyproject.toml, ensure all source files are included.

## 🎉 Congratulations!

Your CLI is now ready to be shared with the world! Users will be able to install it with just:

```bash
pipx install anyt
```

Good luck with your project! 🚀

