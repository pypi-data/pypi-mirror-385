"""Test vigil package imports and metadata."""

from __future__ import annotations

import vigil


def test_package_version():
    """Test that package has a version."""
    assert hasattr(vigil, "__version__")
    assert isinstance(vigil.__version__, str)
    assert len(vigil.__version__) > 0


def test_package_exports():
    """Test that package exports expected modules."""
    assert hasattr(vigil, "cli")
    assert hasattr(vigil, "tools")


def test_tools_module():
    """Test that tools module has expected exports."""
    from vigil import tools

    # Core tool modules
    assert hasattr(tools, "promote")
    assert hasattr(tools, "anchor")
    assert hasattr(tools, "doctor")
    assert hasattr(tools, "vigilurl")
    assert hasattr(tools, "workspace_spec")
    assert hasattr(tools, "receipt_index")
