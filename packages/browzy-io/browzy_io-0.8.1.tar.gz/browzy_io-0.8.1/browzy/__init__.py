import os
from typing import TYPE_CHECKING

from browzy.logging_config import setup_logging

# Only set up logging if not in MCP mode or if explicitly requested
if os.environ.get('BROWZY_SETUP_LOGGING', 'true').lower() != 'false':
	from browzy.config import CONFIG

	# Get log file paths from config/environment
	debug_log_file = getattr(CONFIG, 'BROWZY_DEBUG_LOG_FILE', None)
	info_log_file = getattr(CONFIG, 'BROWZY_INFO_LOG_FILE', None)

	# Set up logging with file handlers if specified
	logger = setup_logging(debug_log_file=debug_log_file, info_log_file=info_log_file)
else:
	import logging

	logger = logging.getLogger('browzy')

# Monkeypatch BaseSubprocessTransport.__del__ to handle closed event loops gracefully
from asyncio import base_subprocess

_original_del = base_subprocess.BaseSubprocessTransport.__del__


def _patched_del(self):
	"""Patched __del__ that handles closed event loops without throwing noisy red-herring errors like RuntimeError: Event loop is closed"""
	try:
		# Check if the event loop is closed before calling the original
		if hasattr(self, '_loop') and self._loop and self._loop.is_closed():
			# Event loop is closed, skip cleanup that requires the loop
			return
		_original_del(self)
	except RuntimeError as e:
		if 'Event loop is closed' in str(e):
			# Silently ignore this specific error
			pass
		else:
			raise


base_subprocess.BaseSubprocessTransport.__del__ = _patched_del


# Type stubs for lazy imports - fixes linter warnings
if TYPE_CHECKING:
	from browzy.agent.prompts import SystemPrompt
	from browzy.agent.service import BrowzyAgent
	from browzy.agent.views import ActionModel, ActionResult, AgentHistoryList
	from browzy.browser import BrowserProfile, BrowserSession
	from browzy.browser import BrowserSession as BrowzyBrowser
	from browzy.dom.service import DomService
	from browzy.llm import models
	from browzy.llm.anthropic.chat import ChatAnthropic
	from browzy.llm.azure.chat import ChatAzureOpenAI
	from browzy.llm.browzy.chat import ChatBrowzy
	from browzy.llm.google.chat import ChatGoogle
	from browzy.llm.groq.chat import ChatGroq
	from browzy.llm.oci_raw.chat import ChatOCIRaw
	from browzy.llm.ollama.chat import ChatOllama
	from browzy.llm.openai.chat import ChatOpenAI
	from browzy.tools.service import Controller, Tools


# Lazy imports mapping - only import when actually accessed
_LAZY_IMPORTS = {
	# Agent service (heavy due to dependencies)
	'BrowzyAgent': ('browzy.agent.service', 'BrowzyAgent'),
	'Agent': ('browzy.agent.service', 'BrowzyAgent'),  # Backward compatibility
	# System prompt (moderate weight due to agent.views imports)
	'SystemPrompt': ('browzy.agent.prompts', 'SystemPrompt'),
	# Agent views (very heavy - over 1 second!)
	'ActionModel': ('browzy.agent.views', 'ActionModel'),
	'ActionResult': ('browzy.agent.views', 'ActionResult'),
	'AgentHistoryList': ('browzy.agent.views', 'AgentHistoryList'),
	'BrowserSession': ('browzy.browser', 'BrowserSession'),
	'BrowzyBrowser': ('browzy.browser', 'BrowserSession'),  # New alias
	'Browser': ('browzy.browser', 'BrowserSession'),  # Backward compatibility
	'BrowserProfile': ('browzy.browser', 'BrowserProfile'),
	# Tools (moderate weight)
	'Tools': ('browzy.tools.service', 'Tools'),
	'Controller': ('browzy.tools.service', 'Controller'),  # alias
	# DOM service (moderate weight)
	'DomService': ('browzy.dom.service', 'DomService'),
	# Chat models (very heavy imports)
	'ChatOpenAI': ('browzy.llm.openai.chat', 'ChatOpenAI'),
	'ChatGoogle': ('browzy.llm.google.chat', 'ChatGoogle'),
	'ChatAnthropic': ('browzy.llm.anthropic.chat', 'ChatAnthropic'),
	'ChatBrowzy': ('browzy.llm.browzy.chat', 'ChatBrowzy'),
	'ChatBrowserUse': ('browzy.llm.browzy.chat', 'ChatBrowzy'),  # Backward compatibility
	'ChatGroq': ('browzy.llm.groq.chat', 'ChatGroq'),
	'ChatAzureOpenAI': ('browzy.llm.azure.chat', 'ChatAzureOpenAI'),
	'ChatOCIRaw': ('browzy.llm.oci_raw.chat', 'ChatOCIRaw'),
	'ChatOllama': ('browzy.llm.ollama.chat', 'ChatOllama'),
	# LLM models module
	'models': ('browzy.llm.models', None),
}


def __getattr__(name: str):
	"""Lazy import mechanism - only import modules when they're actually accessed."""
	if name in _LAZY_IMPORTS:
		module_path, attr_name = _LAZY_IMPORTS[name]
		try:
			from importlib import import_module

			module = import_module(module_path)
			if attr_name is None:
				# For modules like 'models', return the module itself
				attr = module
			else:
				attr = getattr(module, attr_name)
			# Cache the imported attribute in the module's globals
			globals()[name] = attr
			return attr
		except ImportError as e:
			raise ImportError(f'Failed to import {name} from {module_path}: {e}') from e

	raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
	'BrowzyAgent',
	'Agent',  # Backward compatibility
	'BrowserSession',
	'BrowzyBrowser',  # New alias
	'Browser',  # Backward compatibility
	'BrowserProfile',
	'Controller',
	'DomService',
	'SystemPrompt',
	'ActionResult',
	'ActionModel',
	'AgentHistoryList',
	# Chat models
	'ChatOpenAI',
	'ChatGoogle',
	'ChatAnthropic',
	'ChatBrowzy',
	'ChatBrowserUse',  # Backward compatibility
	'ChatGroq',
	'ChatAzureOpenAI',
	'ChatOCIRaw',
	'ChatOllama',
	'Tools',
	'Controller',
	# LLM models module
	'models',
]
