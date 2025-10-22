"""Environment capture utilities for Vigil."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


def capture_system_info() -> dict[str, Any]:
    """Capture system information.

    Returns:
        Dictionary with system information
    """
    return {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "hostname": platform.node()
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler(),
            "build": platform.python_build()
        },
        "runtime": {
            "executable": sys.executable,
            "path": sys.path,
            "prefix": sys.prefix,
            "base_prefix": getattr(sys, "base_prefix", sys.prefix)
        }
    }


def capture_python_environment() -> dict[str, Any]:
    """Capture Python package environment.

    Returns:
        Dictionary with Python environment information
    """
    env_info = {
        "packages": {},
        "pip_freeze": None,
        "conda_info": None,
        "virtual_env": None
    }

    # Try to get pip freeze
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            env_info["pip_freeze"] = result.stdout.strip().split("\n")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Try to get conda info
    try:
        result = subprocess.run(["conda", "info", "--json"],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            env_info["conda_info"] = json.loads(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass

    # Check for virtual environment
    if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        env_info["virtual_env"] = {
            "active": True,
            "path": sys.prefix,
            "base_path": getattr(sys, "base_prefix", None)
        }
    else:
        env_info["virtual_env"] = {"active": False}

    # Get some key package versions
    key_packages = ["numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "seaborn", "jupyter"]
    for package in key_packages:
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            env_info["packages"][package] = version
        except ImportError:
            env_info["packages"][package] = "not_installed"

    return env_info


def capture_docker_info() -> dict[str, Any]:
    """Capture Docker container information if running in container.

    Returns:
        Dictionary with Docker information
    """
    docker_info = {
        "running_in_container": False,
        "container_id": None,
        "image": None,
        "image_digest": None
    }

    # Check if running in Docker
    if Path("/.dockerenv").exists():
        docker_info["running_in_container"] = True

        # Try to get container ID
        try:
            with open("/proc/self/cgroup") as f:
                content = f.read()
                if "docker" in content:
                    # Extract container ID from cgroup
                    lines = content.split("\n")
                    for line in lines:
                        if "docker" in line:
                            parts = line.split("/")
                            if len(parts) > 2:
                                docker_info["container_id"] = parts[-1][:12]
                                break
        except (FileNotFoundError, IndexError):
            pass

        # Try to get image information
        try:
            result = subprocess.run(["cat", "/proc/self/mountinfo"],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Look for image information in mount info
                for line in result.stdout.split("\n"):
                    if "docker" in line and "image" in line:
                        # Extract image name if possible
                        parts = line.split()
                        for part in parts:
                            if "docker" in part and "image" in part:
                                docker_info["image"] = part
                                break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return docker_info


def capture_gpu_info() -> dict[str, Any]:
    """Capture GPU information if available.

    Returns:
        Dictionary with GPU information
    """
    gpu_info = {
        "available": False,
        "nvidia": None,
        "cuda": None
    }

    # Check for NVIDIA GPU
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                               "--format=csv,noheader,nounits"],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            gpu_info["available"] = True
            gpu_info["nvidia"] = {
                "smi_output": result.stdout.strip(),
                "driver_version": None,
                "gpu_name": None,
                "memory_total": None
            }

            # Parse nvidia-smi output
            lines = result.stdout.strip().split("\n")
            if lines:
                parts = lines[0].split(", ")
                if len(parts) >= 3:
                    gpu_info["nvidia"]["gpu_name"] = parts[0].strip()
                    gpu_info["nvidia"]["driver_version"] = parts[1].strip()
                    gpu_info["nvidia"]["memory_total"] = parts[2].strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Check for CUDA
    try:
        result = subprocess.run(["nvcc", "--version"],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            gpu_info["cuda"] = {
                "available": True,
                "version_output": result.stdout.strip()
            }
        else:
            gpu_info["cuda"] = {"available": False}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        gpu_info["cuda"] = {"available": False}

    return gpu_info


def capture_environment_variables() -> dict[str, Any]:
    """Capture relevant environment variables.

    Returns:
        Dictionary with environment variables
    """
    relevant_vars = [
        "PATH", "PYTHONPATH", "CONDA_DEFAULT_ENV", "VIRTUAL_ENV",
        "CUDA_VISIBLE_DEVICES", "NVIDIA_VISIBLE_DEVICES",
        "OMP_NUM_THREADS", "MKL_NUM_THREADS",
        "VIGIL_API_URL", "VIGIL_CONFIG_DIR"
    ]

    env_vars = {}
    for var in relevant_vars:
        value = os.environ.get(var)
        if value is not None:
            env_vars[var] = value

    return env_vars


def capture_vigil_info() -> dict[str, Any]:
    """Capture Vigil-specific information.

    Returns:
        Dictionary with Vigil information
    """
    vigil_info = {
        "version": "0.2.4",  # This should be imported from vigil.__version__
        "config_dir": None,
        "workspace_root": None
    }

    # Try to find Vigil config directory
    config_dirs = [
        Path.home() / ".vigil",
        Path.cwd() / ".vigil",
        Path(os.environ.get("VIGIL_CONFIG_DIR", ""))
    ]

    for config_dir in config_dirs:
        if config_dir and config_dir.exists():
            vigil_info["config_dir"] = str(config_dir)
            break

    # Try to find workspace root
    current_path = Path.cwd()
    while current_path != current_path.parent:
        if (current_path / "vigil.yaml").exists():
            vigil_info["workspace_root"] = str(current_path)
            break
        current_path = current_path.parent

    return vigil_info


def capture_full_environment() -> dict[str, Any]:
    """Capture complete environment information.

    Returns:
        Dictionary with complete environment information
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "system": capture_system_info(),
        "python": capture_python_environment(),
        "docker": capture_docker_info(),
        "gpu": capture_gpu_info(),
        "environment_variables": capture_environment_variables(),
        "vigil": capture_vigil_info()
    }


def save_environment_snapshot(output_path: Path, environment_data: dict[str, Any] | None = None) -> None:
    """Save environment snapshot to file.

    Args:
        output_path: Path to save environment snapshot
        environment_data: Environment data to save (if None, captures current environment)
    """
    if environment_data is None:
        environment_data = capture_full_environment()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(environment_data, f, indent=2, default=str)


def load_environment_snapshot(snapshot_path: Path) -> dict[str, Any]:
    """Load environment snapshot from file.

    Args:
        snapshot_path: Path to environment snapshot file

    Returns:
        Environment data dictionary
    """
    with snapshot_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def compare_environments(env1: dict[str, Any], env2: dict[str, Any]) -> dict[str, Any]:
    """Compare two environment snapshots.

    Args:
        env1: First environment snapshot
        env2: Second environment snapshot

    Returns:
        Comparison results
    """
    comparison = {
        "identical": True,
        "differences": [],
        "summary": {
            "system_changes": 0,
            "python_changes": 0,
            "package_changes": 0,
            "environment_changes": 0
        }
    }

    # Compare system info
    if env1.get("system") != env2.get("system"):
        comparison["identical"] = False
        comparison["summary"]["system_changes"] += 1
        comparison["differences"].append("System information differs")

    # Compare Python info
    if env1.get("python") != env2.get("python"):
        comparison["identical"] = False
        comparison["summary"]["python_changes"] += 1
        comparison["differences"].append("Python environment differs")

    # Compare packages
    packages1 = env1.get("python", {}).get("packages", {})
    packages2 = env2.get("python", {}).get("packages", {})

    if packages1 != packages2:
        comparison["identical"] = False
        comparison["summary"]["package_changes"] += 1
        comparison["differences"].append("Package versions differ")

    # Compare environment variables
    env_vars1 = env1.get("environment_variables", {})
    env_vars2 = env2.get("environment_variables", {})

    if env_vars1 != env_vars2:
        comparison["identical"] = False
        comparison["summary"]["environment_changes"] += 1
        comparison["differences"].append("Environment variables differ")

    return comparison


def cli() -> None:
    """CLI entry point for environment capture."""
    import argparse

    parser = argparse.ArgumentParser(description="Capture and manage Vigil environment snapshots")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Capture command
    capture_parser = subparsers.add_parser("capture", help="Capture environment snapshot")
    capture_parser.add_argument("output", type=Path, help="Output file path")
    capture_parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare environment snapshots")
    compare_parser.add_argument("snapshot1", type=Path, help="First snapshot file")
    compare_parser.add_argument("snapshot2", type=Path, help="Second snapshot file")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show current environment info")
    info_parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "capture":
        environment_data = capture_full_environment()

        if args.format == "yaml":
            with args.output.open("w", encoding="utf-8") as f:
                yaml.dump(environment_data, f, default_flow_style=False)
        else:
            save_environment_snapshot(args.output, environment_data)

        print(f"Environment snapshot saved to {args.output}")

    elif args.command == "compare":
        env1 = load_environment_snapshot(args.snapshot1)
        env2 = load_environment_snapshot(args.snapshot2)
        comparison = compare_environments(env1, env2)

        if comparison["identical"]:
            print("✅ Environments are identical")
        else:
            print("❌ Environments differ")
            print(f"Differences: {len(comparison['differences'])}")
            for diff in comparison["differences"]:
                print(f"  - {diff}")
            print(f"Summary: {comparison['summary']}")

    elif args.command == "info":
        environment_data = capture_full_environment()

        if args.format == "yaml":
            print(yaml.dump(environment_data, default_flow_style=False))
        else:
            print(json.dumps(environment_data, indent=2, default=str))


if __name__ == "__main__":
    cli()
