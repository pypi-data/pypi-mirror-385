"""
We have switched all of our code from langchain to openai.types.chat.chat_completion_message_param.

For easier transition we have
"""

from typing import TYPE_CHECKING

# Lightweight imports that are commonly used
from browzy.llm.base import BaseChatModel
from browzy.llm.messages import (
	AssistantMessage,
	BaseMessage,
	SystemMessage,
	UserMessage,
)
from browzy.llm.messages import (
	ContentPartImageParam as ContentImage,
)
from browzy.llm.messages import (
	ContentPartRefusalParam as ContentRefusal,
)
from browzy.llm.messages import (
	ContentPartTextParam as ContentText,
)

# Type stubs for lazy imports
if TYPE_CHECKING:
	from browzy.llm.anthropic.chat import ChatAnthropic
	from browzy.llm.aws.chat_anthropic import ChatAnthropicBedrock
	from browzy.llm.aws.chat_bedrock import ChatAWSBedrock
	from browzy.llm.azure.chat import ChatAzureOpenAI
	from browzy.llm.browzy.chat import ChatBrowzy
	from browzy.llm.cerebras.chat import ChatCerebras
	from browzy.llm.deepseek.chat import ChatDeepSeek
	from browzy.llm.google.chat import ChatGoogle
	from browzy.llm.groq.chat import ChatGroq
	from browzy.llm.oci_raw.chat import ChatOCIRaw
	from browzy.llm.ollama.chat import ChatOllama
	from browzy.llm.openai.chat import ChatOpenAI
	from browzy.llm.openrouter.chat import ChatOpenRouter

	# Type stubs for model instances - enables IDE autocomplete
	openai_gpt_4o: ChatOpenAI
	openai_gpt_4o_mini: ChatOpenAI
	openai_gpt_4_1_mini: ChatOpenAI
	openai_o1: ChatOpenAI
	openai_o1_mini: ChatOpenAI
	openai_o1_pro: ChatOpenAI
	openai_o3: ChatOpenAI
	openai_o3_mini: ChatOpenAI
	openai_o3_pro: ChatOpenAI
	openai_o4_mini: ChatOpenAI
	openai_gpt_5: ChatOpenAI
	openai_gpt_5_mini: ChatOpenAI
	openai_gpt_5_nano: ChatOpenAI

	azure_gpt_4o: ChatAzureOpenAI
	azure_gpt_4o_mini: ChatAzureOpenAI
	azure_gpt_4_1_mini: ChatAzureOpenAI
	azure_o1: ChatAzureOpenAI
	azure_o1_mini: ChatAzureOpenAI
	azure_o1_pro: ChatAzureOpenAI
	azure_o3: ChatAzureOpenAI
	azure_o3_mini: ChatAzureOpenAI
	azure_o3_pro: ChatAzureOpenAI
	azure_gpt_5: ChatAzureOpenAI
	azure_gpt_5_mini: ChatAzureOpenAI

	google_gemini_2_0_flash: ChatGoogle
	google_gemini_2_0_pro: ChatGoogle
	google_gemini_2_5_pro: ChatGoogle
	google_gemini_2_5_flash: ChatGoogle
	google_gemini_2_5_flash_lite: ChatGoogle

# Models are imported on-demand via __getattr__

# Lazy imports mapping for heavy chat models
_LAZY_IMPORTS = {
	'ChatAnthropic': ('browzy.llm.anthropic.chat', 'ChatAnthropic'),
	'ChatAnthropicBedrock': ('browzy.llm.aws.chat_anthropic', 'ChatAnthropicBedrock'),
	'ChatAWSBedrock': ('browzy.llm.aws.chat_bedrock', 'ChatAWSBedrock'),
	'ChatAzureOpenAI': ('browzy.llm.azure.chat', 'ChatAzureOpenAI'),
	'ChatBrowzy': ('browzy.llm.browzy.chat', 'ChatBrowzy'),
	'ChatBrowserUse': ('browzy.llm.browzy.chat', 'ChatBrowzy'),  # Backward compatibility
	'ChatCerebras': ('browzy.llm.cerebras.chat', 'ChatCerebras'),
	'ChatDeepSeek': ('browzy.llm.deepseek.chat', 'ChatDeepSeek'),
	'ChatGoogle': ('browzy.llm.google.chat', 'ChatGoogle'),
	'ChatGroq': ('browzy.llm.groq.chat', 'ChatGroq'),
	'ChatOCIRaw': ('browzy.llm.oci_raw.chat', 'ChatOCIRaw'),
	'ChatOllama': ('browzy.llm.ollama.chat', 'ChatOllama'),
	'ChatOpenAI': ('browzy.llm.openai.chat', 'ChatOpenAI'),
	'ChatOpenRouter': ('browzy.llm.openrouter.chat', 'ChatOpenRouter'),
}

# Cache for model instances - only created when accessed
_model_cache: dict[str, 'BaseChatModel'] = {}


def __getattr__(name: str):
	"""Lazy import mechanism for heavy chat model imports and model instances."""
	if name in _LAZY_IMPORTS:
		module_path, attr_name = _LAZY_IMPORTS[name]
		try:
			from importlib import import_module

			module = import_module(module_path)
			attr = getattr(module, attr_name)
			return attr
		except ImportError as e:
			raise ImportError(f'Failed to import {name} from {module_path}: {e}') from e

	# Check cache first for model instances
	if name in _model_cache:
		return _model_cache[name]

	# Try to get model instances from models module on-demand
	try:
		from browzy.llm.models import __getattr__ as models_getattr

		attr = models_getattr(name)
		# Cache in our clean cache dict
		_model_cache[name] = attr
		return attr
	except (AttributeError, ImportError):
		pass

	raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
	# Message types -> for easier transition from langchain
	'BaseMessage',
	'UserMessage',
	'SystemMessage',
	'AssistantMessage',
	# Content parts with better names
	'ContentText',
	'ContentRefusal',
	'ContentImage',
	# Chat models
	'BaseChatModel',
	'ChatOpenAI',
	'ChatBrowzy',
	'ChatBrowserUse',  # Backward compatibility
	'ChatDeepSeek',
	'ChatGoogle',
	'ChatAnthropic',
	'ChatAnthropicBedrock',
	'ChatAWSBedrock',
	'ChatGroq',
	'ChatAzureOpenAI',
	'ChatOCIRaw',
	'ChatOllama',
	'ChatOpenRouter',
	'ChatCerebras',
]
