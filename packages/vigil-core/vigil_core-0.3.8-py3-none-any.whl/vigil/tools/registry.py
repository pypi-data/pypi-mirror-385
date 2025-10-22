"""Local artifact registry for Vigil."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4


class ArtifactType(str, Enum):
    """Types of artifacts."""

    DATASET = "dataset"
    MODEL = "model"
    CODE = "code"
    NOTE = "note"
    RECEIPT = "receipt"
    OTHER = "other"


class ArtifactStatus(str, Enum):
    """Status of artifacts."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass
class ArtifactMetadata:
    """Metadata for an artifact."""

    id: str
    name: str
    artifact_type: ArtifactType
    uri: str
    checksum: str
    size_bytes: int | None = None
    description: str | None = None
    tags: list[str] = None
    metadata: dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    status: ArtifactStatus = ArtifactStatus.ACTIVE

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now(UTC)
        if self.updated_at is None:
            self.updated_at = datetime.now(UTC)


@dataclass
class ArtifactRelationship:
    """Relationship between artifacts."""

    id: str
    from_artifact_id: str
    to_artifact_id: str
    relationship_type: str
    description: str | None = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(UTC)


class LocalRegistry:
    """Local SQLite-based artifact registry."""

    def __init__(self, registry_path: Path | None = None):
        """Initialize local registry.

        Args:
            registry_path: Path to SQLite database file
        """
        self.registry_path = registry_path or Path(".vigil/registry.db")
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.registry_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    uri TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    size_bytes INTEGER,
                    description TEXT,
                    tags TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active'
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    from_artifact_id TEXT NOT NULL,
                    to_artifact_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (from_artifact_id) REFERENCES artifacts (id),
                    FOREIGN KEY (to_artifact_id) REFERENCES artifacts (id)
                )
            """)

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts (artifact_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_status ON artifacts (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_checksum ON artifacts (checksum)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships (from_artifact_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships (to_artifact_id)")

            conn.commit()

    def register_artifact(self, artifact: ArtifactMetadata) -> ArtifactMetadata:
        """Register an artifact in the local registry.

        Args:
            artifact: Artifact metadata

        Returns:
            Registered artifact with updated timestamps
        """
        artifact.id = artifact.id or str(uuid4())
        artifact.updated_at = datetime.now(UTC)

        with sqlite3.connect(self.registry_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO artifacts
                (id, name, artifact_type, uri, checksum, size_bytes, description,
                 tags, metadata, created_at, updated_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                artifact.id,
                artifact.name,
                artifact.artifact_type.value,
                artifact.uri,
                artifact.checksum,
                artifact.size_bytes,
                artifact.description,
                json.dumps(artifact.tags),
                json.dumps(artifact.metadata),
                artifact.created_at.isoformat(),
                artifact.updated_at.isoformat(),
                artifact.status.value
            ))
            conn.commit()

        return artifact

    def get_artifact(self, artifact_id: str) -> ArtifactMetadata | None:
        """Get an artifact by ID.

        Args:
            artifact_id: Artifact ID

        Returns:
            Artifact metadata or None if not found
        """
        with sqlite3.connect(self.registry_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM artifacts WHERE id = ?", (artifact_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_artifact(row)

        return None

    def find_artifacts(self, artifact_type: ArtifactType | None = None,
                      status: ArtifactStatus | None = None,
                      tags: list[str] | None = None,
                      limit: int = 100) -> list[ArtifactMetadata]:
        """Find artifacts matching criteria.

        Args:
            artifact_type: Filter by artifact type
            status: Filter by status
            tags: Filter by tags (any match)
            limit: Maximum number of results

        Returns:
            List of matching artifacts
        """
        query = "SELECT * FROM artifacts WHERE 1=1"
        params = []

        if artifact_type:
            query += " AND artifact_type = ?"
            params.append(artifact_type.value)

        if status:
            query += " AND status = ?"
            params.append(status.value)

        if tags:
            # SQLite JSON functions for tag matching
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("JSON_EXTRACT(tags, '$') LIKE ?")
                params.append(f'%"{tag}"%')
            query += " AND (" + " OR ".join(tag_conditions) + ")"

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.registry_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_artifact(row) for row in rows]

    def search_artifacts(self, query: str, limit: int = 100) -> list[ArtifactMetadata]:
        """Search artifacts by name, description, or metadata.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching artifacts
        """
        search_term = f"%{query}%"

        with sqlite3.connect(self.registry_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM artifacts
                WHERE name LIKE ?
                   OR description LIKE ?
                   OR metadata LIKE ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (search_term, search_term, search_term, limit))
            rows = cursor.fetchall()

            return [self._row_to_artifact(row) for row in rows]

    def add_relationship(self, relationship: ArtifactRelationship) -> ArtifactRelationship:
        """Add a relationship between artifacts.

        Args:
            relationship: Relationship metadata

        Returns:
            Relationship with ID
        """
        relationship.id = relationship.id or str(uuid4())

        with sqlite3.connect(self.registry_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO relationships
                (id, from_artifact_id, to_artifact_id, relationship_type, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                relationship.id,
                relationship.from_artifact_id,
                relationship.to_artifact_id,
                relationship.relationship_type,
                relationship.description,
                relationship.created_at.isoformat()
            ))
            conn.commit()

        return relationship

    def get_relationships(self, artifact_id: str) -> list[ArtifactRelationship]:
        """Get all relationships for an artifact.

        Args:
            artifact_id: Artifact ID

        Returns:
            List of relationships
        """
        with sqlite3.connect(self.registry_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM relationships
                WHERE from_artifact_id = ? OR to_artifact_id = ?
                ORDER BY created_at DESC
            """, (artifact_id, artifact_id))
            rows = cursor.fetchall()

            return [self._row_to_relationship(row) for row in rows]

    def get_provenance_graph(self, artifact_id: str, max_depth: int = 3) -> dict[str, Any]:
        """Get provenance graph for an artifact.

        Args:
            artifact_id: Root artifact ID
            max_depth: Maximum depth to traverse

        Returns:
            Graph structure with nodes and edges
        """
        visited = set()
        nodes = []
        edges = []

        def traverse(artifact_id: str, depth: int):
            if depth > max_depth or artifact_id in visited:
                return

            visited.add(artifact_id)
            artifact = self.get_artifact(artifact_id)
            if not artifact:
                return

            nodes.append({
                "id": artifact.id,
                "name": artifact.name,
                "type": artifact.artifact_type.value,
                "uri": artifact.uri,
                "checksum": artifact.checksum
            })

            relationships = self.get_relationships(artifact_id)
            for rel in relationships:
                target_id = rel.to_artifact_id if rel.from_artifact_id == artifact_id else rel.from_artifact_id

                edges.append({
                    "from": rel.from_artifact_id,
                    "to": rel.to_artifact_id,
                    "type": rel.relationship_type,
                    "description": rel.description
                })

                traverse(target_id, depth + 1)

        traverse(artifact_id, 0)

        return {
            "nodes": nodes,
            "edges": edges,
            "root_artifact_id": artifact_id
        }

    def _row_to_artifact(self, row: sqlite3.Row) -> ArtifactMetadata:
        """Convert database row to ArtifactMetadata."""
        return ArtifactMetadata(
            id=row["id"],
            name=row["name"],
            artifact_type=ArtifactType(row["artifact_type"]),
            uri=row["uri"],
            checksum=row["checksum"],
            size_bytes=row["size_bytes"],
            description=row["description"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            status=ArtifactStatus(row["status"])
        )

    def _row_to_relationship(self, row: sqlite3.Row) -> ArtifactRelationship:
        """Convert database row to ArtifactRelationship."""
        return ArtifactRelationship(
            id=row["id"],
            from_artifact_id=row["from_artifact_id"],
            to_artifact_id=row["to_artifact_id"],
            relationship_type=row["relationship_type"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"])
        )


def register_from_receipt(receipt_path: Path, registry: LocalRegistry | None = None) -> list[ArtifactMetadata]:
    """Register artifacts from a Vigil receipt.

    Args:
        receipt_path: Path to receipt JSON file
        registry: Local registry instance

    Returns:
        List of registered artifacts
    """
    if registry is None:
        registry = LocalRegistry()

    with receipt_path.open(encoding="utf-8") as f:
        receipt_data = json.load(f)

    artifacts = []

    # Register output artifacts
    outputs = receipt_data.get("outputs", [])
    for output in outputs:
        if isinstance(output, dict):
            artifact = ArtifactMetadata(
                id=str(uuid4()),
                name=output.get("name", f"artifact_{len(artifacts)}"),
                artifact_type=ArtifactType.OTHER,  # Could be inferred from file extension
                uri=output.get("uri", ""),
                checksum=output.get("checksum", ""),
                size_bytes=output.get("size_bytes"),
                description=f"Artifact from receipt {receipt_path.name}",
                metadata={
                    "receipt_id": receipt_data.get("runletId"),
                    "receipt_path": str(receipt_path)
                }
            )

            registered_artifact = registry.register_artifact(artifact)
            artifacts.append(registered_artifact)

    return artifacts


def cli() -> None:
    """CLI entry point for local registry."""
    import argparse

    parser = argparse.ArgumentParser(description="Local Vigil artifact registry")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register command
    register_parser = subparsers.add_parser("register", help="Register artifacts")
    register_parser.add_argument("--receipt", type=Path, help="Register from receipt")
    register_parser.add_argument("--name", help="Artifact name")
    register_parser.add_argument("--type", choices=[t.value for t in ArtifactType], help="Artifact type")
    register_parser.add_argument("--uri", help="Artifact URI")
    register_parser.add_argument("--checksum", help="Artifact checksum")
    register_parser.add_argument("--description", help="Artifact description")

    # List command
    list_parser = subparsers.add_parser("list", help="List artifacts")
    list_parser.add_argument("--type", choices=[t.value for t in ArtifactType], help="Filter by type")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum results")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search artifacts")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=100, help="Maximum results")

    # Graph command
    graph_parser = subparsers.add_parser("graph", help="Show provenance graph")
    graph_parser.add_argument("artifact_id", help="Artifact ID")
    graph_parser.add_argument("--depth", type=int, default=3, help="Maximum depth")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    registry = LocalRegistry()

    if args.command == "register":
        if args.receipt:
            artifacts = register_from_receipt(args.receipt, registry)
            print(f"Registered {len(artifacts)} artifacts from receipt")
            for artifact in artifacts:
                print(f"  {artifact.id}: {artifact.name}")
        else:
            if not all([args.name, args.type, args.uri, args.checksum]):
                print("Error: --name, --type, --uri, and --checksum are required")
                return

            artifact = ArtifactMetadata(
                id=str(uuid4()),
                name=args.name,
                artifact_type=ArtifactType(args.type),
                uri=args.uri,
                checksum=args.checksum,
                description=args.description
            )

            registered_artifact = registry.register_artifact(artifact)
            print(f"Registered artifact: {registered_artifact.id}")

    elif args.command == "list":
        artifact_type = ArtifactType(args.type) if args.type else None
        artifacts = registry.find_artifacts(artifact_type=artifact_type, limit=args.limit)

        print(f"Found {len(artifacts)} artifacts:")
        for artifact in artifacts:
            print(f"  {artifact.id}: {artifact.name} ({artifact.artifact_type.value})")
            print(f"    URI: {artifact.uri}")
            print(f"    Checksum: {artifact.checksum}")
            if artifact.description:
                print(f"    Description: {artifact.description}")
            print()

    elif args.command == "search":
        artifacts = registry.search_artifacts(args.query, args.limit)

        print(f"Found {len(artifacts)} artifacts matching '{args.query}':")
        for artifact in artifacts:
            print(f"  {artifact.id}: {artifact.name} ({artifact.artifact_type.value})")
            print(f"    URI: {artifact.uri}")
            print()

    elif args.command == "graph":
        graph = registry.get_provenance_graph(args.artifact_id, args.depth)

        print(f"Provenance graph for {args.artifact_id}:")
        print(f"Nodes: {len(graph['nodes'])}")
        print(f"Edges: {len(graph['edges'])}")

        if graph["nodes"]:
            print("\nNodes:")
            for node in graph["nodes"]:
                print(f"  {node['id']}: {node['name']} ({node['type']})")

        if graph["edges"]:
            print("\nEdges:")
            for edge in graph["edges"]:
                print(f"  {edge['from']} -> {edge['to']} ({edge['type']})")


if __name__ == "__main__":
    cli()
