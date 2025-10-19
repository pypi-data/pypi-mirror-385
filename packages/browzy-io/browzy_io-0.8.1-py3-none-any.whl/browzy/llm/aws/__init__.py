from typing import TYPE_CHECKING

# Type stubs for lazy imports
if TYPE_CHECKING:
	from browzy.llm.aws.chat_anthropic import ChatAnthropicBedrock
	from browzy.llm.aws.chat_bedrock import ChatAWSBedrock

# Lazy imports mapping for AWS chat models
_LAZY_IMPORTS = {
	'ChatAnthropicBedrock': ('browzy.llm.aws.chat_anthropic', 'ChatAnthropicBedrock'),
	'ChatAWSBedrock': ('browzy.llm.aws.chat_bedrock', 'ChatAWSBedrock'),
}


def __getattr__(name: str):
	"""Lazy import mechanism for AWS chat models."""
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
	'ChatAWSBedrock',
	'ChatAnthropicBedrock',
]
