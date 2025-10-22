"""Environment capture core API."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class SystemInfo(TypedDict):
    """System information structure."""

    platform: str
    hostname: str
    user: str
    python_version: str
    python_executable: str
    cpu_count: int
    memory_total: str
    timestamp: str


class EnvironmentCapture:
    """Environment capture and analysis."""

    def __init__(self):
        self.system_info = self._capture_system_info()
        self.environment_vars = self._capture_environment_vars()
        self.python_info = self._capture_python_info()
        self.docker_info = self._capture_docker_info() if DOCKER_AVAILABLE else None
        self.gpu_info = self._capture_gpu_info()

    def _capture_system_info(self) -> SystemInfo:
        """Capture basic system information."""
        try:
            memory_total = "unknown"
            try:
                if sys.platform == "darwin":  # macOS
                    result = subprocess.run(
                        ["sysctl", "-n", "hw.memsize"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        memory_bytes = int(result.stdout.strip())
                        memory_total = f"{memory_bytes // (1024**3)} GB"
                elif sys.platform == "linux":
                    with open("/proc/meminfo", "r") as f:
                        for line in f:
                            if line.startswith("MemTotal:"):
                                memory_kb = int(line.split()[1])
                                memory_total = f"{memory_kb // 1024} MB"
                                break
            except Exception:
                pass

            return SystemInfo(
                platform=platform.platform(),
                hostname=platform.node(),
                user=os.getenv("USER", os.getenv("USERNAME", "unknown")),
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                python_executable=sys.executable,
                cpu_count=os.cpu_count() or 1,
                memory_total=memory_total,
                timestamp=datetime.now(UTC).isoformat()
            )
        except Exception:
            return SystemInfo(
                platform="unknown",
                hostname="unknown",
                user="unknown",
                python_version="unknown",
                python_executable="unknown",
                cpu_count=1,
                memory_total="unknown",
                timestamp=datetime.now(UTC).isoformat()
            )

    def _capture_environment_vars(self) -> dict[str, str]:
        """Capture relevant environment variables."""
        relevant_vars = [
            "PATH", "HOME", "USER", "SHELL", "LANG", "LC_ALL",
            "PYTHONPATH", "CONDA_DEFAULT_ENV", "VIRTUAL_ENV",
            "CUDA_VISIBLE_DEVICES", "LD_LIBRARY_PATH"
        ]

        env_vars = {}
        for var in relevant_vars:
            value = os.getenv(var)
            if value:
                env_vars[var] = value

        return env_vars

    def _capture_python_info(self) -> dict[str, Any]:
        """Capture Python-specific information."""
        python_info = {
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "executable": sys.executable,
            "path": sys.path[:10],  # First 10 entries to avoid huge output
            "platform": sys.platform,
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler()
        }

        # Capture installed packages (first 20 to avoid huge output)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                import json
                packages = json.loads(result.stdout)
                python_info["packages"] = packages[:20]  # First 20 packages
        except Exception:
            python_info["packages"] = []

        return python_info

    def _capture_docker_info(self) -> dict[str, Any] | None:
        """Capture Docker information if available."""
        if not DOCKER_AVAILABLE:
            return None

        try:
            client = docker.from_env()
            docker_info = {
                "version": client.version(),
                "info": client.info(),
                "containers": []
            }

            # Get running containers
            containers = client.containers.list(limit=10)
            for container in containers:
                docker_info["containers"].append({
                    "id": container.short_id,
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "status": container.status
                })

            return docker_info
        except Exception:
            return None

    def _capture_gpu_info(self) -> dict[str, Any]:
        """Capture GPU information if available."""
        gpu_info = {"available": False, "devices": []}

        try:
            # Try nvidia-smi
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                gpu_info["available"] = True
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        parts = line.split(", ")
                        if len(parts) >= 3:
                            gpu_info["devices"].append({
                                "name": parts[0],
                                "memory_mb": int(parts[1]) if parts[1].isdigit() else 0,
                                "driver_version": parts[2]
                            })
        except Exception:
            pass

        return gpu_info

    def to_dict(self) -> dict[str, Any]:
        """Convert environment capture to dictionary."""
        return {
            "system": self.system_info,
            "environment": self.environment_vars,
            "python": self.python_info,
            "docker": self.docker_info,
            "gpu": self.gpu_info,
            "captured_at": datetime.now(UTC).isoformat()
        }

    def save(self, output_path: Path | str) -> None:
        """Save environment capture to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        import json
        output_path.write_text(
            json.dumps(self.to_dict(), indent=2),
            encoding="utf-8"
        )

    @classmethod
    def load(cls, input_path: Path | str) -> EnvironmentCapture:
        """Load environment capture from file."""
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Environment file not found: {input_path}")

        import json
        data = json.loads(input_path.read_text(encoding="utf-8"))

        # Reconstruct object from saved data
        capture = cls.__new__(cls)
        capture.system_info = data["system"]
        capture.environment_vars = data["environment"]
        capture.python_info = data["python"]
        capture.docker_info = data.get("docker")
        capture.gpu_info = data["gpu"]

        return capture
