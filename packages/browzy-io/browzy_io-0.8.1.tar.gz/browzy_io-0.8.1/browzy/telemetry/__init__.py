"""
Telemetry for Browser Use.
"""

from typing import TYPE_CHECKING

# Type stubs for lazy imports
if TYPE_CHECKING:
	from browzy.telemetry.service import ProductTelemetry
	from browzy.telemetry.views import (
		BaseTelemetryEvent,
		CLITelemetryEvent,
		MCPClientTelemetryEvent,
		MCPServerTelemetryEvent,
	)

# Lazy imports mapping
_LAZY_IMPORTS = {
	'ProductTelemetry': ('browzy.telemetry.service', 'ProductTelemetry'),
	'BaseTelemetryEvent': ('browzy.telemetry.views', 'BaseTelemetryEvent'),
	'CLITelemetryEvent': ('browzy.telemetry.views', 'CLITelemetryEvent'),
	'MCPClientTelemetryEvent': ('browzy.telemetry.views', 'MCPClientTelemetryEvent'),
	'MCPServerTelemetryEvent': ('browzy.telemetry.views', 'MCPServerTelemetryEvent'),
}


def __getattr__(name: str):
	"""Lazy import mechanism for telemetry components."""
	if name in _LAZY_IMPORTS:
		module_path, attr_name = _LAZY_IMPORTS[name]
		try:
			from importlib import import_module

			module = import_module(module_path)
			attr = getattr(module, attr_name)
			# Cache the imported attribute in the module's globals
			globals()[name] = attr
			return attr
		except ImportError as e:
			raise ImportError(f'Failed to import {name} from {module_path}: {e}') from e

	raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
	'BaseTelemetryEvent',
	'ProductTelemetry',
	'CLITelemetryEvent',
	'MCPClientTelemetryEvent',
	'MCPServerTelemetryEvent',
]
