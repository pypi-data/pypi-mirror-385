# JupyterLab Hurl Extension

This JupyterLab extension provides syntax highlighting for Hurl files in JupyterLab 4.x using CodeMirror 6.

## Requirements

- JupyterLab >= 4.0.0
- Node.js >= 18
- Python >= 3.8

## Installation

### For Development

1. Install the package in development mode:

```bash
cd jupyterlab-hurl-extension

# Install dependencies
npm install

# Build the extension
npm run build

# Link the extension to JupyterLab
jupyter labextension develop . --overwrite

# Rebuild the extension TypeScript source after making changes
npm run build
```

2. Restart JupyterLab and refresh your browser

### For Production

```bash
cd jupyterlab-hurl-extension

# Install dependencies and build
npm install
npm run build:prod

# Install the extension
jupyter labextension install .
```

## Verify Installation

```bash
jupyter labextension list
```

You should see `jupyterlab-hurl-extension` in the list.

## Development

### Watch Mode

You can watch the source directory and run JupyterLab simultaneously in different terminals:

```bash
# Terminal 1: Watch the source directory
npm run watch

# Terminal 2: Run JupyterLab
jupyter lab
```

After making changes, you'll need to refresh your browser to see them.

### Uninstall

```bash
jupyter labextension uninstall jupyterlab-hurl-extension
```

## Troubleshooting

### Extension not loading

1. Check if the extension is installed:
   ```bash
   jupyter labextension list
   ```

2. Check for build errors:
   ```bash
   npm run build
   ```

3. Clear JupyterLab cache:
   ```bash
   jupyter lab clean
   jupyter lab build
   ```

### Syntax highlighting not working

1. Verify the kernel is using the correct MIME type (`text/x-hurl`)
2. Check browser console (F12) for errors
3. Ensure the Hurl kernel is properly installed
4. Try creating a new notebook

## Technical Details

This extension registers a CodeMirror 6 StreamLanguage for Hurl syntax. It provides:

- Syntax highlighting for HTTP methods, URLs, headers
- Section header recognition (`[Asserts]`, `[Captures]`, etc.)
- Assertion keyword highlighting
- JSONPath and XPath expression highlighting
- String, number, and boolean value highlighting
- Comment highlighting
- Template expression highlighting (`{{variable}}`)

The extension integrates with JupyterLab's language registry to provide syntax highlighting when the MIME type `text/x-hurl` is detected.
