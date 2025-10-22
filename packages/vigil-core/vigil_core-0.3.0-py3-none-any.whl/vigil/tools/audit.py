"""Audit logging for Vigil CLI actions."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class AuditEntry:
    """Represents an audit log entry."""

    def __init__(self, entry_id: str, timestamp: datetime, action: str,
                 command: str, args: list[str], result: str,
                 receipt_id: str | None = None, checksum: str | None = None,
                 metadata: dict[str, Any] | None = None):
        self.entry_id = entry_id
        self.timestamp = timestamp
        self.action = action
        self.command = command
        self.args = args
        self.result = result
        self.receipt_id = receipt_id
        self.checksum = checksum
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "command": self.command,
            "args": self.args,
            "result": self.result,
            "receipt_id": self.receipt_id,
            "checksum": self.checksum,
            "metadata": self.metadata
        }


class AuditLogger:
    """Immutable audit logger for Vigil CLI actions."""

    def __init__(self, audit_file: Path | None = None):
        """Initialize audit logger.

        Args:
            audit_file: Path to audit log file
        """
        self.audit_file = audit_file or Path(".vigil/audit.log")
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_immutable()

    def _ensure_immutable(self) -> None:
        """Ensure audit log is immutable (append-only)."""
        if self.audit_file.exists():
            # Make file read-only to prevent modification
            os.chmod(self.audit_file, 0o444)

    def log_action(self, action: str, command: str, args: list[str],
                   result: str, receipt_id: str | None = None,
                   checksum: str | None = None, metadata: dict[str, Any] | None = None) -> None:
        """Log a CLI action.

        Args:
            action: Action performed (run, promote, verify, etc.)
            command: Full command executed
            args: Command arguments
            result: Result of the action
            receipt_id: Receipt ID if applicable
            checksum: Checksum if applicable
            metadata: Additional metadata
        """
        # Temporarily make file writable
        if self.audit_file.exists():
            os.chmod(self.audit_file, 0o644)

        entry = AuditEntry(
            entry_id=str(uuid4()),
            timestamp=datetime.now(UTC),
            action=action,
            command=command,
            args=args,
            result=result,
            receipt_id=receipt_id,
            checksum=checksum,
            metadata=metadata or {}
        )

        # Append to audit log
        with self.audit_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

        # Make file read-only again
        os.chmod(self.audit_file, 0o444)

    def get_entries(self, action: str | None = None,
                   limit: int = 100) -> list[AuditEntry]:
        """Get audit entries.

        Args:
            action: Filter by action
            limit: Maximum number of entries

        Returns:
            List of audit entries
        """
        entries = []

        if not self.audit_file.exists():
            return entries

        with self.audit_file.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry_data = json.loads(line.strip())
                    entry = AuditEntry(
                        entry_id=entry_data["entry_id"],
                        timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                        action=entry_data["action"],
                        command=entry_data["command"],
                        args=entry_data["args"],
                        result=entry_data["result"],
                        receipt_id=entry_data.get("receipt_id"),
                        checksum=entry_data.get("checksum"),
                        metadata=entry_data.get("metadata", {})
                    )

                    if action is None or entry.action == action:
                        entries.append(entry)

                        if len(entries) >= limit:
                            break

                except (json.JSONDecodeError, KeyError):
                    continue

        return entries

    def get_receipt_history(self, receipt_id: str) -> list[AuditEntry]:
        """Get audit history for a specific receipt.

        Args:
            receipt_id: Receipt ID

        Returns:
            List of audit entries for the receipt
        """
        entries = []

        if not self.audit_file.exists():
            return entries

        with self.audit_file.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry_data = json.loads(line.strip())
                    if entry_data.get("receipt_id") == receipt_id:
                        entry = AuditEntry(
                            entry_id=entry_data["entry_id"],
                            timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                            action=entry_data["action"],
                            command=entry_data["command"],
                            args=entry_data["args"],
                            result=entry_data["result"],
                            receipt_id=entry_data.get("receipt_id"),
                            checksum=entry_data.get("checksum"),
                            metadata=entry_data.get("metadata", {})
                        )
                        entries.append(entry)

                except (json.JSONDecodeError, KeyError):
                    continue

        return entries

    def get_stats(self) -> dict[str, Any]:
        """Get audit log statistics.

        Returns:
            Audit log statistics
        """
        if not self.audit_file.exists():
            return {"total_entries": 0, "actions": {}, "date_range": None}

        actions = {}
        first_date = None
        last_date = None
        total_entries = 0

        with self.audit_file.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry_data = json.loads(line.strip())
                    action = entry_data["action"]
                    timestamp = datetime.fromisoformat(entry_data["timestamp"])

                    actions[action] = actions.get(action, 0) + 1
                    total_entries += 1

                    if first_date is None or timestamp < first_date:
                        first_date = timestamp
                    if last_date is None or timestamp > last_date:
                        last_date = timestamp

                except (json.JSONDecodeError, KeyError):
                    continue

        return {
            "total_entries": total_entries,
            "actions": actions,
            "date_range": {
                "first": first_date.isoformat() if first_date else None,
                "last": last_date.isoformat() if last_date else None
            }
        }

    def export_entries(self, output_file: Path, format: str = "json") -> None:
        """Export audit entries to file.

        Args:
            output_file: Output file path
            format: Export format (json, csv)
        """
        entries = self.get_entries()

        if format == "json":
            with output_file.open("w", encoding="utf-8") as f:
                json.dump([entry.to_dict() for entry in entries], f, indent=2)

        elif format == "csv":
            import csv
            with output_file.open("w", encoding="utf-8", newline="") as f:
                if entries:
                    writer = csv.DictWriter(f, fieldnames=entries[0].to_dict().keys())
                    writer.writeheader()
                    for entry in entries:
                        writer.writerow(entry.to_dict())

        else:
            raise ValueError(f"Unsupported format: {format}")


# Global audit logger instance
_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def log_action(action: str, command: str, args: list[str], result: str,
               receipt_id: str | None = None, checksum: str | None = None,
               metadata: dict[str, Any] | None = None) -> None:
    """Log a CLI action using global audit logger."""
    logger = get_audit_logger()
    logger.log_action(action, command, args, result, receipt_id, checksum, metadata)


def cli() -> None:
    """CLI entry point for audit log management."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage Vigil audit log")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List audit entries")
    list_parser.add_argument("--action", help="Filter by action")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum entries to show")

    # Stats command
    subparsers.add_parser("stats", help="Show audit log statistics")

    # History command
    history_parser = subparsers.add_parser("history", help="Show history for receipt")
    history_parser.add_argument("receipt_id", help="Receipt ID")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export audit entries")
    export_parser.add_argument("output", type=Path, help="Output file")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    logger = get_audit_logger()

    if args.command == "list":
        entries = logger.get_entries(action=args.action, limit=args.limit)
        print(f"Audit entries ({len(entries)}):")
        for entry in entries:
            print(f"  {entry.timestamp}: {entry.action} -> {entry.result}")
            if entry.receipt_id:
                print(f"    Receipt: {entry.receipt_id}")
            if entry.checksum:
                print(f"    Checksum: {entry.checksum}")
            print()

    elif args.command == "stats":
        stats = logger.get_stats()
        print("Audit Log Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Actions: {stats['actions']}")
        print(f"  Date range: {stats['date_range']}")

    elif args.command == "history":
        entries = logger.get_receipt_history(args.receipt_id)
        print(f"History for receipt {args.receipt_id}:")
        for entry in entries:
            print(f"  {entry.timestamp}: {entry.action} -> {entry.result}")
            print(f"    Command: {entry.command}")
            print()

    elif args.command == "export":
        logger.export_entries(args.output, args.format)
        print(f"Exported audit entries to {args.output}")


if __name__ == "__main__":
    cli()
