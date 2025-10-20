"""Jupyter Hurl Kernel - A kernel for executing Hurl commands in Jupyter notebooks."""

import json
import shutil
import sys
from pathlib import Path

from jupyter_client.kernelspec import KernelSpecManager
from jupyter_core.paths import jupyter_data_dir


def install_kernel(user=True, prefix=None):
    """Install the Hurl kernel specification.

    Args:
        user: Install to the user's kernel directory (default: True)
        prefix: Install to a specific prefix (e.g., virtual environment)
    """
    # Get the kernel specification
    kernel_json_file = Path(__file__).parent / "resources" / "kernel.json"

    if not kernel_json_file.exists():
        print(f"Error: kernel.json not found at {kernel_json_file}", file=sys.stderr)
        sys.exit(1)

    with open(kernel_json_file) as f:
        kernel_json = json.load(f)

    # Install the kernel spec
    ksm = KernelSpecManager()

    # Get the source directory (where kernel.json is located)
    source_dir = kernel_json_file.parent

    try:
        # Install the kernel specification
        dest = ksm.install_kernel_spec(
            str(source_dir),
            kernel_name="hurl",
            user=user,
            prefix=prefix,
        )
        print(f"Installed Hurl kernel to: {dest}")

        # Install CodeMirror mode for syntax highlighting
        codemirror_src = source_dir / "codemirror" / "hurl.js"
        if codemirror_src.exists():
            try:
                # Get Jupyter data directory
                data_dir = Path(jupyter_data_dir())
                codemirror_dest_dir = data_dir / "nbextensions" / "codemirror" / "mode" / "hurl"
                codemirror_dest_dir.mkdir(parents=True, exist_ok=True)

                # Copy the mode file
                codemirror_dest = codemirror_dest_dir / "hurl.js"
                shutil.copy2(codemirror_src, codemirror_dest)
                print(f"Installed CodeMirror mode to: {codemirror_dest}")
            except Exception as e:
                print(f"Warning: Could not install CodeMirror mode: {e}", file=sys.stderr)
                print("Syntax highlighting may not work properly.", file=sys.stderr)

        print("\nTo use the kernel, start Jupyter:")
        print("  jupyter notebook")
        print("  or")
        print("  jupyter lab")
        print("\nThen select 'Hurl' as the kernel for your notebook.")
        print("\nNote: You may need to refresh your browser for syntax highlighting to work.")
    except Exception as e:
        print(f"Error installing kernel: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Entry point for installing the kernel."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Install the Hurl Jupyter kernel"
    )
    parser.add_argument(
        "--user",
        action="store_true",
        default=True,
        help="Install to the user's kernel directory (default)",
    )
    parser.add_argument(
        "--sys-prefix",
        action="store_true",
        help="Install to Python's sys.prefix (useful in virtual environments)",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        help="Install to a specific prefix",
    )

    args = parser.parse_args()

    # Determine installation location
    if args.sys_prefix:
        prefix = sys.prefix
        user = False
    elif args.prefix:
        prefix = args.prefix
        user = False
    else:
        prefix = None
        user = True

    install_kernel(user=user, prefix=prefix)
