import json
import subprocess
from pathlib import Path

from app.code.tools import pin_capsule_digest

OLD_DIGEST = "sha256:" + "a" * 64
NEW_DIGEST = "sha256:" + "b" * 64
IMAGE_REF = "ghcr.io/example/capsule"


def _write_manifest(base_dir: Path) -> None:
    manifest = (
        "capsule:\n"
        "  image: \"{image}\"\n"
        "  extensions:\n"
        "    - ext-one\n"
        "    - ext-two\n"
    ).format(image=f"{IMAGE_REF}@{OLD_DIGEST}")
    (base_dir / "vigil.yaml").write_text(manifest, encoding="utf-8")


def _initialise_git_repo(base_dir: Path) -> None:
    subprocess.run(["git", "init"], cwd=base_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Vigil Test"],
        cwd=base_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "vigil@example.com"],
        cwd=base_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "vigil.yaml"], cwd=base_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial manifest"],
        cwd=base_dir,
        check=True,
        capture_output=True,
    )


def _write_documentation(base_dir: Path) -> None:
    (base_dir / "README.md").write_text(f"Capsule digest: {OLD_DIGEST}\n", encoding="utf-8")

    arcade_dir = base_dir / "app/notes/arcade"
    arcade_dir.mkdir(parents=True, exist_ok=True)
    (arcade_dir / "README.md").write_text(
        f"Arcade digest -> {OLD_DIGEST}\n",
        encoding="utf-8",
    )

    method_dir = base_dir / "app/notes/method"
    method_dir.mkdir(parents=True, exist_ok=True)
    (method_dir / "METHODCARD.md").write_text(
        f"Method digest: {OLD_DIGEST}\n",
        encoding="utf-8",
    )
    (method_dir / "methodcard.json").write_text(
        json.dumps({"capsule": {"digest": OLD_DIGEST}}, indent=2) + "\n",
        encoding="utf-8",
    )

    notebooks_dir = base_dir / "app/notes/notebooks"
    notebooks_dir.mkdir(parents=True, exist_ok=True)
    (notebooks_dir / "01_explore_data.ipynb").write_text(
        json.dumps(
            {
                "cells": [],
                "metadata": {"capsule_digest": OLD_DIGEST},
                "nbformat": 4,
                "nbformat_minor": 5,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (notebooks_dir / "01_explore_data.md").write_text(
        f"Notebook digest {OLD_DIGEST}\n",
        encoding="utf-8",
    )

    vigil_dir = base_dir / ".vigil"
    vigil_dir.mkdir(parents=True, exist_ok=True)
    (vigil_dir / "workspace.spec.json").write_text(
        json.dumps(
            {
                "capsule": {
                    "image": f"{IMAGE_REF}@{OLD_DIGEST}",
                    "extensions": ["ext-one"],
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_pin_capsule_digest_updates_known_documents(tmp_path: Path) -> None:
    base_dir = tmp_path / "repo"
    base_dir.mkdir()

    _write_manifest(base_dir)
    _initialise_git_repo(base_dir)

    # Create documentation with the digest after the initial commit so that
    # the git-based discovery does not see the files.
    _write_documentation(base_dir)

    touched = pin_capsule_digest.run(
        NEW_DIGEST,
        base_dir=base_dir,
        paths_output=Path("touched.txt"),
    )

    manifest_text = (base_dir / "vigil.yaml").read_text(encoding="utf-8")
    assert NEW_DIGEST in manifest_text
    assert OLD_DIGEST not in manifest_text

    spec_path = base_dir / ".vigil/workspace.spec.json"
    spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
    assert spec_data["capsule"]["image"] == f"{IMAGE_REF}@{NEW_DIGEST}"

    expected_docs = [
        base_dir / "README.md",
        base_dir / "app/notes/arcade/README.md",
        base_dir / "app/notes/method/METHODCARD.md",
        base_dir / "app/notes/method/methodcard.json",
        base_dir / "app/notes/notebooks/01_explore_data.ipynb",
        base_dir / "app/notes/notebooks/01_explore_data.md",
    ]

    for path in expected_docs:
        contents = path.read_text(encoding="utf-8")
        assert NEW_DIGEST in contents
        assert OLD_DIGEST not in contents

    touched_rel = {p.relative_to(base_dir).as_posix() for p in touched}
    assert {
        "vigil.yaml",
        ".vigil/workspace.spec.json",
        "README.md",
        "app/notes/arcade/README.md",
        "app/notes/method/METHODCARD.md",
        "app/notes/method/methodcard.json",
        "app/notes/notebooks/01_explore_data.ipynb",
        "app/notes/notebooks/01_explore_data.md",
    } == touched_rel

    paths_output = (base_dir / "touched.txt").read_text(encoding="utf-8").strip().splitlines()
    assert touched_rel == set(paths_output)
