"""Export utilities for Vigil provenance graphs and metadata."""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


def export_provenance_graph_rocrate(graph_data: Dict[str, Any],
                                  output_dir: Path) -> None:
    """Export provenance graph as RO-Crate.

    Args:
        graph_data: Provenance graph data
        output_dir: Output directory for RO-Crate
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create RO-Crate metadata
    rocrate_metadata = {
        "@context": [
            "https://w3id.org/ro/crate/1.1/context",
            {
                "prov": "http://www.w3.org/ns/prov#",
                "schema": "https://schema.org/",
                "vigil": "https://vigil.dev/schemas/"
            }
        ],
        "@graph": [
            {
                "@id": "ro-crate-metadata.json",
                "@type": "CreativeWork",
                "identifier": "ro-crate-metadata.json",
                "about": {
                    "@id": "./"
                },
                "conformsTo": {
                    "@id": "https://w3id.org/ro/crate/1.1"
                },
                "about": {
                    "@id": "./"
                }
            },
            {
                "@id": "./",
                "@type": "Dataset",
                "name": "Vigil Provenance Graph",
                "description": "Provenance graph exported from Vigil",
                "dateCreated": datetime.now(UTC).isoformat(),
                "creator": {
                    "@type": "Organization",
                    "name": "Vigil"
                }
            }
        ]
    }

    # Add nodes as RO-Crate entities
    for node in graph_data.get("nodes", []):
        entity = {
            "@id": f"./{node['id']}",
            "@type": "File",
            "name": node.get("name", node["id"]),
            "description": f"Artifact: {node.get('type', 'unknown')}",
            "contentSize": node.get("size_bytes"),
            "encodingFormat": "application/octet-stream"
        }

        # Add Vigil-specific properties
        if "uri" in node:
            entity["url"] = node["uri"]
        if "checksum" in node:
            entity["sha256"] = node["checksum"]

        rocrate_metadata["@graph"].append(entity)

    # Add provenance relationships
    for edge in graph_data.get("edges", []):
        relationship = {
            "@id": f"./{edge['id']}",
            "@type": "CreativeWork",
            "name": f"Relationship: {edge['type']}",
            "about": [
                {"@id": f"./{edge['from']}"},
                {"@id": f"./{edge['to']}"}
            ]
        }

        # Add PROV-O properties
        if edge["type"] == "input_of":
            relationship["@type"] = "prov:Usage"
            relationship["prov:hadRole"] = "input"
        elif edge["type"] == "output_of":
            relationship["@type"] = "prov:Generation"
            relationship["prov:hadRole"] = "output"

        rocrate_metadata["@graph"].append(relationship)

    # Write RO-Crate metadata
    with (output_dir / "ro-crate-metadata.json").open("w", encoding="utf-8") as f:
        json.dump(rocrate_metadata, f, indent=2)

    # Write Vigil-specific metadata
    vigil_metadata = {
        "vigil_version": "0.2.1",
        "export_timestamp": datetime.now(UTC).isoformat(),
        "export_format": "ro-crate",
        "original_graph": graph_data
    }

    with (output_dir / "vigil-metadata.json").open("w", encoding="utf-8") as f:
        json.dump(vigil_metadata, f, indent=2)


def export_provenance_graph_jsonld(graph_data: Dict[str, Any],
                                 output_file: Path) -> None:
    """Export provenance graph as JSON-LD.

    Args:
        graph_data: Provenance graph data
        output_file: Output file path
    """
    jsonld_data = {
        "@context": {
            "prov": "http://www.w3.org/ns/prov#",
            "schema": "https://schema.org/",
            "vigil": "https://vigil.dev/schemas/",
            "id": "@id",
            "type": "@type",
            "name": "schema:name",
            "description": "schema:description",
            "created": "prov:generatedAtTime",
            "used": "prov:used",
            "wasGeneratedBy": "prov:wasGeneratedBy",
            "wasDerivedFrom": "prov:wasDerivedFrom"
        },
        "@graph": []
    }

    # Add nodes as PROV entities
    for node in graph_data.get("nodes", []):
        entity = {
            "@id": f"vigil:artifact/{node['id']}",
            "@type": "prov:Entity",
            "name": node.get("name", node["id"]),
            "description": f"Artifact: {node.get('type', 'unknown')}"
        }

        # Add Vigil-specific properties
        if "uri" in node:
            entity["vigil:uri"] = node["uri"]
        if "checksum" in node:
            entity["vigil:checksum"] = node["checksum"]
        if "size_bytes" in node:
            entity["vigil:sizeBytes"] = node["size_bytes"]

        jsonld_data["@graph"].append(entity)

    # Add relationships as PROV activities
    for edge in graph_data.get("edges", []):
        activity = {
            "@id": f"vigil:activity/{edge['id']}",
            "@type": "prov:Activity",
            "name": f"Relationship: {edge['type']}"
        }

        # Add PROV relationships
        if edge["type"] == "input_of":
            activity["prov:used"] = {"@id": f"vigil:artifact/{edge['from']}"}
            activity["prov:generated"] = {"@id": f"vigil:artifact/{edge['to']}"}
        elif edge["type"] == "output_of":
            activity["prov:generated"] = {"@id": f"vigil:artifact/{edge['from']}"}
            activity["prov:used"] = {"@id": f"vigil:artifact/{edge['to']}"}
        elif edge["type"] == "derived_from":
            activity["prov:wasDerivedFrom"] = {
                "@id": f"vigil:artifact/{edge['from']}"
            }
            activity["prov:generated"] = {"@id": f"vigil:artifact/{edge['to']}"}

        jsonld_data["@graph"].append(activity)

    # Write JSON-LD file
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(jsonld_data, f, indent=2)


def export_receipt_chain(receipts: List[Dict[str, Any]],
                        output_file: Path) -> None:
    """Export receipt chain as structured data.

    Args:
        receipts: List of receipts in chain
        output_file: Output file path
    """
    chain_data = {
        "chain_id": str(uuid4()),
        "export_timestamp": datetime.now(UTC).isoformat(),
        "total_receipts": len(receipts),
        "receipts": []
    }

    for i, receipt in enumerate(receipts):
        receipt_entry = {
            "index": i,
            "receipt_id": receipt.get("runletId"),
            "timestamp": receipt.get("startedAt"),
            "git_ref": receipt.get("gitRef"),
            "inputs_count": len(receipt.get("inputs", [])),
            "outputs_count": len(receipt.get("outputs", [])),
            "parent_receipt": receipt.get("parentReceipt"),
            "signature": receipt.get("signature"),
            "full_receipt": receipt
        }
        chain_data["receipts"].append(receipt_entry)

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(chain_data, f, indent=2)


def export_environment_comparison(env1: Dict[str, Any],
                                env2: Dict[str, Any],
                                output_file: Path) -> None:
    """Export environment comparison as structured data.

    Args:
        env1: First environment
        env2: Second environment
        output_file: Output file path
    """
    comparison_data = {
        "comparison_id": str(uuid4()),
        "export_timestamp": datetime.now(UTC).isoformat(),
        "environment1": {
            "timestamp": env1.get("timestamp"),
            "system": env1.get("system", {}),
            "python": env1.get("python", {}),
            "docker": env1.get("docker", {}),
            "gpu": env1.get("gpu", {})
        },
        "environment2": {
            "timestamp": env2.get("timestamp"),
            "system": env2.get("system", {}),
            "python": env2.get("python", {}),
            "docker": env2.get("docker", {}),
            "gpu": env2.get("gpu", {})
        },
        "differences": []
    }

    # Compare environments
    def compare_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], path: str = "") -> List[Dict[str, Any]]:
        differences = []
        all_keys = set(dict1.keys()) | set(dict2.keys())

        for key in all_keys:
            current_path = f"{path}.{key}" if path else key

            if key not in dict1:
                differences.append({
                    "path": current_path,
                    "type": "missing_in_env1",
                    "value": dict2[key]
                })
            elif key not in dict2:
                differences.append({
                    "path": current_path,
                    "type": "missing_in_env2",
                    "value": dict1[key]
                })
            elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                differences.extend(compare_dicts(dict1[key], dict2[key], current_path))
            elif dict1[key] != dict2[key]:
                differences.append({
                    "path": current_path,
                    "type": "different_value",
                    "env1_value": dict1[key],
                    "env2_value": dict2[key]
                })

        return differences

    comparison_data["differences"] = compare_dicts(
        comparison_data["environment1"],
        comparison_data["environment2"]
    )

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(comparison_data, f, indent=2)


def cli() -> None:
    """CLI entry point for export utilities."""
    import argparse

    parser = argparse.ArgumentParser(description="Export Vigil data in various formats")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Provenance graph export
    graph_parser = subparsers.add_parser("graph", help="Export provenance graph")
    graph_parser.add_argument("input", type=Path, help="Input graph file")
    graph_parser.add_argument("output", type=Path, help="Output file/directory")
    graph_parser.add_argument("--format", choices=["jsonld", "rocrate"], default="jsonld", help="Export format")

    # Receipt chain export
    chain_parser = subparsers.add_parser("chain", help="Export receipt chain")
    chain_parser.add_argument("receipts", nargs="+", type=Path, help="Receipt files")
    chain_parser.add_argument("output", type=Path, help="Output file")

    # Environment comparison export
    env_parser = subparsers.add_parser("env", help="Export environment comparison")
    env_parser.add_argument("env1", type=Path, help="First environment file")
    env_parser.add_argument("env2", type=Path, help="Second environment file")
    env_parser.add_argument("output", type=Path, help="Output file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "graph":
        with args.input.open("r", encoding="utf-8") as f:
            graph_data = json.load(f)

        if args.format == "jsonld":
            export_provenance_graph_jsonld(graph_data, args.output)
            print(f"Exported provenance graph as JSON-LD to {args.output}")
        elif args.format == "rocrate":
            export_provenance_graph_rocrate(graph_data, args.output)
            print(f"Exported provenance graph as RO-Crate to {args.output}")

    elif args.command == "chain":
        receipts = []
        for receipt_file in args.receipts:
            with receipt_file.open("r", encoding="utf-8") as f:
                receipts.append(json.load(f))

        export_receipt_chain(receipts, args.output)
        print(f"Exported receipt chain to {args.output}")

    elif args.command == "env":
        with args.env1.open("r", encoding="utf-8") as f:
            env1 = json.load(f)
        with args.env2.open("r", encoding="utf-8") as f:
            env2 = json.load(f)

        export_environment_comparison(env1, env2, args.output)
        print(f"Exported environment comparison to {args.output}")


if __name__ == "__main__":
    cli()
