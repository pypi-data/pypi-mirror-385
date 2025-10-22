"""Inspection utilities for Vigil artifacts and receipts."""

from __future__ import annotations

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.json import JSON


console = Console()


def inspect_receipt(receipt_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """Inspect a Vigil receipt and return detailed information.

    Args:
        receipt_path: Path to receipt JSON file
        verbose: Include detailed information

    Returns:
        Dictionary with inspection results
    """
    if not receipt_path.exists():
        return {"error": f"Receipt not found: {receipt_path}"}

    try:
        with receipt_path.open(encoding="utf-8") as f:
            receipt_data = json.load(f)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}

    # Basic information
    info = {
        "file_path": str(receipt_path),
        "file_size": receipt_path.stat().st_size,
        "modified": datetime.fromtimestamp(receipt_path.stat().st_mtime).isoformat(),
        "receipt_id": receipt_data.get("runletId", "unknown"),
        "issuer": receipt_data.get("issuer", "unknown"),
        "vigil_url": receipt_data.get("vigilUrl", "unknown"),
        "git_ref": receipt_data.get("gitRef", "unknown"),
        "capsule_digest": receipt_data.get("capsuleDigest", "unknown"),
        "started_at": receipt_data.get("startedAt", "unknown"),
        "finished_at": receipt_data.get("finishedAt", "unknown"),
        "signature": receipt_data.get("signature", "unknown"),
        "glyphs": receipt_data.get("glyphs", []),
        "anchor": receipt_data.get("anchor", None)
    }

    # Inputs and outputs
    inputs = receipt_data.get("inputs", [])
    outputs = receipt_data.get("outputs", [])

    info["inputs"] = {
        "count": len(inputs),
        "items": inputs if verbose else [{"uri": inp.get("uri", "unknown")} for inp in inputs]
    }

    info["outputs"] = {
        "count": len(outputs),
        "items": outputs if verbose else [{"uri": out.get("uri", "unknown"), "checksum": out.get("checksum", "unknown")} for out in outputs]
    }

    # Metrics
    metrics = receipt_data.get("metrics", {})
    info["metrics"] = metrics if verbose else {"keys": list(metrics.keys())}

    # Environment
    environment = receipt_data.get("environment", {})
    info["environment"] = environment if verbose else {"keys": list(environment.keys())}

    # Validation
    validation = validate_receipt_structure(receipt_data)
    info["validation"] = validation

    return info


def inspect_artifact(artifact_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """Inspect an artifact file and return detailed information.

    Args:
        artifact_path: Path to artifact file
        verbose: Include detailed information

    Returns:
        Dictionary with inspection results
    """
    if not artifact_path.exists():
        return {"error": f"Artifact not found: {artifact_path}"}

    stat = artifact_path.stat()

    info = {
        "file_path": str(artifact_path),
        "file_name": artifact_path.name,
        "file_extension": artifact_path.suffix,
        "file_size": stat.st_size,
        "file_size_human": format_file_size(stat.st_size),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "permissions": oct(stat.st_mode)[-3:],
        "is_file": artifact_path.is_file(),
        "is_dir": artifact_path.is_dir(),
        "is_symlink": artifact_path.is_symlink()
    }

    # Calculate checksum
    if artifact_path.is_file():
        try:
            checksum = calculate_checksum(artifact_path)
            info["checksum"] = checksum
        except Exception as e:
            info["checksum_error"] = str(e)

    # File type detection
    if artifact_path.is_file():
        info["mime_type"] = detect_mime_type(artifact_path)
        info["file_type"] = detect_file_type(artifact_path)

    # Content analysis (for certain file types)
    if verbose and artifact_path.is_file():
        content_info = analyze_file_content(artifact_path)
        if content_info:
            info["content"] = content_info

    return info


def inspect_data_handle(handle_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """Inspect a data handle file and return detailed information.

    Args:
        handle_path: Path to data handle JSON file
        verbose: Include detailed information

    Returns:
        Dictionary with inspection results
    """
    if not handle_path.exists():
        return {"error": f"Data handle not found: {handle_path}"}

    try:
        with handle_path.open(encoding="utf-8") as f:
            handle_data = json.load(f)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}

    info = {
        "file_path": str(handle_path),
        "file_name": handle_path.name,
        "file_size": handle_path.stat().st_size,
        "modified": datetime.fromtimestamp(handle_path.stat().st_mtime).isoformat()
    }

    # Extract handle information
    info["name"] = handle_data.get("name", "unknown")
    info["uri"] = handle_data.get("uri", "unknown")
    info["checksum"] = handle_data.get("checksum", "unknown")
    info["schema"] = handle_data.get("schema", "unknown")

    # Metadata
    metadata = handle_data.get("metadata", {})
    info["metadata"] = metadata if verbose else {"keys": list(metadata.keys())}

    # Schema information
    schema_info = handle_data.get("schema", {})
    if isinstance(schema_info, dict):
        info["schema_info"] = {
            "columns": list(schema_info.get("columns", {}).keys()) if "columns" in schema_info else [],
            "fields": len(schema_info.get("fields", [])) if "fields" in schema_info else 0
        }

    # Validation
    validation = validate_data_handle_structure(handle_data)
    info["validation"] = validation

    return info


def inspect_project(project_path: Path, verbose: bool = False) -> Dict[str, Any]:
    """Inspect a Vigil project and return detailed information.

    Args:
        project_path: Path to project root
        verbose: Include detailed information

    Returns:
        Dictionary with inspection results
    """
    if not project_path.exists():
        return {"error": f"Project path not found: {project_path}"}

    info = {
        "project_path": str(project_path),
        "project_name": project_path.name
    }

    # Check for vigil.yaml
    vigil_yaml = project_path / "vigil.yaml"
    if vigil_yaml.exists():
        try:
            with vigil_yaml.open(encoding="utf-8") as f:
                vigil_config = yaml.safe_load(f)
            info["vigil_config"] = vigil_config if verbose else {"present": True, "keys": list(vigil_config.keys())}
        except Exception as e:
            info["vigil_config_error"] = str(e)
    else:
        info["vigil_config"] = {"present": False}

    # Check for .vigil directory
    vigil_dir = project_path / ".vigil"
    if vigil_dir.exists():
        info["vigil_dir"] = {
            "present": True,
            "contents": [item.name for item in vigil_dir.iterdir()] if verbose else ["present"]
        }
    else:
        info["vigil_dir"] = {"present": False}

    # Check for data handles
    handles_dir = project_path / "app" / "data" / "handles"
    if handles_dir.exists():
        handles = list(handles_dir.glob("*.dhandle.json"))
        info["data_handles"] = {
            "count": len(handles),
            "files": [h.name for h in handles] if verbose else ["present"]
        }
    else:
        info["data_handles"] = {"count": 0}

    # Check for receipts
    receipts_dir = project_path / "app" / "code" / "receipts"
    if receipts_dir.exists():
        receipts = list(receipts_dir.glob("*.json"))
        info["receipts"] = {
            "count": len(receipts),
            "files": [r.name for r in receipts] if verbose else ["present"]
        }
    else:
        info["receipts"] = {"count": 0}

    # Check for artifacts
    artifacts_dir = project_path / "app" / "code" / "artifacts"
    if artifacts_dir.exists():
        artifacts = list(artifacts_dir.iterdir())
        info["artifacts"] = {
            "count": len(artifacts),
            "files": [a.name for a in artifacts] if verbose else ["present"]
        }
    else:
        info["artifacts"] = {"count": 0}

    return info


def validate_receipt_structure(receipt_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate receipt structure and return validation results.

    Args:
        receipt_data: Receipt data dictionary

    Returns:
        Validation results
    """
    validation = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "required_fields": [],
        "optional_fields": []
    }

    # Required fields
    required_fields = ["issuer", "runletId", "vigilUrl", "outputs"]
    for field in required_fields:
        if field in receipt_data:
            validation["required_fields"].append(field)
        else:
            validation["errors"].append(f"Missing required field: {field}")
            validation["valid"] = False

    # Optional fields
    optional_fields = ["inputs", "metrics", "environment", "signature", "anchor", "glyphs"]
    for field in optional_fields:
        if field in receipt_data:
            validation["optional_fields"].append(field)

    # Validate outputs
    outputs = receipt_data.get("outputs", [])
    if outputs:
        for i, output in enumerate(outputs):
            if not isinstance(output, dict):
                validation["errors"].append(f"Output {i} is not a dictionary")
                validation["valid"] = False
            elif not output.get("checksum"):
                validation["warnings"].append(f"Output {i} missing checksum")

    return validation


def validate_data_handle_structure(handle_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data handle structure and return validation results.

    Args:
        handle_data: Data handle data dictionary

    Returns:
        Validation results
    """
    validation = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "required_fields": [],
        "optional_fields": []
    }

    # Required fields
    required_fields = ["name", "uri", "checksum"]
    for field in required_fields:
        if field in handle_data:
            validation["required_fields"].append(field)
        else:
            validation["errors"].append(f"Missing required field: {field}")
            validation["valid"] = False

    # Optional fields
    optional_fields = ["schema", "metadata"]
    for field in optional_fields:
        if field in handle_data:
            validation["optional_fields"].append(field)

    return validation


def calculate_checksum(file_path: Path, algorithm: str = "sha256") -> str:
    """Calculate checksum for a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, sha1, md5)

    Returns:
        Checksum string
    """
    hash_func = getattr(hashlib, algorithm)()

    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)

    return f"{algorithm}:{hash_func.hexdigest()}"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def detect_mime_type(file_path: Path) -> str:
    """Detect MIME type of a file.

    Args:
        file_path: Path to file

    Returns:
        MIME type string
    """
    import mimetypes

    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or "application/octet-stream"


def detect_file_type(file_path: Path) -> str:
    """Detect file type based on extension and content.

    Args:
        file_path: Path to file

    Returns:
        File type string
    """
    suffix = file_path.suffix.lower()

    type_map = {
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".csv": "CSV",
        ".tsv": "TSV",
        ".txt": "Text",
        ".md": "Markdown",
        ".py": "Python",
        ".r": "R",
        ".sh": "Shell",
        ".sql": "SQL",
        ".xml": "XML",
        ".html": "HTML",
        ".pdf": "PDF",
        ".png": "PNG Image",
        ".jpg": "JPEG Image",
        ".jpeg": "JPEG Image",
        ".gif": "GIF Image",
        ".svg": "SVG Image",
        ".zip": "ZIP Archive",
        ".tar": "TAR Archive",
        ".gz": "GZIP Archive"
    }

    return type_map.get(suffix, "Unknown")


def analyze_file_content(file_path: Path) -> Optional[Dict[str, Any]]:
    """Analyze file content for certain file types.

    Args:
        file_path: Path to file

    Returns:
        Content analysis results or None
    """
    suffix = file_path.suffix.lower()

    if suffix == ".json":
        try:
            with file_path.open(encoding="utf-8") as f:
                data = json.load(f)
            return {
                "type": "JSON",
                "valid": True,
                "keys": list(data.keys()) if isinstance(data, dict) else None,
                "array_length": len(data) if isinstance(data, list) else None
            }
        except Exception:
            return {"type": "JSON", "valid": False}

    elif suffix in [".yaml", ".yml"]:
        try:
            with file_path.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return {
                "type": "YAML",
                "valid": True,
                "keys": list(data.keys()) if isinstance(data, dict) else None
            }
        except Exception:
            return {"type": "YAML", "valid": False}

    elif suffix == ".csv":
        try:
            import csv
            with file_path.open(encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
            return {
                "type": "CSV",
                "valid": True,
                "rows": len(rows),
                "columns": len(rows[0]) if rows else 0,
                "headers": rows[0] if rows else []
            }
        except Exception:
            return {"type": "CSV", "valid": False}

    return None


def display_inspection_result(result: Dict[str, Any], title: str = "Inspection Result") -> None:
    """Display inspection result in a formatted way.

    Args:
        result: Inspection result dictionary
        title: Title for the display
    """
    if "error" in result:
        console.print(f"[red]Error: {result['error']}[/red]")
        return

    # Create a tree structure
    tree = Tree(f"[bold]{title}[/bold]")

    # Add basic information
    for key, value in result.items():
        if key not in ["error", "validation"] and not isinstance(value, dict):
            tree.add(f"[cyan]{key}[/cyan]: {value}")

    # Add nested information
    for key, value in result.items():
        if isinstance(value, dict) and key != "validation":
            branch = tree.add(f"[cyan]{key}[/cyan]")
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, (list, dict)):
                    branch.add(f"{sub_key}: {len(sub_value) if isinstance(sub_value, list) else 'present'}")
                else:
                    branch.add(f"{sub_key}: {sub_value}")

    # Add validation results
    if "validation" in result:
        validation = result["validation"]
        validation_branch = tree.add("[yellow]Validation[/yellow]")

        if validation.get("valid"):
            validation_branch.add("[green]✓ Valid[/green]")
        else:
            validation_branch.add("[red]✗ Invalid[/red]")

        if validation.get("errors"):
            for error in validation["errors"]:
                validation_branch.add(f"[red]Error: {error}[/red]")

        if validation.get("warnings"):
            for warning in validation["warnings"]:
                validation_branch.add(f"[yellow]Warning: {warning}[/yellow]")

    console.print(tree)


def cli() -> None:
    """CLI entry point for inspection."""
    import argparse

    parser = argparse.ArgumentParser(description="Inspect Vigil artifacts, receipts, and projects")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Receipt inspection
    receipt_parser = subparsers.add_parser("receipt", help="Inspect a receipt")
    receipt_parser.add_argument("path", type=Path, help="Path to receipt JSON file")
    receipt_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    receipt_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Artifact inspection
    artifact_parser = subparsers.add_parser("artifact", help="Inspect an artifact")
    artifact_parser.add_argument("path", type=Path, help="Path to artifact file")
    artifact_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    artifact_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Data handle inspection
    handle_parser = subparsers.add_parser("handle", help="Inspect a data handle")
    handle_parser.add_argument("path", type=Path, help="Path to data handle JSON file")
    handle_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    handle_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Project inspection
    project_parser = subparsers.add_parser("project", help="Inspect a project")
    project_parser.add_argument("path", type=Path, help="Path to project directory")
    project_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    project_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute inspection
    if args.command == "receipt":
        result = inspect_receipt(args.path, args.verbose)
        title = f"Receipt Inspection: {args.path.name}"
    elif args.command == "artifact":
        result = inspect_artifact(args.path, args.verbose)
        title = f"Artifact Inspection: {args.path.name}"
    elif args.command == "handle":
        result = inspect_data_handle(args.path, args.verbose)
        title = f"Data Handle Inspection: {args.path.name}"
    elif args.command == "project":
        result = inspect_project(args.path, args.verbose)
        title = f"Project Inspection: {args.path.name}"
    else:
        print("Unknown command")
        return

    # Display results
    if args.json:
        console.print(JSON(json.dumps(result, indent=2)))
    else:
        display_inspection_result(result, title)


if __name__ == "__main__":
    cli()
