"""Vigil: Observable, collaborative, reproducible science platform.

This package provides both a CLI tool and importable library for creating
reproducible scientific workflows with automatic provenance tracking.

CLI Usage:
    Install the CLI globally:
        $ uv tool install vigil-core

    Create a new project:
        $ vigil new imaging-starter my-project
        $ cd my-project
        $ vigil run --cores 4
        $ vigil promote

Library Usage:
    Import and use programmatically:
        from vigil.core import run_pipeline, generate_receipt
        result = run_pipeline("python train.py")
        receipt = generate_receipt(result.artifacts)
"""

# Import core API for programmatic access
from vigil import core, tools

__version__ = "0.3.8"
__all__ = ["core", "tools", "__version__"]
