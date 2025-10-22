"""Entry point for running vigil.tools modules directly.

This allows running tools as:
    python -m vigil.tools.anchor
    python -m vigil.tools.doctor
    python -m vigil.tools.promote
    etc.

The module name is taken from sys.argv and dispatched to the appropriate tool.
"""

from __future__ import annotations

import sys

if __name__ == "__main__":
    # This allows running: python -m vigil.tools.anchor
    # The tool modules have their own __main__ blocks that will be executed
    print(
        "Use 'python -m vigil.tools.<tool>' to run a specific tool, "
        "or use the 'vigil' CLI command.",
        file=sys.stderr,
    )
    print("\nAvailable tools:", file=sys.stderr)
    print("  - vigil.tools.promote", file=sys.stderr)
    print("  - vigil.tools.anchor", file=sys.stderr)
    print("  - vigil.tools.doctor", file=sys.stderr)
    print("  - vigil.tools.vigilurl", file=sys.stderr)
    print("  - vigil.tools.workspace_spec", file=sys.stderr)
    sys.exit(1)
