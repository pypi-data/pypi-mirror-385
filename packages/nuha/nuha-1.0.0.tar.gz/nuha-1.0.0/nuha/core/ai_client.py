"""AI client for interacting with different AI providers."""

from abc import ABC, abstractmethod
from collections.abc import Iterable

from anthropic import Anthropic
from anthropic.types import MessageParam
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from zhipuai import ZhipuAI

from nuha.core.config import AIProvider, Config

Message = dict[str, str]
ConversationHistory = list[Message]
OpenAIMessages = Iterable[ChatCompletionMessageParam]
AnthropicMessages = Iterable[MessageParam]


class BaseAIProvider(ABC):
    """Base class for AI providers."""

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def chat(self, messages: ConversationHistory) -> str:
        """Send a chat request and get response."""
        pass


class ZhipuAIProvider(BaseAIProvider):
    """ZHIPUAI provider implementation."""

    def __init__(
        self, api_key: str, model: str, temperature: float, max_tokens: int
    ) -> None:
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = ZhipuAI(api_key=api_key, base_url="https://api.z.ai/api/paas/v4/")

    def chat(self, messages: ConversationHistory) -> str:
        """Send a chat request to ZHIPUAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore[arg-type]  # ZHIPUAI accepts simpler format
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        # Handle response safely - pyrefly sees this as StreamResponse
        if hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content
            return str(content) if content is not None else ""
        else:
            return ""


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider implementation."""

    def __init__(
        self, api_key: str, model: str, temperature: float, max_tokens: int
    ) -> None:
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = OpenAI(api_key=api_key)

    def chat(self, messages: ConversationHistory) -> str:
        """Send a chat request to OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore[arg-type]  # Cast to OpenAI format
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        content = response.choices[0].message.content
        return str(content) if content is not None else ""


class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider implementation."""

    def __init__(
        self, api_key: str, model: str, temperature: float, max_tokens: int
    ) -> None:
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = Anthropic(api_key=api_key)

    def chat(self, messages: ConversationHistory) -> str:
        """Send a chat request to Claude."""
        # Claude expects system message separately
        system_message: str | None = None
        user_messages: list[dict[str, str]] = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_message,
            messages=user_messages,  # type: ignore[arg-type]  # Cast to Anthropic format
        )

        # Handle different response content types safely
        for content_block in response.content:
            if hasattr(content_block, "text"):
                return str(content_block.text)

        # Fallback if no text content found
        return ""


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek provider implementation (OpenAI-compatible API)."""

    def __init__(
        self, api_key: str, model: str, temperature: float, max_tokens: int
    ) -> None:
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    def chat(self, messages: ConversationHistory) -> str:
        """Send a chat request to DeepSeek."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore[arg-type]  # Cast to OpenAI format
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        content = response.choices[0].message.content
        return str(content) if content is not None else ""


class AIClient:
    """Main AI client that manages different providers."""

    def __init__(self, config: Config | None = None) -> None:
        """Initialize AI client with configuration."""
        self.config = config or Config.load()
        self._provider: BaseAIProvider | None = None

    def _get_provider(self) -> BaseAIProvider:
        """Get the appropriate AI provider based on configuration."""
        if self._provider:
            return self._provider

        provider_type = self.config.ai.provider
        api_key = self.config.get_api_key(provider_type)

        if not api_key:
            raise ValueError(
                f"API key not configured for provider: {provider_type.value}. "
                f"Please run 'nuha setup' or set the appropriate environment variable."
            )

        # Get model defaults based on provider
        model = self._get_default_model(provider_type)

        provider_map: dict[AIProvider, type[BaseAIProvider]] = {
            AIProvider.ZHIPUAI: ZhipuAIProvider,
            AIProvider.OPENAI: OpenAIProvider,
            AIProvider.CLAUDE: ClaudeProvider,
            AIProvider.DEEPSEEK: DeepSeekProvider,
        }

        provider_class = provider_map.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unsupported AI provider: {provider_type.value}")

        # Create provider instance with proper type
        provider_instance = provider_class(  # type: ignore[bad-instantiation]
            api_key=api_key,
            model=model,
            temperature=self.config.ai.temperature,
            max_tokens=self.config.ai.max_tokens,
        )
        self._provider = provider_instance

        return self._provider

    def _get_default_model(self, provider: AIProvider) -> str:
        """Get default model for provider if not configured."""
        if self.config.ai.model and self.config.ai.model != "glm-4.5-flash":
            return self.config.ai.model

        model_defaults = {
            AIProvider.ZHIPUAI: "glm-4.5-flash",
            AIProvider.OPENAI: "gpt-4-turbo-preview",
            AIProvider.CLAUDE: "claude-3-5-sonnet-20241022",
            AIProvider.DEEPSEEK: "deepseek-chat",
        }

        return model_defaults.get(provider, self.config.ai.model)

    def chat(self, messages: ConversationHistory) -> str:
        """Send a chat request to the configured AI provider."""
        provider = self._get_provider()
        return provider.chat(messages)

    def explain_command(
        self,
        command: str,
        error: str | None = None,
        context: dict[str, str | list[str]] | None = None,
    ) -> str:
        """Explain a command and its potential errors."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Nuha, an expert terminal assistant. Your role is to help users "
                    "understand and debug terminal commands. Provide clear, concise explanations "
                    "with actionable solutions. Format your responses with:\n"
                    "1. **Problem Analysis**: What went wrong\n"
                    "2. **Solution**: Step-by-step fix\n"
                    "3. **Prevention**: How to avoid this in the future"
                ),
            }
        ]

        # Build user message
        user_content = f"Command: `{command}`\n\n"

        if error:
            user_content += f"Error output:\n```\n{error}\n```\n\n"

        if context:
            user_content += "Context:\n"
            if "shell" in context:
                user_content += f"- Shell: {context['shell']}\n"
            if "cwd" in context:
                user_content += f"- Working directory: {context['cwd']}\n"
            if "recent_commands" in context:
                recent_commands = context["recent_commands"]
                if isinstance(recent_commands, list):
                    user_content += f"- Recent commands: {', '.join(str(cmd) for cmd in recent_commands[:5])}\n"

        user_content += "\nPlease explain what happened and how to fix it."

        messages.append({"role": "user", "content": user_content})

        return self.chat(messages)

    def analyze_patterns(self, commands: list[str]) -> str:
        """Analyze command patterns and provide insights."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Nuha, an expert terminal assistant. Analyze command patterns "
                    "and provide insights about efficiency, common mistakes, and best practices."
                ),
            },
            {
                "role": "user",
                "content": f"Analyze these recent commands:\n\n"
                f"{chr(10).join(f'{i + 1}. {cmd}' for i, cmd in enumerate(commands))}\n\n"
                f"Provide insights about patterns, potential issues, and optimization opportunities.",
            },
        ]

        return self.chat(messages)

    def interactive_debug(
        self, query: str, conversation_history: ConversationHistory | None = None
    ) -> str:
        """Handle interactive debugging session."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Nuha, an expert terminal assistant. You're in an interactive "
                    "debugging session. Help the user troubleshoot their terminal issues "
                    "with clear, actionable guidance. Ask follow-up questions when needed."
                ),
            }
        ]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": query})

        return self.chat(messages)

    def set_provider(self, provider: AIProvider) -> None:
        """Change the AI provider."""
        self.config.ai.provider = provider
        self._provider = None  # Reset provider to force recreation
