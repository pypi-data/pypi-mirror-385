"""Utilities for generating Vigil Suggestion Cells from workflow context."""

from __future__ import annotations

import difflib
import json
import shlex
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import yaml

from ..lib.paths import PROJECT_ROOT, project_path

SNAKEFILE = project_path("app/code/pipelines/Snakefile")
PARAMS_PATH = project_path("app/code/configs/params.yaml")


@dataclass(slots=True)
class _CommandResult:
    ok: bool
    stdout: str
    stderr: str

    def merged(self) -> str:
        """Return stdout/stderr joined in a single string."""
        pieces = [self.stdout.strip(), self.stderr.strip()]
        merged = "\n".join(part for part in pieces if part).strip()
        return merged or "(no output)"


def _run_command(parts: Iterable[str]) -> _CommandResult:
    """Execute a command, capturing stdout/stderr without raising."""

    proc = subprocess.run(
        list(parts),
        check=False,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    return _CommandResult(proc.returncode == 0, proc.stdout, proc.stderr)


def _snakemake_base_args(targets: Iterable[str], profile: str | None) -> list[str]:
    args = ["uv", "run", "snakemake", "-s", str(SNAKEFILE)]
    args.extend(targets)
    if profile:
        args.extend(["--profile", profile])
    return args


def _render_targets(panel_state: dict[str, Any]) -> list[str]:
    raw_targets = panel_state.get("targets")
    if isinstance(raw_targets, str):
        return [*shlex.split(raw_targets)]
    if isinstance(raw_targets, Iterable):
        return [str(item) for item in raw_targets]

    single_target = panel_state.get("target", "all")
    if isinstance(single_target, str):
        return [*shlex.split(single_target)]
    return ["all"]


def _summarize_output(output: str, limit: int = 24) -> str:
    lines = [line.rstrip() for line in output.splitlines() if line.strip()]
    if not lines:
        return "(no output)"
    if len(lines) <= limit:
        return "\n".join(lines)
    clipped = lines[:limit]
    clipped.append(f"… ({len(lines) - limit} more lines clipped)")
    return "\n".join(clipped)


def _read_params() -> dict[str, Any]:
    if not PARAMS_PATH.exists():
        return {}
    try:
        data = yaml.safe_load(PARAMS_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return {}
    return data or {}


def _get_nested(data: dict[str, Any], keys: Iterable[str]) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _infer_param_updates(params: dict[str, Any], panel_state: dict[str, Any]) -> list[tuple[list[str], Any, Any]]:
    updates: list[tuple[list[str], Any, Any]] = []
    suggestions = panel_state.get("paramSuggestions")
    if isinstance(suggestions, dict):
        for dotted_key, value in suggestions.items():
            if value is None:
                continue
            if isinstance(dotted_key, str):
                keys = [part for part in dotted_key.split(".") if part]
            elif isinstance(dotted_key, Iterable):
                keys = [str(part) for part in dotted_key]
            else:
                continue
            if not keys:
                continue
            current_value = _get_nested(params, keys)
            if current_value == value:
                continue
            updates.append((keys, current_value, value))

    # Heuristic adjustment for process.threshold if metrics are provided.
    metrics = panel_state.get("metrics")
    desired_threshold = panel_state.get("suggestedThreshold")
    if desired_threshold is None and isinstance(metrics, dict):
        observed_precision = metrics.get("precision") or metrics.get("observed_precision")
        target_precision = (
            metrics.get("target_precision")
            or panel_state.get("targetPrecision")
            or panel_state.get("desiredPrecision")
        )
        try:
            observed = float(observed_precision)
            target = float(target_precision)
        except (TypeError, ValueError):
            observed = target = None
        current_threshold = _get_nested(params, ["process", "threshold"])
        try:
            current_threshold_value = float(current_threshold)
        except (TypeError, ValueError):
            current_threshold_value = None
        if (
            observed is not None
            and target is not None
            and current_threshold_value is not None
        ):
            delta = target - observed
            if abs(delta) > 0.01:
                # Adjust threshold in the opposite direction of precision delta.
                adjustment = 0.05 if delta < 0 else -0.05
                desired_threshold = round(current_threshold_value + adjustment, 3)

    if desired_threshold is None:
        current_threshold = _get_nested(params, ["process", "threshold"])
        try:
            current_threshold_value = float(current_threshold)
        except (TypeError, ValueError):
            current_threshold_value = None
        if current_threshold_value is not None:
            desired_threshold = round(current_threshold_value + 0.05, 3)

    if desired_threshold is not None:
        current_threshold = _get_nested(params, ["process", "threshold"])
        if current_threshold != desired_threshold:
            updates.append(([
                "process",
                "threshold",
            ], current_threshold, desired_threshold))

    # Remove duplicates preserving last suggestion.
    seen: dict[tuple[str, ...], tuple[Any, Any]] = {}
    for keys, current_value, new_value in updates:
        seen[tuple(keys)] = (current_value, new_value)

    deduped: list[tuple[list[str], Any, Any]] = []
    for keys_tuple, (current_value, new_value) in seen.items():
        deduped.append((list(keys_tuple), current_value, new_value))
    return deduped


def _format_updates_block(updates: list[tuple[list[str], Any, Any]]) -> str:
    if not updates:
        return "print(\"No parameter changes recommended; review DAG notes above.\")"

    lines: list[str] = [
        "from __future__ import annotations",
        "from pathlib import Path",
        "from typing import Any",
        "import yaml",
        "",
        f"params_path = Path('{PARAMS_PATH.as_posix()}')",
        "params = yaml.safe_load(params_path.read_text(encoding='utf-8')) or {}",
        "",
        "def _assign(mapping: dict[str, Any], keys: list[str], value: Any) -> None:",
        "    cur: dict[str, Any] = mapping",
        "    for key in keys[:-1]:",
        "        if key not in cur or not isinstance(cur[key], dict):",
        "            cur[key] = {}",
        "        cur = cur[key]  # type: ignore[assignment]",
        "    cur[keys[-1]] = value",
        "",
    ]
    for keys, current, new_value in updates:
        dotted = ".".join(keys)
        lines.append(f"# {dotted}: {current!r} -> {new_value!r}")
        lines.append(f"_assign(params, {json.dumps(keys)}, {json.dumps(new_value)})")
        lines.append("")
    lines.extend(
        [
            "params_path.write_text(",
            "    yaml.safe_dump(params, sort_keys=False),",
            "    encoding='utf-8',",
            ")",
            "print('Updated parameters written to', params_path)",
        ]
    )
    return "\n".join(lines)


def _diff_dag(previous: str | None, current: str) -> str:
    if not previous:
        return current or "(empty DAG)"
    diff = difflib.unified_diff(
        previous.splitlines(),
        current.splitlines(),
        fromfile="previous",
        tofile="current",
        lineterm="",
    )
    diff_text = "\n".join(diff).strip()
    return diff_text or "No DAG changes detected."


def _comment_block(title: str, body: str) -> str:
    header = f"# {title}" if title else "#"
    if not body.strip():
        return f"{header}\n# (no details)"
    body_lines = [f"# {line}" if line else "#" for line in body.splitlines()]
    return "\n".join([header, *body_lines])


def suggest_cell(panel_state: dict) -> str:
    """Return a Suggestion Cell describing DAG changes and parameter edits."""

    profile = panel_state.get("profile")
    targets = _render_targets(panel_state)

    dry_run_cmd = [*_snakemake_base_args(targets, profile), "-n"]
    dag_cmd = [*_snakemake_base_args(targets, profile), "--dag"]

    dry_result = _run_command(dry_run_cmd)
    dag_result = _run_command(dag_cmd)

    summarized_dry = _summarize_output(dry_result.merged())
    current_dag = dag_result.stdout.strip() or dag_result.merged()

    previous_dag = None
    for key in ("previousDag", "lastDag", "baselineDag", "dagSnapshot"):
        maybe = panel_state.get(key)
        if isinstance(maybe, str) and maybe.strip():
            previous_dag = maybe
            break

    dag_diff = _diff_dag(previous_dag, current_dag)
    params = _read_params()
    updates = _infer_param_updates(params, panel_state)

    suggestion_lines: list[str] = [
        "# Vigil auto-target suggestion",
        _comment_block("Target(s)", ", ".join(targets)),
        _comment_block("Dry-run summary", summarized_dry),
        _comment_block("DAG diff", _summarize_output(dag_diff, limit=32)),
        "",
        _format_updates_block(updates),
    ]

    return "\n".join(suggestion_lines)
