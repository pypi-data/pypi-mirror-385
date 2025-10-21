"""JupyterLab Hurl Extension - Syntax highlighting for Hurl in JupyterLab 4."""

from ._version import __version__

__all__ = ["__version__"]


def _jupyter_labextension_paths():
    """Called by JupyterLab to get the extension metadata."""
    return [{
        "src": "labextension",
        "dest": "jupyterlab-hurl-extension"
    }]
