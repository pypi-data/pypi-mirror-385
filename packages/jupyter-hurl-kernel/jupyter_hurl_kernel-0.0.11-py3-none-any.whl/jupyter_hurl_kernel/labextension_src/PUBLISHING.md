# Publishing the JupyterLab Extension

This document explains how to publish the jupyterlab-hurl-extension package to npm.

## Quick Start

1. **Set up npm token** (one-time): See [../.github/NPM_SETUP.md](../.github/NPM_SETUP.md)
2. **Create a release**: Tag and create a GitHub release
3. **Automatic publishing**: GitHub Actions handles the rest

## Publishing Process

### Option 1: Automatic Publishing via GitHub Release (Recommended)

1. **Ensure all changes are committed and pushed**

2. **Create and push a version tag:**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. **Create a GitHub Release:**
   - Go to https://github.com/micedre/jupyter-hurl-kernel/releases
   - Click "Create a new release"
   - Select the tag you just created (`v0.1.0`)
   - Add release notes describing changes
   - Click "Publish release"

4. **GitHub Actions will automatically:**
   - Build the TypeScript extension
   - Update version in package.json
   - Run tests and validation
   - Publish to npm with provenance
   - Attach the built package to the release

### Option 2: Manual Workflow Trigger

1. **Go to GitHub Actions**
   - Navigate to: https://github.com/micedre/jupyter-hurl-kernel/actions
   - Select "Publish JupyterLab Extension to npm"

2. **Run the workflow:**
   - Click "Run workflow"
   - Enter the version number (e.g., `0.1.0`)
   - Click "Run workflow"

### Option 3: Manual Publishing (Development/Testing)

For testing or local publishing:

```bash
cd jupyterlab-hurl-extension

# Login to npm (one-time)
npm login

# Install dependencies
npm install

# Build the extension
npm run build:prod

# Test package creation (doesn't publish)
npm pack

# Dry run (shows what would be published)
npm publish --dry-run

# Actually publish
npm publish --access public
```

## Version Numbers

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.0.0): Incompatible API changes
- **MINOR** version (0.1.0): Add functionality (backwards compatible)
- **PATCH** version (0.0.1): Bug fixes (backwards compatible)

Examples:
- `v0.1.0` - First release
- `v0.1.1` - Bug fix
- `v0.2.0` - New feature
- `v1.0.0` - Stable release

## Pre-Release Checklist

Before publishing a new version:

- [ ] All tests pass
- [ ] Code is linted and formatted
- [ ] Documentation is updated
- [ ] CHANGELOG is updated (if you have one)
- [ ] Version number is appropriate
- [ ] No uncommitted changes
- [ ] Tested installation locally

## After Publishing

1. **Verify on npm:**
   - Check https://www.npmjs.com/package/jupyterlab-hurl-extension
   - Verify version number
   - Check package contents

2. **Test installation:**
   ```bash
   # In a fresh environment
   pip install jupyterlab
   jupyter labextension install jupyterlab-hurl-extension
   jupyter labextension list
   ```

3. **Update documentation:**
   - Update installation instructions if needed
   - Announce release in GitHub Discussions or README

## Troubleshooting

### Build Fails

Check the GitHub Actions logs for TypeScript or build errors:
```bash
cd jupyterlab-hurl-extension
npm run clean:all
npm install
npm run build:prod
```

### Permission Denied

Verify:
- `NPM_TOKEN` secret is set in GitHub
- Token has publish permissions
- You're the package owner

### Version Already Exists

npm doesn't allow republishing the same version. Either:
- Increment version number
- Use `npm unpublish` within 72 hours (not recommended)

### Package Not Found After Publishing

- Wait a few minutes for npm to propagate
- Clear npm cache: `npm cache clean --force`
- Try installing with specific version: `jupyter labextension install jupyterlab-hurl-extension@0.1.0`

## Unpublishing

⚠️ **Only use in emergencies within 72 hours of publishing**

```bash
npm unpublish jupyterlab-hurl-extension@0.1.0
```

Better approach: Publish a patched version with fixes.

## Security

- npm token is stored as GitHub secret
- Never commit tokens to repository
- Use automation tokens (not personal tokens)
- Enable 2FA on npm account

## Support

For issues with publishing:
- Check [../.github/NPM_SETUP.md](../.github/NPM_SETUP.md)
- Review GitHub Actions logs
- Check npm documentation: https://docs.npmjs.com/

For extension issues:
- See [README.md](README.md)
- See [JUPYTERLAB4_INSTALLATION.md](../JUPYTERLAB4_INSTALLATION.md)
