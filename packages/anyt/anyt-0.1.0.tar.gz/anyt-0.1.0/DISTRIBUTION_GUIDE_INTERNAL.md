# AnyTask CLI - Internal Distribution Guide for AnyTransformer Inc

## 🏢 License & Distribution Policy

**Software**: AnyTask CLI (`anyt`)  
**Owner**: AnyTransformer Inc  
**License**: Proprietary (see LICENSE file)

### What You Can Do:
✅ Distribute compiled binaries (wheel files) to clients/partners  
✅ Install and use internally within AnyTransformer  
✅ Share with authorized users  

### What You Cannot Do:
❌ Make source code public  
❌ Publish to public PyPI  
❌ Share source code with unauthorized parties  
❌ Make GitHub repository public  

## 📦 Recommended Distribution Methods

### Method 1: Private Package Repository (Best for Scale)

Set up a private Python package index:

#### AWS CodeArtifact (Recommended)
```bash
# Setup (one-time)
aws codeartifact create-repository \
  --domain anytransformer \
  --repository anyt-cli \
  --description "AnyTask CLI internal repository"

# Configure authentication
aws codeartifact login \
  --tool pip \
  --domain anytransformer \
  --repository anyt-cli

# Publish
aws codeartifact login --tool twine ...
twine upload --repository codeartifact dist/*

# Users install
pip install anyt --index-url https://anytransformer-<id>.d.codeartifact.us-east-1.amazonaws.com/pypi/anyt-cli/simple/
```

#### Azure Artifacts
```bash
# Setup
az artifacts universal publish \
  --organization https://dev.azure.com/anytransformer \
  --feed anyt-cli \
  --name anyt \
  --version 0.1.0 \
  --path dist/

# Users install
pip install anyt --index-url https://pkgs.dev.azure.com/anytransformer/_packaging/anyt-cli/pypi/simple/
```

#### Google Artifact Registry
```bash
# Setup
gcloud artifacts repositories create anyt-cli \
  --repository-format=python \
  --location=us-central1

# Publish
gcloud artifacts print-settings python --repository=anyt-cli
twine upload --repository-url https://us-central1-python.pkg.dev/anytransformer/anyt-cli/ dist/*

# Users install
pip install anyt --index-url https://us-central1-python.pkg.dev/anytransformer/anyt-cli/simple/
```

### Method 2: Private GitHub Releases (Simple)

```bash
# 1. Ensure repository is PRIVATE
# Verify at: https://github.com/anytransformer/AnyTaskBackend/settings

# 2. Create release
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# 3. Create GitHub Release
# - Go to: https://github.com/anytransformer/AnyTaskBackend/releases/new
# - Tag: v0.1.0
# - Title: AnyTask CLI v0.1.0
# - Description: Internal release for AnyTransformer team
# - Attach: dist/anyt-0.1.0-py3-none-any.whl

# 4. Share with authorized users
# Users need GitHub authentication (PAT or SSH)
# Install with:
pip install https://<PAT>@github.com/anytransformer/AnyTaskBackend/releases/download/v0.1.0/anyt-0.1.0-py3-none-any.whl
```

### Method 3: Internal File Server (Quick)

```bash
# Upload to company file server
scp dist/anyt-0.1.0-py3-none-any.whl internal-server:/shared/software/anyt/

# Or use cloud storage
aws s3 cp dist/anyt-0.1.0-py3-none-any.whl s3://anytransformer-internal/software/anyt/
gsutil cp dist/anyt-0.1.0-py3-none-any.whl gs://anytransformer-internal/software/anyt/

# Users download and install
pip install /shared/software/anyt/anyt-0.1.0-py3-none-any.whl
# or
pip install https://s3.amazonaws.com/anytransformer-internal/software/anyt/anyt-0.1.0-py3-none-any.whl
```

### Method 4: Direct Distribution via Slack/Email (Ad-hoc)

```bash
# Just share the wheel file:
dist/anyt-0.1.0-py3-none-any.whl

# Via Slack:
# - Upload to #engineering or #tools channel
# - Include installation instructions

# Via Email:
# - Attach wheel file
# - Include installation instructions below
```

## 📋 Installation Instructions for End Users

Share these instructions with internal users or clients:

### For Internal AnyTransformer Team

```bash
# Option A: From private package repository (if set up)
pip install anyt --index-url https://[your-private-pypi-url]/simple/

# Option B: From downloaded wheel file
pip install anyt-0.1.0-py3-none-any.whl

# Option C: Using pipx (recommended for CLI tools)
pipx install anyt-0.1.0-py3-none-any.whl

# Verify installation
anyt --version
anyt --help
```

### For External Clients/Partners

```bash
# Install from provided wheel file
pip install anyt-0.1.0-py3-none-any.whl

# Or using pipx (recommended)
pipx install anyt-0.1.0-py3-none-any.whl

# Configure
anyt env add production https://api.anytransformer.com

# Authenticate (with provided key)
anyt auth login --agent-key <provided-key>

# Start using
anyt --help
```

## 🔐 Security Best Practices

### 1. Access Control
- Keep GitHub repository PRIVATE
- Use private package repositories with authentication
- Control access via IAM/RBAC
- Use Personal Access Tokens (PAT) for GitHub access

### 2. Distribution
- Only share wheel files, never source code
- Use signed releases (optional)
- Track who has access
- Revoke access when needed

### 3. Versioning
- Tag all releases: `v0.1.0`, `v0.2.0`, etc.
- Maintain CHANGELOG.md
- Communicate updates to users

## 🚀 Release Process for AnyTransformer Team

### 1. Prepare Release

```bash
cd /Users/bsheng/work/AnyTaskBackend

# Update version in:
# - pyproject.toml
# - src/cli/__init__.py

# Update CHANGELOG.md with changes

# Commit
git add .
git commit -m "Release v0.1.1"
```

### 2. Build

```bash
# Clean and build
rm -rf dist/
uv build

# Verify build
ls -lh dist/
# Should see:
# - anyt-0.1.1-py3-none-any.whl
# - anyt-0.1.1.tar.gz
```

### 3. Test

```bash
# Test installation
pip install dist/anyt-0.1.1-py3-none-any.whl --force-reinstall

# Verify
anyt --version
anyt --help

# Run smoke tests
anyt env list
```

### 4. Distribute

Choose one of the methods above:

```bash
# Method 1: Private package repo
twine upload --repository-url <private-repo-url> dist/*

# Method 2: GitHub Release
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1
# Create release on GitHub and attach wheels

# Method 3: File server
scp dist/anyt-0.1.1-py3-none-any.whl internal-server:/shared/software/anyt/

# Method 4: Slack/Email
# Upload dist/anyt-0.1.1-py3-none-any.whl to Slack #releases channel
```

### 5. Announce

Send announcement via:
- Slack (#releases, #engineering)
- Email to team
- Update internal wiki/docs

Template:
```
🎉 AnyTask CLI v0.1.1 Released

Changes:
- [List major changes from CHANGELOG.md]

Installation:
pip install anyt-0.1.1-py3-none-any.whl
# or download from [location]

Documentation:
https://internal-wiki.anytransformer.com/tools/anyt

Questions? Ask in #anyt-support
```

## 📊 Tracking Distribution

### Internal Users
- Track via private package repository download stats
- Monitor GitHub release downloads (for private repos)
- Survey team usage

### External Clients
- Maintain list of authorized users/organizations
- Track wheel file distribution
- Monitor API key usage (backend metrics)
- Collect feedback

## 🆘 Support

### For Internal Team
- Slack: #anyt-support
- Email: engineering@anytransformer.com
- Wiki: https://wiki.anytransformer.com/tools/anyt

### For External Clients
- Email: support@anytransformer.com
- Documentation: https://anytransformer.com/docs/cli

## 🔄 Updating Users

When releasing new versions:

1. **Notify users** via appropriate channel
2. **Provide update instructions**:
   ```bash
   pip install --upgrade anyt-0.1.1-py3-none-any.whl
   # or from private repo:
   pip install --upgrade anyt --index-url <private-repo-url>
   ```
3. **Document breaking changes** in CHANGELOG.md
4. **Provide migration guide** if needed

## ⚠️ Important Reminders

- ❌ DO NOT publish to public PyPI (pypi.org)
- ❌ DO NOT make GitHub repository public
- ❌ DO NOT share source code with unauthorized parties
- ✅ ONLY distribute compiled wheel files
- ✅ MAINTAIN access control
- ✅ TRACK distribution to external parties

## 📞 Questions?

Contact:
- **Technical**: engineering@anytransformer.com
- **Legal/Licensing**: legal@anytransformer.com
- **Business/Partnerships**: partnerships@anytransformer.com

