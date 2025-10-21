"""
Plugin system for Ariadne.

This module provides a plugin architecture for extending Ariadne functionality,
with plugin discovery, loading, and lifecycle management.
"""

from .manager import (
    BackendPlugin,
    Plugin,
    PluginError,
    PluginInfo,
    PluginManager,
    PluginState,
    PluginStatus,
    PluginType,
    RouterPlugin,
    get_plugin_manager,
    list_plugins,
    load_plugin,
    unload_plugin,
)

__all__ = [
    "BackendPlugin",
    "Plugin",
    "PluginError",
    "PluginInfo",
    "PluginManager",
    "PluginState",
    "PluginStatus",
    "PluginType",
    "RouterPlugin",
    "get_plugin_manager",
    "list_plugins",
    "load_plugin",
    "unload_plugin",
]
