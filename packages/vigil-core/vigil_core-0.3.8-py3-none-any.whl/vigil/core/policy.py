"""Policy enforcement core API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict


class PolicyResult(TypedDict):
    """Policy evaluation result."""

    compliant: bool
    violations: list[str]
    warnings: list[str]
    score: float


class PolicyEngine:
    """Policy enforcement engine."""

    def __init__(self, policies_dir: Path | str = ".vigil/policies"):
        self.policies_dir = Path(policies_dir)
        self.policies_dir.mkdir(parents=True, exist_ok=True)
        self.policies: dict[str, dict[str, Any]] = {}
        self._load_policies()

    def _load_policies(self) -> None:
        """Load policies from the policies directory."""
        for policy_file in self.policies_dir.glob("*.json"):
            try:
                policy_data = json.loads(policy_file.read_text(encoding="utf-8"))
                policy_name = policy_file.stem
                self.policies[policy_name] = policy_data
            except Exception:
                continue

    def add_policy(self, name: str, policy: dict[str, Any]) -> None:
        """Add a policy."""
        self.policies[name] = policy
        policy_file = self.policies_dir / f"{name}.json"
        policy_file.write_text(json.dumps(policy, indent=2), encoding="utf-8")

    def evaluate_receipt(self, receipt: dict[str, Any]) -> PolicyResult:
        """Evaluate a receipt against all policies."""
        violations = []
        warnings = []
        compliant = True

        for policy_name, policy in self.policies.items():
            result = self._evaluate_policy(receipt, policy)
            if not result["compliant"]:
                compliant = False
                violations.extend([f"{policy_name}: {v}" for v in result["violations"]])
            warnings.extend([f"{policy_name}: {w}" for w in result["warnings"]])

        # Calculate compliance score
        total_checks = len(self.policies)
        passed_checks = total_checks - len(violations)
        score = passed_checks / total_checks if total_checks > 0 else 1.0

        return PolicyResult(
            compliant=compliant,
            violations=violations,
            warnings=warnings,
            score=score
        )

    def _evaluate_policy(self, receipt: dict[str, Any], policy: dict[str, Any]) -> PolicyResult:
        """Evaluate a single policy against a receipt."""
        violations = []
        warnings = []

        # Check required fields
        required_fields = policy.get("required_fields", [])
        for field in required_fields:
            if field not in receipt:
                violations.append(f"Missing required field: {field}")

        # Check artifact requirements
        if "artifacts" in policy:
            artifact_policy = policy["artifacts"]
            artifacts = receipt.get("outputs", [])

            # Check minimum number of artifacts
            min_artifacts = artifact_policy.get("min_count", 0)
            if len(artifacts) < min_artifacts:
                violations.append(f"Too few artifacts: {len(artifacts)} < {min_artifacts}")

            # Check artifact types
            allowed_types = artifact_policy.get("allowed_types", [])
            if allowed_types:
                for artifact in artifacts:
                    artifact_type = artifact.get("kind", "unknown")
                    if artifact_type not in allowed_types:
                        violations.append(f"Disallowed artifact type: {artifact_type}")

        # Check environment requirements
        if "environment" in policy:
            env_policy = policy["environment"]
            environment = receipt.get("environment", {})

            # Check Python version
            if "min_python_version" in env_policy:
                min_version = env_policy["min_python_version"]
                python_version = environment.get("python_version", "0.0.0")
                if self._version_compare(python_version, min_version) < 0:
                    violations.append(f"Python version too old: {python_version} < {min_version}")

        # Check git requirements
        if "git" in policy:
            git_policy = policy["git"]
            git_info = receipt.get("git", {})

            # Check for clean working directory
            if git_policy.get("require_clean", False):
                git_status = git_info.get("status", "unknown")
                if git_status != "clean":
                    violations.append("Git working directory is not clean")

        # Check for warnings
        if "warnings" in policy:
            for warning_rule in policy["warnings"]:
                if self._check_warning_rule(receipt, warning_rule):
                    warnings.append(warning_rule.get("message", "Policy warning"))

        return PolicyResult(
            compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            score=1.0 if len(violations) == 0 else 0.0
        )

    def _version_compare(self, version1: str, version2: str) -> int:
        """Compare two version strings."""
        try:
            v1_parts = [int(x) for x in version1.split(".")]
            v2_parts = [int(x) for x in version2.split(".")]

            # Pad with zeros to make same length
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1
            return 0
        except Exception:
            return 0

    def _check_warning_rule(self, receipt: dict[str, Any], rule: dict[str, Any]) -> bool:
        """Check if a warning rule is triggered."""
        # Simple implementation - can be extended
        field = rule.get("field")
        value = rule.get("value")

        if field and value:
            receipt_value = receipt.get(field)
            if receipt_value == value:
                return True

        return False


def create_default_policy() -> dict[str, Any]:
    """Create a default reproducibility policy."""
    return {
        "name": "reproducibility/v1",
        "description": "Basic reproducibility requirements",
        "required_fields": ["id", "owner", "pipeline", "outputs", "environment", "git"],
        "artifacts": {
            "min_count": 1,
            "allowed_types": ["data", "model", "code", "documentation"]
        },
        "environment": {
            "min_python_version": "3.8"
        },
        "git": {
            "require_clean": False
        },
        "warnings": [
            {
                "field": "signature",
                "value": "UNSIGNED-DEV",
                "message": "Receipt is not cryptographically signed"
            }
        ]
    }
