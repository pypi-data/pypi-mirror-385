"""Vigil Core API - importable library for programmatic access."""

from .receipts import generate_receipt, verify_receipt, ReceiptManager
from .pipeline import run_pipeline, PipelineConfig, PipelineResult
from .signer import Signer, verify_signature
from .policy import PolicyEngine, PolicyResult, create_default_policy
from .env import EnvironmentCapture, SystemInfo

__all__ = [
    "generate_receipt",
    "verify_receipt",
    "ReceiptManager",
    "run_pipeline",
    "PipelineConfig",
    "PipelineResult",
    "Signer",
    "verify_signature",
    "PolicyEngine",
    "PolicyResult",
    "create_default_policy",
    "EnvironmentCapture",
    "SystemInfo",
]
