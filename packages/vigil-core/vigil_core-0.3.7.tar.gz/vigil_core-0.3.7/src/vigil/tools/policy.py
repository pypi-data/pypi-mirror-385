"""Policy enforcement utilities for Vigil receipts and artifacts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class PolicySeverity(str, Enum):
    """Policy violation severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class PolicyViolation:
    """Represents a policy violation."""

    rule_id: str
    severity: PolicySeverity
    message: str
    details: dict[str, Any] | None = None
    artifact_path: Path | None = None


@dataclass
class PolicyResult:
    """Result of policy evaluation."""

    passed: bool
    violations: list[PolicyViolation]
    summary: dict[str, int]


class PolicyEngine:
    """Local policy evaluation engine."""

    def __init__(self, policy_dir: Path | None = None):
        """Initialize policy engine.

        Args:
            policy_dir: Directory containing policy files (.json, .yaml, .rego)
        """
        self.policy_dir = policy_dir or Path(".vigil/policies")
        self.policies: dict[str, dict[str, Any]] = {}
        self._load_policies()

    def _load_policies(self) -> None:
        """Load policy files from the policy directory."""
        if not self.policy_dir.exists():
            return

        for policy_file in self.policy_dir.glob("*.{json,yaml,yml}"):
            try:
                with policy_file.open(encoding="utf-8") as f:
                    if policy_file.suffix in [".yaml", ".yml"]:
                        policy_data = yaml.safe_load(f)
                    else:
                        policy_data = json.load(f)

                if isinstance(policy_data, dict):
                    policy_name = policy_file.stem
                    self.policies[policy_name] = policy_data
            except Exception as e:
                print(f"Warning: Failed to load policy {policy_file}: {e}")

    def evaluate_receipt(self, receipt_path: Path) -> PolicyResult:
        """Evaluate a receipt against all loaded policies.

        Args:
            receipt_path: Path to receipt JSON file

        Returns:
            Policy evaluation result
        """
        violations: list[PolicyViolation] = []

        if not receipt_path.exists():
            violations.append(PolicyViolation(
                rule_id="receipt_exists",
                severity=PolicySeverity.ERROR,
                message=f"Receipt file not found: {receipt_path}",
                artifact_path=receipt_path
            ))
            return PolicyResult(passed=False, violations=violations, summary={"error": 1})

        try:
            with receipt_path.open(encoding="utf-8") as f:
                receipt_data = json.load(f)
        except json.JSONDecodeError as e:
            violations.append(PolicyViolation(
                rule_id="receipt_valid_json",
                severity=PolicySeverity.ERROR,
                message=f"Invalid JSON in receipt: {e}",
                artifact_path=receipt_path
            ))
            return PolicyResult(passed=False, violations=violations, summary={"error": 1})

        # Evaluate against each policy
        for policy_name, policy_config in self.policies.items():
            policy_violations = self._evaluate_policy(policy_name, policy_config, receipt_data, receipt_path)
            violations.extend(policy_violations)

        # Calculate summary
        summary = {"error": 0, "warning": 0, "info": 0}
        for violation in violations:
            summary[violation.severity.value] += 1

        passed = summary["error"] == 0
        return PolicyResult(passed=passed, violations=violations, summary=summary)

    def _evaluate_policy(self, policy_name: str, policy_config: dict[str, Any],
                        receipt_data: dict[str, Any], receipt_path: Path) -> list[PolicyViolation]:
        """Evaluate a single policy against receipt data."""
        violations: list[PolicyViolation] = []

        # Extract policy rules
        rules = policy_config.get("rules", [])
        if not isinstance(rules, list):
            return violations

        for rule in rules:
            rule_id = rule.get("id", f"{policy_name}_rule")
            severity_str = rule.get("severity", "error")
            try:
                severity = PolicySeverity(severity_str)
            except ValueError:
                severity = PolicySeverity.ERROR

            # Evaluate rule conditions
            conditions = rule.get("conditions", [])
            for condition in conditions:
                violation = self._evaluate_condition(rule_id, severity, condition, receipt_data, receipt_path)
                if violation:
                    violations.append(violation)

        return violations

    def _evaluate_condition(self, rule_id: str, severity: PolicySeverity,
                          condition: dict[str, Any], receipt_data: dict[str, Any],
                          receipt_path: Path) -> PolicyViolation | None:
        """Evaluate a single condition."""
        condition_type = condition.get("type")

        if condition_type == "required_field":
            field_path = condition.get("field")
            if field_path and not self._field_exists(receipt_data, field_path):
                return PolicyViolation(
                    rule_id=rule_id,
                    severity=severity,
                    message=f"Required field missing: {field_path}",
                    details={"field": field_path},
                    artifact_path=receipt_path
                )

        elif condition_type == "field_pattern":
            field_path = condition.get("field")
            pattern = condition.get("pattern")
            if field_path and pattern:
                field_value = self._get_field_value(receipt_data, field_path)
                if field_value and not re.match(pattern, str(field_value)):
                    return PolicyViolation(
                        rule_id=rule_id,
                        severity=severity,
                        message=f"Field pattern mismatch: {field_path}",
                        details={"field": field_path, "pattern": pattern, "value": field_value},
                        artifact_path=receipt_path
                    )

        elif condition_type == "environment_version":
            min_version = condition.get("min_version")
            env_version = self._get_field_value(receipt_data, "environment.python_version")
            if min_version and env_version and not self._version_gte(env_version, min_version):
                return PolicyViolation(
                    rule_id=rule_id,
                    severity=severity,
                    message=f"Python version too old: {env_version} < {min_version}",
                    details={"current": env_version, "minimum": min_version},
                    artifact_path=receipt_path
                )

        elif condition_type == "checksum_present":
            outputs = self._get_field_value(receipt_data, "outputs")
            if outputs and isinstance(outputs, list):
                for output in outputs:
                    if isinstance(output, dict) and not output.get("checksum"):
                        return PolicyViolation(
                            rule_id=rule_id,
                            severity=severity,
                            message="Output artifact missing checksum",
                            details={"output": output},
                            artifact_path=receipt_path
                        )

        elif condition_type == "signature_required":
            signature = self._get_field_value(receipt_data, "signature")
            if not signature or signature == "UNSIGNED-DEV":
                return PolicyViolation(
                    rule_id=rule_id,
                    severity=severity,
                    message="Receipt must be signed",
                    details={"signature": signature},
                    artifact_path=receipt_path
                )

        return None

    def _field_exists(self, data: dict[str, Any], field_path: str) -> bool:
        """Check if a field exists in nested data."""
        return self._get_field_value(data, field_path) is not None

    def _get_field_value(self, data: dict[str, Any], field_path: str) -> Any:
        """Get value from nested data using dot notation."""
        keys = field_path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def _version_gte(self, version1: str, version2: str) -> bool:
        """Compare version strings (simple semantic versioning)."""
        try:
            v1_parts = [int(x) for x in version1.split(".")]
            v2_parts = [int(x) for x in version2.split(".")]

            # Pad with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            return v1_parts >= v2_parts
        except ValueError:
            return False


def evaluate_receipt_policy(receipt_path: Path, policy_dir: Path | None = None) -> PolicyResult:
    """Evaluate a receipt against policies.

    Args:
        receipt_path: Path to receipt JSON file
        policy_dir: Directory containing policy files

    Returns:
        Policy evaluation result
    """
    engine = PolicyEngine(policy_dir)
    return engine.evaluate_receipt(receipt_path)


def create_default_policy(policy_dir: Path) -> None:
    """Create default policy files.

    Args:
        policy_dir: Directory to create policies in
    """
    policy_dir.mkdir(parents=True, exist_ok=True)

    # Basic compliance policy
    basic_policy = {
        "name": "Basic Compliance",
        "description": "Basic requirements for Vigil receipts",
        "rules": [
            {
                "id": "required_fields",
                "severity": "error",
                "conditions": [
                    {
                        "type": "required_field",
                        "field": "issuer"
                    },
                    {
                        "type": "required_field",
                        "field": "runletId"
                    },
                    {
                        "type": "required_field",
                        "field": "outputs"
                    }
                ]
            },
            {
                "id": "checksums_required",
                "severity": "error",
                "conditions": [
                    {
                        "type": "checksum_present"
                    }
                ]
            }
        ]
    }

    with (policy_dir / "basic_compliance.json").open("w", encoding="utf-8") as f:
        json.dump(basic_policy, f, indent=2)

    # Production policy
    production_policy = {
        "name": "Production Requirements",
        "description": "Strict requirements for production receipts",
        "rules": [
            {
                "id": "signature_required",
                "severity": "error",
                "conditions": [
                    {
                        "type": "signature_required"
                    }
                ]
            },
            {
                "id": "python_version",
                "severity": "warning",
                "conditions": [
                    {
                        "type": "environment_version",
                        "min_version": "3.11"
                    }
                ]
            }
        ]
    }

    with (policy_dir / "production.json").open("w", encoding="utf-8") as f:
        json.dump(production_policy, f, indent=2)


def cli() -> None:
    """CLI entry point for policy evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate Vigil receipts against policies")
    parser.add_argument("receipt", type=Path, help="Path to receipt JSON file")
    parser.add_argument("--policy-dir", type=Path, help="Directory containing policy files")
    parser.add_argument("--create-default", action="store_true", help="Create default policy files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.create_default:
        policy_dir = args.policy_dir or Path(".vigil/policies")
        create_default_policy(policy_dir)
        print(f"Created default policies in {policy_dir}")
        return

    result = evaluate_receipt_policy(args.receipt, args.policy_dir)

    if result.passed:
        print("✅ Policy evaluation passed")
    else:
        print("❌ Policy evaluation failed")

    if args.verbose or not result.passed:
        for violation in result.violations:
            severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[violation.severity.value]
            print(f"{severity_icon} {violation.rule_id}: {violation.message}")
            if violation.details:
                print(f"   Details: {violation.details}")

    print(f"Summary: {result.summary}")

    if not result.passed:
        exit(1)


if __name__ == "__main__":
    cli()
