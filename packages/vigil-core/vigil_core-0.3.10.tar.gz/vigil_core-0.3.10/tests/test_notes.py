"""Tests for vigil.notes module."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from vigil.notes import (
    create_experiment_entry,
    create_protocol,
    generate_index,
    get_template_path,
)


def test_get_template_path():
    """Test getting template paths."""
    # Should return valid paths for known templates
    exp_path = get_template_path("experiment_entry.md")
    assert exp_path.exists()
    assert exp_path.name == "experiment_entry.md"

    proto_path = get_template_path("protocol.md")
    assert proto_path.exists()
    assert proto_path.name == "protocol.md"

    # Should raise FileNotFoundError for unknown templates
    with pytest.raises(FileNotFoundError):
        get_template_path("nonexistent.md")


def test_create_experiment_entry(tmp_path: Path):
    """Test creating experiment entries."""
    output_dir = tmp_path / "experiments"

    # Create experiment with default date
    exp_path = create_experiment_entry(
        title="Test Experiment",
        author="Jane Doe",
        output_dir=output_dir,
        status="in_progress",
        tags=["imaging", "pilot"],
    )

    # Check file was created
    assert exp_path.exists()
    assert exp_path.parent == output_dir

    # Check filename format: YYYY-MM-DD_slug.md
    today = datetime.now().strftime("%Y-%m-%d")
    assert exp_path.name.startswith(today)
    assert "test-experiment" in exp_path.name
    assert exp_path.suffix == ".md"

    # Check content has expected metadata
    content = exp_path.read_text()
    assert "date: " in content
    assert "author: Jane Doe" in content
    assert "experiment: Test Experiment" in content
    assert "status: in_progress" in content
    assert "tags: [imaging, pilot]" in content
    assert "# Experiment: Test Experiment" in content


def test_create_experiment_entry_custom_date(tmp_path: Path):
    """Test creating experiment entry with custom date."""
    output_dir = tmp_path / "experiments"

    exp_path = create_experiment_entry(
        title="Past Experiment",
        author="John Smith",
        output_dir=output_dir,
        date="2025-01-15",
    )

    # Check filename uses custom date
    assert exp_path.name.startswith("2025-01-15")
    content = exp_path.read_text()
    assert "date: 2025-01-15" in content


def test_create_experiment_entry_slug_generation(tmp_path: Path):
    """Test that experiment titles are properly slugified."""
    output_dir = tmp_path / "experiments"

    # Test with special characters and spaces
    exp_path = create_experiment_entry(
        title="Testing: Cell Segmentation & Analysis!",
        author="Jane Doe",
        output_dir=output_dir,
    )

    # Slug should be lowercase, hyphenated, alphanumeric
    filename = exp_path.stem
    slug = filename.split("_", 1)[1]  # Remove date prefix
    assert slug == "testing-cell-segmentation-analysis"


def test_create_protocol(tmp_path: Path):
    """Test creating protocols."""
    output_dir = tmp_path / "protocols"

    proto_path = create_protocol(
        title="Cell Culture Protocol",
        author="Jane Doe",
        output_dir=output_dir,
        version="1.0",
    )

    # Check file was created
    assert proto_path.exists()
    assert proto_path.parent == output_dir

    # Check filename format: slug.md
    assert proto_path.name == "cell-culture-protocol.md"

    # Check content
    content = proto_path.read_text()
    assert "title: Cell Culture Protocol" in content
    assert "version: 1.0" in content
    assert "author: Jane Doe" in content
    assert "# Cell Culture Protocol" in content


def test_create_protocol_custom_validated_date(tmp_path: Path):
    """Test creating protocol with custom validation date."""
    output_dir = tmp_path / "protocols"

    proto_path = create_protocol(
        title="Test Protocol",
        author="John Smith",
        output_dir=output_dir,
        validated="2025-01-01",
    )

    content = proto_path.read_text()
    assert "validated: 2025-01-01" in content


def test_generate_index_empty(tmp_path: Path):
    """Test generating index with no experiments or protocols."""
    notes_dir = tmp_path

    index_path = generate_index(notes_dir)

    assert index_path.exists()
    assert index_path.name == "README.md"

    content = index_path.read_text()
    assert "# Lab Notebook" in content
    assert "## Analysis" in content
    assert "app/code/receipts/" in content


def test_generate_index_with_experiments(tmp_path: Path):
    """Test generating index with experiments."""
    notes_dir = tmp_path
    exp_dir = notes_dir / "experiments"
    exp_dir.mkdir(parents=True)

    # Create some experiment files
    (exp_dir / "2025-01-20_initial-test.md").write_text("# Test 1")
    (exp_dir / "2025-01-19_baseline-run.md").write_text("# Test 2")
    (exp_dir / "2025-01-18_pilot-study.md").write_text("# Test 3")

    index_path = generate_index(notes_dir)
    content = index_path.read_text()

    assert "## Recent Experiments" in content
    # Should be sorted by date (newest first)
    assert "2025-01-20: Initial Test" in content
    assert "2025-01-19: Baseline Run" in content
    assert "2025-01-18: Pilot Study" in content
    # Check links are correct
    assert "(experiments/2025-01-20_initial-test.md)" in content


def test_generate_index_with_protocols(tmp_path: Path):
    """Test generating index with protocols."""
    notes_dir = tmp_path
    proto_dir = notes_dir / "protocols"
    proto_dir.mkdir(parents=True)

    # Create some protocol files
    (proto_dir / "cell-culture.md").write_text("# Protocol 1")
    (proto_dir / "imaging-setup.md").write_text("# Protocol 2")
    (proto_dir / "README.md").write_text("# Should be ignored")

    index_path = generate_index(notes_dir)
    content = index_path.read_text()

    assert "## Protocols" in content
    assert "Cell Culture" in content
    assert "Imaging Setup" in content
    # README should be excluded from protocol list (only 2 protocols should appear)
    assert content.count("(protocols/") == 2


def test_generate_index_with_both(tmp_path: Path):
    """Test generating index with both experiments and protocols."""
    notes_dir = tmp_path
    exp_dir = notes_dir / "experiments"
    proto_dir = notes_dir / "protocols"
    exp_dir.mkdir(parents=True)
    proto_dir.mkdir(parents=True)

    # Create experiments
    (exp_dir / "2025-01-20_test.md").write_text("# Exp")
    # Create protocols
    (proto_dir / "protocol-1.md").write_text("# Proto")

    index_path = generate_index(notes_dir)
    content = index_path.read_text()

    assert "## Recent Experiments" in content
    assert "## Protocols" in content
    assert "## Analysis" in content


def test_generate_index_limits_experiments(tmp_path: Path):
    """Test that index only shows last 10 experiments."""
    notes_dir = tmp_path
    exp_dir = notes_dir / "experiments"
    exp_dir.mkdir(parents=True)

    # Create 15 experiments
    for i in range(15):
        date = f"2025-01-{i+1:02d}"
        (exp_dir / f"{date}_experiment-{i}.md").write_text(f"# Exp {i}")

    index_path = generate_index(notes_dir)
    content = index_path.read_text()

    # Count number of experiment links (should be max 10)
    experiment_count = content.count("(experiments/")
    assert experiment_count == 10


def test_timestamp_format(tmp_path: Path):
    """Test that experiment filenames use correct timestamp format."""
    output_dir = tmp_path / "experiments"

    exp_path = create_experiment_entry(
        title="Test",
        author="Jane Doe",
        output_dir=output_dir,
        date="2025-01-20",
    )

    # Filename should be YYYY-MM-DD_slug.md
    assert exp_path.name.startswith("2025-01-20_")
    assert exp_path.name.endswith(".md")

    # Date should be in correct format (not reversed, not with slashes, etc.)
    parts = exp_path.name.split("_")
    date_part = parts[0]
    assert len(date_part) == 10  # YYYY-MM-DD is 10 chars
    assert date_part.count("-") == 2
    year, month, day = date_part.split("-")
    assert len(year) == 4
    assert len(month) == 2
    assert len(day) == 2
