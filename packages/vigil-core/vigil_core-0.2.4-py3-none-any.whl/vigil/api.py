"""Stable Python API for Vigil core functionality."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .tools import audit, cache, deterministic, env, inspect, policy, registry


class VigilCoreAPI:
    """Stable Python API for Vigil core functionality."""

    def __init__(self, project_root: Path | None = None):
        """Initialize Vigil core API.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()
        self._find_vigil_root()

    def _find_vigil_root(self) -> None:
        """Find Vigil project root."""
        current = self.project_root
        while current != current.parent:
            if (current / "vigil.yaml").exists():
                self.project_root = current
                break
            current = current.parent

    def run_pipeline(self, pipeline_config: dict[str, Any] | None = None,
                    reuse_cache: bool = False) -> dict[str, Any]:
        """Run a pipeline and capture metadata.

        Args:
            pipeline_config: Pipeline configuration
            reuse_cache: Whether to reuse cached results

        Returns:
            Pipeline execution result
        """
        # This would integrate with the actual pipeline execution
        # For now, return a mock result
        result = {
            "success": True,
            "runlet_id": f"rl_{int(datetime.now(UTC).timestamp())}",
            "started_at": datetime.now(UTC).isoformat(),
            "finished_at": datetime.now(UTC).isoformat(),
            "inputs": [],
            "outputs": [],
            "metrics": {},
            "environment": {}
        }

        # Log action
        audit.log_action(
            action="run",
            command="vigil run",
            args=[],
            result="success",
            metadata={"reuse_cache": reuse_cache}
        )

        return result

    def generate_receipt(self, run_result: dict[str, Any],
                        parent_receipt: str | None = None) -> dict[str, Any]:
        """Generate a receipt from pipeline execution result.

        Args:
            run_result: Pipeline execution result
            parent_receipt: Parent receipt hash for chaining

        Returns:
            Generated receipt
        """
        # This would integrate with the actual receipt generation
        # For now, return a mock receipt
        receipt = {
            "$schema": "https://vigil.dev/schemas/receipt/v1",
            "schemaVersion": "1.0.0",
            "issuer": "Vigil",
            "runletId": run_result["runlet_id"],
            "vigilUrl": f"vigil://project/run/{run_result['runlet_id']}",
            "gitRef": "unknown",
            "capsuleDigest": "unknown",
            "inputs": run_result["inputs"],
            "outputs": run_result["outputs"],
            "metrics": run_result["metrics"],
            "startedAt": run_result["started_at"],
            "finishedAt": run_result["finished_at"],
            "glyphs": ["RECEIPT"],
            "anchor": None,
            "signature": "UNSIGNED-DEV",
            "parentReceipt": parent_receipt
        }

        # Log action
        audit.log_action(
            action="promote",
            command="vigil promote",
            args=[],
            result="success",
            receipt_id=receipt["runletId"],
            metadata={"parent_receipt": parent_receipt}
        )

        return receipt

    def verify_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]:
        """Verify a receipt's integrity.

        Args:
            receipt: Receipt to verify

        Returns:
            Verification result
        """
        # This would integrate with the actual verification
        # For now, return a mock result
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checksum_valid": True,
            "signature_valid": True,
            "schema_valid": True
        }

        # Log action
        audit.log_action(
            action="verify",
            command="vigil verify",
            args=[],
            result="success" if result["valid"] else "failed",
            receipt_id=receipt.get("runletId"),
            metadata=result
        )

        return result

    def capture_environment(self) -> dict[str, Any]:
        """Capture current environment snapshot.

        Returns:
            Environment snapshot
        """
        return env.capture_full_environment()

    def compare_environments(self, env1: dict[str, Any],
                           env2: dict[str, Any]) -> dict[str, Any]:
        """Compare two environment snapshots.

        Args:
            env1: First environment
            env2: Second environment

        Returns:
            Comparison result
        """
        return env.compare_environments(env1, env2)

    def evaluate_policy(self, receipt: dict[str, Any],
                       policy_dir: Path | None = None) -> dict[str, Any]:
        """Evaluate receipt against policies.

        Args:
            receipt: Receipt to evaluate
            policy_dir: Policy directory

        Returns:
            Policy evaluation result
        """
        # Create temporary receipt file
        temp_receipt = Path(".vigil/temp_receipt.json")
        temp_receipt.parent.mkdir(parents=True, exist_ok=True)

        with temp_receipt.open("w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)

        try:
            result = policy.evaluate_receipt_policy(temp_receipt, policy_dir)
            return {
                "passed": result.passed,
                "violations": [
                    {
                        "rule_id": v.rule_id,
                        "severity": v.severity.value,
                        "message": v.message,
                        "details": v.details
                    }
                    for v in result.violations
                ],
                "summary": result.summary
            }
        finally:
            temp_receipt.unlink(missing_ok=True)

    def inspect_artifact(self, artifact_path: Path,
                        verbose: bool = False) -> dict[str, Any]:
        """Inspect an artifact.

        Args:
            artifact_path: Path to artifact
            verbose: Verbose output

        Returns:
            Inspection result
        """
        return inspect.inspect_artifact(artifact_path, verbose)

    def inspect_receipt(self, receipt_path: Path,
                       verbose: bool = False) -> dict[str, Any]:
        """Inspect a receipt.

        Args:
            receipt_path: Path to receipt
            verbose: Verbose output

        Returns:
            Inspection result
        """
        return inspect.inspect_receipt(receipt_path, verbose)

    def inspect_project(self, project_path: Path | None = None,
                       verbose: bool = False) -> dict[str, Any]:
        """Inspect a project.

        Args:
            project_path: Project path
            verbose: Verbose output

        Returns:
            Inspection result
        """
        if project_path is None:
            project_path = self.project_root
        return inspect.inspect_project(project_path, verbose)

    def register_artifact(self, artifact_metadata: dict[str, Any]) -> str:
        """Register an artifact in local registry.

        Args:
            artifact_metadata: Artifact metadata

        Returns:
            Artifact ID
        """
        local_registry = registry.LocalRegistry()

        # Convert dict to ArtifactMetadata
        artifact = registry.ArtifactMetadata(
            id=artifact_metadata.get("id"),
            name=artifact_metadata["name"],
            artifact_type=registry.ArtifactType(artifact_metadata["type"]),
            uri=artifact_metadata["uri"],
            checksum=artifact_metadata["checksum"],
            size_bytes=artifact_metadata.get("size_bytes"),
            description=artifact_metadata.get("description"),
            tags=artifact_metadata.get("tags", []),
            metadata=artifact_metadata.get("metadata", {})
        )

        registered_artifact = local_registry.register_artifact(artifact)
        return registered_artifact.id

    def get_provenance_graph(self, artifact_id: str,
                           max_depth: int = 3) -> dict[str, Any]:
        """Get provenance graph for an artifact.

        Args:
            artifact_id: Artifact ID
            max_depth: Maximum depth

        Returns:
            Provenance graph
        """
        local_registry = registry.LocalRegistry()
        return local_registry.get_provenance_graph(artifact_id, max_depth)

    def get_cache_entry(self, inputs: list[dict[str, Any]],
                       environment: dict[str, Any]) -> dict[str, Any] | None:
        """Get cached pipeline execution.

        Args:
            inputs: Pipeline inputs
            environment: Environment metadata

        Returns:
            Cache entry if found
        """
        cache_manager = cache.ReproducibilityCache()
        entry = cache_manager.get_cache_entry(inputs, environment)

        if entry:
            return {
                "cache_id": entry.cache_id,
                "inputs_hash": entry.inputs_hash,
                "outputs": entry.outputs,
                "receipt_id": entry.receipt_id,
                "created_at": entry.created_at.isoformat(),
                "metadata": entry.metadata
            }

        return None

    def store_cache_entry(self, inputs: list[dict[str, Any]],
                         environment: dict[str, Any],
                         outputs: list[dict[str, Any]],
                         receipt_id: str,
                         metadata: dict[str, Any]) -> str:
        """Store pipeline execution in cache.

        Args:
            inputs: Pipeline inputs
            environment: Environment metadata
            outputs: Pipeline outputs
            receipt_id: Receipt ID
            metadata: Additional metadata

        Returns:
            Cache ID
        """
        cache_manager = cache.ReproducibilityCache()
        return cache_manager.store_cache_entry(
            inputs, environment, outputs, receipt_id, metadata
        )

    def get_audit_entries(self, action: str | None = None,
                         limit: int = 100) -> list[dict[str, Any]]:
        """Get audit log entries.

        Args:
            action: Filter by action
            limit: Maximum entries

        Returns:
            List of audit entries
        """
        audit_logger = audit.get_audit_logger()
        entries = audit_logger.get_entries(action, limit)

        return [entry.to_dict() for entry in entries]

    def set_deterministic_mode(self, seed: int | None = None,
                              fixed_time: datetime | None = None) -> None:
        """Set deterministic mode for reproducible execution.

        Args:
            seed: Random seed
            fixed_time: Fixed timestamp
        """
        deterministic.set_deterministic_environment(seed, fixed_time)


# Convenience functions for common operations
def run_pipeline(pipeline_config: dict[str, Any] | None = None,
                reuse_cache: bool = False) -> dict[str, Any]:
    """Run a pipeline and capture metadata."""
    api = VigilCoreAPI()
    return api.run_pipeline(pipeline_config, reuse_cache)


def generate_receipt(run_result: dict[str, Any],
                    parent_receipt: str | None = None) -> dict[str, Any]:
    """Generate a receipt from pipeline execution result."""
    api = VigilCoreAPI()
    return api.generate_receipt(run_result, parent_receipt)


def verify_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Verify a receipt's integrity."""
    api = VigilCoreAPI()
    return api.verify_receipt(receipt)


def capture_environment() -> dict[str, Any]:
    """Capture current environment snapshot."""
    api = VigilCoreAPI()
    return api.capture_environment()


def compare_environments(env1: dict[str, Any], env2: dict[str, Any]) -> dict[str, Any]:
    """Compare two environment snapshots."""
    api = VigilCoreAPI()
    return api.compare_environments(env1, env2)


def evaluate_policy(receipt: dict[str, Any],
                   policy_dir: Path | None = None) -> dict[str, Any]:
    """Evaluate receipt against policies."""
    api = VigilCoreAPI()
    return api.evaluate_policy(receipt, policy_dir)


def inspect_artifact(artifact_path: Path, verbose: bool = False) -> dict[str, Any]:
    """Inspect an artifact."""
    api = VigilCoreAPI()
    return api.inspect_artifact(artifact_path, verbose)


def inspect_receipt(receipt_path: Path, verbose: bool = False) -> dict[str, Any]:
    """Inspect a receipt."""
    api = VigilCoreAPI()
    return api.inspect_receipt(receipt_path, verbose)


def inspect_project(project_path: Path | None = None,
                   verbose: bool = False) -> dict[str, Any]:
    """Inspect a project."""
    api = VigilCoreAPI()
    return api.inspect_project(project_path, verbose)


def register_artifact(artifact_metadata: dict[str, Any]) -> str:
    """Register an artifact in local registry."""
    api = VigilCoreAPI()
    return api.register_artifact(artifact_metadata)


def get_provenance_graph(artifact_id: str, max_depth: int = 3) -> dict[str, Any]:
    """Get provenance graph for an artifact."""
    api = VigilCoreAPI()
    return api.get_provenance_graph(artifact_id, max_depth)


def get_cache_entry(inputs: list[dict[str, Any]],
                   environment: dict[str, Any]) -> dict[str, Any] | None:
    """Get cached pipeline execution."""
    api = VigilCoreAPI()
    return api.get_cache_entry(inputs, environment)


def store_cache_entry(inputs: list[dict[str, Any]],
                     environment: dict[str, Any],
                     outputs: list[dict[str, Any]],
                     receipt_id: str,
                     metadata: dict[str, Any]) -> str:
    """Store pipeline execution in cache."""
    api = VigilCoreAPI()
    return api.store_cache_entry(inputs, environment, outputs, receipt_id, metadata)


def get_audit_entries(action: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """Get audit log entries."""
    api = VigilCoreAPI()
    return api.get_audit_entries(action, limit)


def set_deterministic_mode(seed: int | None = None,
                          fixed_time: datetime | None = None) -> None:
    """Set deterministic mode for reproducible execution."""
    api = VigilCoreAPI()
    api.set_deterministic_mode(seed, fixed_time)
