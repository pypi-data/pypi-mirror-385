# Installation Guide

## For Users (Recommended)

Install the prebuilt extension using pip:

```bash
pip install jupyterlab-hurl-extension
```

That's it! The extension will be automatically enabled in JupyterLab 4.x.

### Verify Installation

```bash
jupyter labextension list
```

You should see `jupyterlab-hurl-extension` in the list of enabled extensions.

## For Developers

If you want to develop or modify the extension:

### Prerequisites

- Python >= 3.8
- Node.js >= 18
- JupyterLab >= 4.0.0

### Install from Source

```bash
git clone https://github.com/micedre/jupyter-hurl-kernel.git
cd jupyter-hurl-kernel/jupyterlab-hurl-extension

# Install Python package in editable mode
pip install -e .

# Install Node.js dependencies
npm install

# Build and link the extension
jupyter labextension develop . --overwrite

# Rebuild after changes
npm run build
```

### Development Mode with Auto-Rebuild

Terminal 1:
```bash
npm run watch
```

Terminal 2:
```bash
jupyter lab --watch
```

Changes to the TypeScript source will automatically rebuild. Just refresh your browser to see changes.

## Uninstall

```bash
pip uninstall jupyterlab-hurl-extension
```

## Troubleshooting

### Extension not showing up

1. Verify installation:
   ```bash
   pip show jupyterlab-hurl-extension
   jupyter labextension list
   ```

2. Rebuild JupyterLab:
   ```bash
   jupyter lab build
   ```

3. Clear cache and restart:
   ```bash
   jupyter lab clean
   jupyter lab
   ```

### Build errors during development

```bash
# Clean everything
npm run clean:all
rm -rf node_modules
npm install
npm run build
```

## More Information

- [Main README](../README.md)
- [JupyterLab 4 Installation Guide](../JUPYTERLAB4_INSTALLATION.md)
- [Publishing Guide](PUBLISHING.md)
