"""Plugin system for Vigil extensions."""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass
class PluginContext:
    """Context passed to plugin hooks."""

    project_root: Path
    vigil_config: dict[str, Any]
    environment: dict[str, Any]
    metadata: dict[str, Any]


@dataclass
class PluginHook:
    """Represents a plugin hook."""

    hook_id: str
    plugin_name: str
    function: Callable
    priority: int = 0
    enabled: bool = True


class PluginManager:
    """Manages Vigil plugins and hooks."""

    def __init__(self, plugins_dir: Path | None = None):
        """Initialize plugin manager.

        Args:
            plugins_dir: Directory containing plugin files
        """
        self.plugins_dir = plugins_dir or Path.home() / ".vigil" / "plugins"
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.hooks: dict[str, list[PluginHook]] = {}
        self.plugins: dict[str, Any] = {}
        self._load_plugins()

    def _load_plugins(self) -> None:
        """Load all plugins from the plugins directory."""
        if not self.plugins_dir.exists():
            return

        for plugin_file in self.plugins_dir.glob("*.py"):
            try:
                self._load_plugin(plugin_file)
            except Exception as e:
                print(f"Warning: Failed to load plugin {plugin_file}: {e}")

    def _load_plugin(self, plugin_file: Path) -> None:
        """Load a single plugin file.

        Args:
            plugin_file: Path to plugin file
        """
        plugin_name = plugin_file.stem

        # Import the plugin module
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
        if spec is None or spec.loader is None:
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.plugins[plugin_name] = module

        # Register hooks from the plugin
        self._register_hooks(plugin_name, module)

    def _register_hooks(self, plugin_name: str, module: Any) -> None:
        """Register hooks from a plugin module.

        Args:
            plugin_name: Name of the plugin
            module: Plugin module
        """
        # Look for hook functions in the module
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and name.startswith("on_"):
                hook_name = name[3:]  # Remove "on_" prefix

                hook = PluginHook(
                    hook_id=str(uuid4()),
                    plugin_name=plugin_name,
                    function=obj,
                    priority=getattr(obj, "priority", 0),
                    enabled=getattr(obj, "enabled", True)
                )

                if hook_name not in self.hooks:
                    self.hooks[hook_name] = []

                self.hooks[hook_name].append(hook)
                # Sort by priority (higher priority first)
                self.hooks[hook_name].sort(key=lambda h: h.priority, reverse=True)

    def call_hook(self, hook_name: str, context: PluginContext, *args, **kwargs) -> list[Any]:
        """Call all registered hooks for a given hook name.

        Args:
            hook_name: Name of the hook
            context: Plugin context
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            List of hook results
        """
        results = []

        if hook_name not in self.hooks:
            return results

        for hook in self.hooks[hook_name]:
            if not hook.enabled:
                continue

            try:
                result = hook.function(context, *args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Warning: Hook {hook.plugin_name}.{hook.function.__name__} failed: {e}")

        return results

    def get_plugin_info(self, plugin_name: str) -> dict[str, Any] | None:
        """Get information about a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin information or None
        """
        if plugin_name not in self.plugins:
            return None

        module = self.plugins[plugin_name]

        return {
            "name": plugin_name,
            "version": getattr(module, "__version__", "unknown"),
            "description": getattr(module, "__description__", ""),
            "author": getattr(module, "__author__", ""),
            "hooks": [
                {
                    "name": hook_name,
                    "function": hook.function.__name__,
                    "priority": hook.priority,
                    "enabled": hook.enabled
                }
                for hook_name, hooks in self.hooks.items()
                for hook in hooks
                if hook.plugin_name == plugin_name
            ]
        }

    def list_plugins(self) -> list[dict[str, Any]]:
        """List all loaded plugins.

        Returns:
            List of plugin information
        """
        return [self.get_plugin_info(name) for name in self.plugins.keys()]

    def enable_hook(self, plugin_name: str, hook_name: str) -> None:
        """Enable a specific hook.

        Args:
            plugin_name: Name of the plugin
            hook_name: Name of the hook
        """
        if hook_name in self.hooks:
            for hook in self.hooks[hook_name]:
                if hook.plugin_name == plugin_name:
                    hook.enabled = True

    def disable_hook(self, plugin_name: str, hook_name: str) -> None:
        """Disable a specific hook.

        Args:
            plugin_name: Name of the plugin
            hook_name: Name of the hook
        """
        if hook_name in self.hooks:
            for hook in self.hooks[hook_name]:
                if hook.plugin_name == plugin_name:
                    hook.enabled = False


# Global plugin manager instance
_plugin_manager: PluginManager | None = None


def get_plugin_manager() -> PluginManager:
    """Get global plugin manager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def call_hook(hook_name: str, context: PluginContext, *args, **kwargs) -> list[Any]:
    """Call a hook using the global plugin manager."""
    manager = get_plugin_manager()
    return manager.call_hook(hook_name, context, *args, **kwargs)


def create_plugin_template(plugin_name: str, output_dir: Path) -> None:
    """Create a plugin template file.

    Args:
        plugin_name: Name of the plugin
        output_dir: Directory to create the plugin in
    """
    template = f'''"""Vigil plugin: {plugin_name}"""

__version__ = "0.1.0"
__description__ = "Description of {plugin_name} plugin"
__author__ = "Your Name"

from pathlib import Path
from typing import Any, Dict
from vigil.tools.plugins import PluginContext


def on_run_start(context: PluginContext, pipeline_config: Dict[str, Any]) -> None:
    """Called when a pipeline run starts.

    Args:
        context: Plugin context
        pipeline_config: Pipeline configuration
    """
    print(f"Plugin {{__name__}}: Pipeline run starting")


def on_run_finish(context: PluginContext, result: Dict[str, Any]) -> None:
    """Called when a pipeline run finishes.

    Args:
        context: Plugin context
        result: Pipeline result
    """
    print(f"Plugin {{__name__}}: Pipeline run finished")


def on_receipt_generated(context: PluginContext, receipt: Dict[str, Any]) -> None:
    """Called when a receipt is generated.

    Args:
        context: Plugin context
        receipt: Generated receipt
    """
    print(f"Plugin {{__name__}}: Receipt generated: {{receipt.get('runletId')}}")


def on_artifact_created(context: PluginContext, artifact: Dict[str, Any]) -> None:
    """Called when an artifact is created.

    Args:
        context: Plugin context
        artifact: Created artifact
    """
    print(f"Plugin {{__name__}}: Artifact created: {{artifact.get('name')}}")
'''

    plugin_file = output_dir / f"{plugin_name}.py"
    with plugin_file.open("w", encoding="utf-8") as f:
        f.write(template)

    print(f"Created plugin template: {plugin_file}")


def cli() -> None:
    """CLI entry point for plugin management."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage Vigil plugins")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", help="List loaded plugins")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show plugin information")
    info_parser.add_argument("plugin_name", help="Name of the plugin")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create plugin template")
    create_parser.add_argument("plugin_name", help="Name of the plugin")
    create_parser.add_argument("--output", type=Path, help="Output directory")

    # Enable/Disable commands
    enable_parser = subparsers.add_parser("enable", help="Enable plugin hook")
    enable_parser.add_argument("plugin_name", help="Name of the plugin")
    enable_parser.add_argument("hook_name", help="Name of the hook")

    disable_parser = subparsers.add_parser("disable", help="Disable plugin hook")
    disable_parser.add_argument("plugin_name", help="Name of the plugin")
    disable_parser.add_argument("hook_name", help="Name of the hook")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = get_plugin_manager()

    if args.command == "list":
        plugins = manager.list_plugins()
        print("Loaded plugins:")
        for plugin in plugins:
            if plugin:
                print(f"  {plugin['name']}: {plugin['description']}")
                print(f"    Version: {plugin['version']}")
                print(f"    Hooks: {len(plugin['hooks'])}")
                print()

    elif args.command == "info":
        info = manager.get_plugin_info(args.plugin_name)
        if info:
            print(f"Plugin: {info['name']}")
            print(f"  Version: {info['version']}")
            print(f"  Description: {info['description']}")
            print(f"  Author: {info['author']}")
            print("  Hooks:")
            for hook in info['hooks']:
                status = "enabled" if hook['enabled'] else "disabled"
                print(f"    {hook['name']}: {hook['function']} (priority: {hook['priority']}, {status})")
        else:
            print(f"Plugin not found: {args.plugin_name}")

    elif args.command == "create":
        output_dir = args.output or Path.home() / ".vigil" / "plugins"
        create_plugin_template(args.plugin_name, output_dir)

    elif args.command == "enable":
        manager.enable_hook(args.plugin_name, args.hook_name)
        print(f"Enabled hook {args.hook_name} for plugin {args.plugin_name}")

    elif args.command == "disable":
        manager.disable_hook(args.plugin_name, args.hook_name)
        print(f"Disabled hook {args.hook_name} for plugin {args.plugin_name}")


if __name__ == "__main__":
    cli()
