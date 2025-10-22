"""Pipeline execution core API."""

from __future__ import annotations

import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict


class PipelineConfig(TypedDict, total=False):
    """Pipeline configuration."""

    command: str
    working_dir: str | Path
    environment: dict[str, str]
    timeout: int
    cores: int
    memory: str
    dry_run: bool


class PipelineResult(TypedDict):
    """Pipeline execution result."""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    started_at: datetime
    finished_at: datetime
    artifacts: list[dict[str, Any]]


def run_pipeline(
    command: str,
    working_dir: Path | str | None = None,
    environment: dict[str, str] | None = None,
    timeout: int = 3600,
    dry_run: bool = False
) -> PipelineResult:
    """Run a pipeline command and return the result."""

    start_time = datetime.now(UTC)

    if working_dir is None:
        working_dir = Path.cwd()
    else:
        working_dir = Path(working_dir)

    if environment is None:
        environment = {}

    # Merge with current environment
    env = os.environ.copy()
    env.update(environment)

    if dry_run:
        return PipelineResult(
            success=True,
            exit_code=0,
            stdout=f"[DRY RUN] Would execute: {command}",
            stderr="",
            duration=0.0,
            started_at=start_time,
            finished_at=start_time,
            artifacts=[]
        )

    try:
        # Run the command
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        end_time = datetime.now(UTC)
        duration = (end_time - start_time).total_seconds()

        return PipelineResult(
            success=result.returncode == 0,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration=duration,
            started_at=start_time,
            finished_at=end_time,
            artifacts=[]
        )

    except subprocess.TimeoutExpired:
        end_time = datetime.now(UTC)
        duration = (end_time - start_time).total_seconds()

        return PipelineResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=f"Pipeline timed out after {timeout} seconds",
            duration=duration,
            started_at=start_time,
            finished_at=end_time,
            artifacts=[]
        )

    except Exception as e:
        end_time = datetime.now(UTC)
        duration = (end_time - start_time).total_seconds()

        return PipelineResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=str(e),
            duration=duration,
            started_at=start_time,
            finished_at=end_time,
            artifacts=[]
        )


def run_snakemake_pipeline(
    snakefile: Path | str = "Snakefile",
    working_dir: Path | str | None = None,
    cores: int = 1,
    dry_run: bool = False
) -> PipelineResult:
    """Run a Snakemake pipeline."""

    snakefile_path = Path(snakefile)
    if not snakefile_path.exists():
        raise FileNotFoundError(f"Snakefile not found: {snakefile}")

    command = f"snakemake --cores {cores}"
    if dry_run:
        command += " --dry-run"

    return run_pipeline(
        command=command,
        working_dir=working_dir,
        dry_run=dry_run
    )
