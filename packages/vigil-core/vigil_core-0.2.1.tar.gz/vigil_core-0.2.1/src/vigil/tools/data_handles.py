"""Utilities for linting Vigil data handle descriptors."""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table


class LintSeverity(str, Enum):
    """Severity level for data handle lint issues."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass(slots=True)
class LintIssue:
    """Structured representation of a lint issue."""

    code: str
    severity: LintSeverity
    message: str
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
        }
        if self.details:
            payload["details"] = self.details
        return payload


@dataclass(slots=True)
class HandleReport:
    """Result of linting a single handle descriptor."""

    path: Path
    issues: list[LintIssue]

    @property
    def status(self) -> LintSeverity:
        if any(issue.severity is LintSeverity.ERROR for issue in self.issues):
            return LintSeverity.ERROR
        if any(issue.severity is LintSeverity.WARNING for issue in self.issues):
            return LintSeverity.WARNING
        return LintSeverity.OK

    def to_dict(self, *, base_path: Path) -> dict[str, Any]:
        try:
            handle_path = self.path.relative_to(base_path)
        except ValueError:
            handle_path = self.path
        return {
            "handle": handle_path.as_posix(),
            "status": self.status.value,
            "issues": [issue.to_dict() for issue in self.issues],
        }


_KNOWN_FORMATS = {
    "csv",
    "parquet",
    "json",
    "ndjson",
    "tsv",
    "vcf",
    "bgen",
    "zarr",
    "ome-ngff",
    "ome-tiff",
    "tiff",
    "ome.zarr",
    "feather",
    "arrow",
}

_RECOMMENDED_CONSENT_LEVELS = {
    "public",
    "internal",
    "restricted",
    "controlled",
    "de-identified",
    "research",
}


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("Handle must contain a top-level JSON object")
    return payload


def _validate_schema(schema: Any) -> tuple[list[str], list[LintIssue]]:
    """Validate schema block and return extracted column names."""

    issues: list[LintIssue] = []
    columns: list[str] = []

    if not isinstance(schema, dict):
        issues.append(
            LintIssue(
                code="schema_type",
                severity=LintSeverity.ERROR,
                message="schema must be an object",
                details={"found": type(schema).__name__},
            )
        )
        return columns, issues

    if "columns" in schema and isinstance(schema["columns"], dict):
        for name, dtype in schema["columns"].items():
            if not isinstance(name, str) or not isinstance(dtype, str):
                issues.append(
                    LintIssue(
                        code="schema_columns",
                        severity=LintSeverity.ERROR,
                        message="schema.columns must map string names to string types",
                    )
                )
                return columns, issues
            columns.append(name)
        return columns, issues

    if "fields" in schema and isinstance(schema["fields"], list):
        for field in schema["fields"]:
            if not isinstance(field, dict):
                issues.append(
                    LintIssue(
                        code="schema_fields",
                        severity=LintSeverity.ERROR,
                        message="schema.fields must contain objects",
                    )
                )
                return columns, issues
            name = field.get("name")
            dtype = field.get("type")
            if not isinstance(name, str) or not isinstance(dtype, str):
                issues.append(
                    LintIssue(
                        code="schema_field_entries",
                        severity=LintSeverity.ERROR,
                        message="schema.fields entries must provide string name/type",
                    )
                )
                return columns, issues
            columns.append(name)
        return columns, issues

    # Accept shorthand mapping of column->type
    if all(isinstance(name, str) and isinstance(dtype, str) for name, dtype in schema.items()):
        columns.extend(schema.keys())
        return columns, issues

    issues.append(
        LintIssue(
            code="schema_shape",
            severity=LintSeverity.ERROR,
            message="schema must provide 'columns', 'fields', or a mapping of column names",
        )
    )
    return columns, issues


def _lint_handle(path: Path, *, project_root: Path) -> HandleReport:
    issues: list[LintIssue] = []

    try:
        payload = _load_json(path)
    except ValueError as exc:
        issues.append(
            LintIssue(
                code="invalid_json",
                severity=LintSeverity.ERROR,
                message=str(exc),
            )
        )
        return HandleReport(path=path, issues=issues)

    offline = payload.get("offline_fallback")
    if not isinstance(offline, str) or not offline:
        issues.append(
            LintIssue(
                code="offline_fallback",
                severity=LintSeverity.ERROR,
                message="offline_fallback must be a non-empty string",
            )
        )
    else:
        offline_path = (project_root / offline).resolve()
        try:
            offline_path.relative_to(project_root)
        except ValueError:
            issues.append(
                LintIssue(
                    code="offline_scope",
                    severity=LintSeverity.ERROR,
                    message="offline_fallback must stay within the project",
                    details={"offline_fallback": offline},
                )
            )
        else:
            if not offline_path.exists():
                issues.append(
                    LintIssue(
                        code="offline_exists",
                        severity=LintSeverity.WARNING,
                        message="offline_fallback does not exist on disk",
                        details={"offline_fallback": offline},
                    )
                )

    schema = payload.get("schema")
    if schema is None:
        issues.append(
            LintIssue(
                code="schema_missing",
                severity=LintSeverity.ERROR,
                message="schema section is required",
            )
        )
    else:
        columns, schema_issues = _validate_schema(schema)
        issues.extend(schema_issues)
        if columns:
            unique = len(set(columns))
            if unique != len(columns):
                issues.append(
                    LintIssue(
                        code="schema_duplicates",
                        severity=LintSeverity.WARNING,
                        message="schema defines duplicate column names",
                        details={"columns": columns},
                    )
                )

    fmt = payload.get("format")
    if fmt is None or not isinstance(fmt, str):
        issues.append(
            LintIssue(
                code="format_missing",
                severity=LintSeverity.WARNING,
                message="format should be provided as a string",
            )
        )
    elif fmt.lower() not in _KNOWN_FORMATS:
        issues.append(
            LintIssue(
                code="format_unknown",
                severity=LintSeverity.WARNING,
                message=f"Unrecognized format '{fmt}'. Update _KNOWN_FORMATS if this is expected.",
            )
        )

    uri = payload.get("uri")
    if uri is not None and not isinstance(uri, str):
        issues.append(
            LintIssue(
                code="uri_type",
                severity=LintSeverity.ERROR,
                message="uri must be a string when provided",
            )
        )

    redact_columns = payload.get("redact_columns")
    if redact_columns is not None:
        if not isinstance(redact_columns, list) or not all(isinstance(item, str) for item in redact_columns):
            issues.append(
                LintIssue(
                    code="redact_columns",
                    severity=LintSeverity.ERROR,
                    message="redact_columns must be a list of strings",
                )
            )

    consent = payload.get("consent")
    if consent is None:
        issues.append(
            LintIssue(
                code="consent_missing",
                severity=LintSeverity.WARNING,
                message="consent metadata is recommended",
            )
        )
    elif isinstance(consent, str):
        if consent.lower() not in _RECOMMENDED_CONSENT_LEVELS:
            issues.append(
                LintIssue(
                    code="consent_level",
                    severity=LintSeverity.WARNING,
                    message="consent level is not in the recommended set",
                    details={"consent": consent},
                )
            )
    elif not isinstance(consent, dict):
        issues.append(
            LintIssue(
                code="consent_type",
                severity=LintSeverity.WARNING,
                message="consent should be a string or object",
                details={"found": type(consent).__name__},
            )
        )

    use_restrictions = payload.get("use_restrictions")
    if use_restrictions is not None:
        if not isinstance(use_restrictions, list) or not all(
            isinstance(item, str) for item in use_restrictions
        ):
            issues.append(
                LintIssue(
                    code="use_restrictions",
                    severity=LintSeverity.ERROR,
                    message="use_restrictions must be a list of strings",
                )
            )

    for bool_field in ("pii", "sensitive"):
        if bool_field in payload and not isinstance(payload[bool_field], bool):
            issues.append(
                LintIssue(
                    code=f"{bool_field}_type",
                    severity=LintSeverity.ERROR,
                    message=f"{bool_field} must be a boolean",
                )
            )

    return HandleReport(path=path, issues=issues)


def lint_handles(
    paths: Sequence[Path] | None,
    *,
    base_path: Path | None = None,
) -> list[HandleReport]:
    """Lint all provided handles (or default directories when None)."""

    project_root = (base_path or Path.cwd()).resolve()

    candidates: list[Path] = []
    if not paths:
        default_dir = project_root / "app" / "data" / "handles"
        if default_dir.exists():
            candidates.extend(sorted(default_dir.glob("*.dhandle.json")))
    else:
        for entry in paths:
            resolved = entry if entry.is_absolute() else (project_root / entry)
            if resolved.is_dir():
                candidates.extend(sorted(resolved.glob("*.dhandle.json")))
            elif resolved.suffixes[-2:] == [".dhandle", ".json"] or resolved.name.endswith(
                ".dhandle.json"
            ):
                candidates.append(resolved)

    # Deduplicate while preserving order
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in candidates:
        path = path.resolve()
        if path not in seen:
            seen.add(path)
            ordered.append(path)

    return [_lint_handle(path, project_root=project_root) for path in ordered]


def build_report(results: Iterable[HandleReport], *, base_path: Path | None = None) -> dict[str, Any]:
    """Build a machine-readable report from lint results."""

    base = (base_path or Path.cwd()).resolve()
    results_list = list(results)
    summary_counts = {
        LintSeverity.OK: 0,
        LintSeverity.WARNING: 0,
        LintSeverity.ERROR: 0,
    }
    for result in results_list:
        summary_counts[result.status] += 1

    if summary_counts[LintSeverity.ERROR] > 0:
        status = LintSeverity.ERROR
    elif summary_counts[LintSeverity.WARNING] > 0:
        status = LintSeverity.WARNING
    else:
        status = LintSeverity.OK

    return {
        "summary": {
            "status": status.value,
            "handles": len(results_list),
            "ok": summary_counts[LintSeverity.OK],
            "warnings": summary_counts[LintSeverity.WARNING],
            "errors": summary_counts[LintSeverity.ERROR],
        },
        "results": [result.to_dict(base_path=base) for result in results_list],
    }


def display_report(report: dict[str, Any]) -> None:
    table = Table(title="Data Handle Lint Report")
    table.add_column("Handle")
    table.add_column("Status")
    table.add_column("Issues", overflow="fold")

    for result in report.get("results", []):
        issues = result.get("issues", [])
        if not issues:
            issue_text = "(clean)"
        else:
            issue_text = "\n".join(
                f"[{issue['severity']}] {issue['code']}: {issue['message']}"
                for issue in issues
            )
        table.add_row(result.get("handle", "?"), result.get("status", "?"), issue_text)

    console = Console()
    console.print(table)

    summary = report.get("summary", {})
    footer = (
        f"Overall: {summary.get('status', '?')} • "
        f"handles={summary.get('handles', 0)} "
        f"warnings={summary.get('warnings', 0)} "
        f"errors={summary.get('errors', 0)}"
    )
    console.print(footer)


def _severity_threshold(value: str) -> LintSeverity | None:
    normalized = value.strip().lower()
    if normalized == "never":
        return None
    if normalized == "warning":
        return LintSeverity.WARNING
    if normalized == "error":
        return LintSeverity.ERROR
    raise typer.BadParameter("fail-on must be one of: never, warning, error")


@dataclass(slots=True)
class LintOptions:
    output_format: str
    fail_on: str
    paths: list[Path]


def run_lint(options: LintOptions) -> tuple[dict[str, Any], int]:
    """Run lint with options, returning report and exit code."""

    results = lint_handles(options.paths)
    report = build_report(results)

    threshold = _severity_threshold(options.fail_on)
    status = report["summary"]["status"]
    status_enum = LintSeverity(status)

    exit_code = 0
    if threshold is not None and status_enum.value != "ok":
        if status_enum is LintSeverity.ERROR:
            exit_code = 1
        elif status_enum is LintSeverity.WARNING and threshold is LintSeverity.WARNING:
            exit_code = 1

    return report, exit_code


def main(
    paths: list[Path] = typer.Argument(  # noqa: B008 - Typer callback
        None,
        help="Specific handle files or directories to lint (defaults to app/data/handles)",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        case_sensitive=False,
        help="Output format: table or json",
    ),
    fail_on: str = typer.Option(
        "error",
        "--fail-on",
        help="Fail on 'error', 'warning', or 'never'",
    ),
) -> None:
    """Lint Vigil data handle descriptors."""

    options = LintOptions(output_format=output_format, fail_on=fail_on, paths=paths or [])
    report, exit_code = run_lint(options)

    if options.output_format.lower() == "json":
        typer.echo(json.dumps(report, indent=2))
    else:
        display_report(report)

    raise typer.Exit(code=exit_code)


if __name__ == "__main__":  # pragma: no cover - manual invocation helper
    typer.run(main)
