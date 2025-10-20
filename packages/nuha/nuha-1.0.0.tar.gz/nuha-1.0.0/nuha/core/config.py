"""Configuration management for Nuha."""

import contextlib
import os
from enum import Enum
from pathlib import Path

import toml
from cryptography.fernet import Fernet
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIProvider(str, Enum):
    """Supported AI providers."""

    ZHIPUAI = "zhipuai"
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"


class AIConfig(BaseModel):
    """AI configuration."""

    provider: AIProvider = Field(default=AIProvider.ZHIPUAI)
    model: str = Field(default="glm-4.5-flash")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=32000)


class TerminalConfig(BaseModel):
    """Terminal configuration."""

    history_limit: int = Field(default=50, ge=1, le=1000)
    auto_analyze: bool = Field(default=True)
    include_context: bool = Field(default=True)


class OutputConfig(BaseModel):
    """Output configuration."""

    format: str = Field(default="rich")
    color: bool = Field(default=True)
    verbose: bool = Field(default=False)


class BehaviorConfig(BaseModel):
    """Behavior configuration."""

    auto_explain_errors: bool = Field(default=False)
    interactive_mode: bool = Field(default=True)
    save_analysis: bool = Field(default=True)


class Config(BaseSettings):
    """Main configuration class."""

    ai: AIConfig = Field(default_factory=AIConfig)
    terminal: TerminalConfig = Field(default_factory=TerminalConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    behavior: BehaviorConfig = Field(default_factory=BehaviorConfig)

    # API Keys (loaded from environment or encrypted storage)
    zhipuai_api_key: str | None = Field(default=None, alias="ZHIPUAI_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    deepseek_api_key: str | None = Field(default=None, alias="DEEPSEEK_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",  # Allow extra fields for API keys
    )

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get configuration directory path."""
        config_dir = Path.home() / ".nuha"
        config_dir.mkdir(exist_ok=True)
        return config_dir

    @classmethod
    def get_config_path(cls) -> Path:
        """Get configuration file path."""
        return cls.get_config_dir() / "config.toml"

    @classmethod
    def get_key_path(cls) -> Path:
        """Get encryption key path."""
        return cls.get_config_dir() / ".key"

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file."""
        config_path = cls.get_config_path()

        if not config_path.exists():
            # Return default config
            config = cls()
            config.save()
            return config

        try:
            with open(config_path) as f:
                data = toml.load(f)

            # Fix provider field if it's stored as a list of characters
            if "ai" in data and isinstance(data["ai"].get("provider"), list):
                data["ai"]["provider"] = "".join(data["ai"]["provider"])

            # Load encrypted API keys if they exist
            encrypted_keys = data.pop("encrypted_keys", {})
            if encrypted_keys:
                decrypted = cls._decrypt_keys(encrypted_keys)
                # Only add API key fields that don't already exist
                for key, value in decrypted.items():
                    if key not in data:
                        data[key] = value

            return cls(**data)
        except Exception as e:
            print(f"Warning: Could not load config: {e}. Using defaults.")
            return cls()

    def save(self) -> None:
        """Save configuration to file."""
        config_path = self.get_config_path()

        # Prepare config dict
        config_dict = {
            "ai": self.ai.model_dump(),
            "terminal": self.terminal.model_dump(),
            "output": self.output.model_dump(),
            "behavior": self.behavior.model_dump(),
        }

        # Encrypt API keys
        keys_to_encrypt = {
            "zhipuai_api_key": self.zhipuai_api_key,
            "openai_api_key": self.openai_api_key,
            "anthropic_api_key": self.anthropic_api_key,
            "deepseek_api_key": self.deepseek_api_key,
        }
        encrypted_keys = self._encrypt_keys(keys_to_encrypt)
        if encrypted_keys:
            config_dict["encrypted_keys"] = encrypted_keys

        # Save to file
        with open(config_path, "w") as f:
            toml.dump(config_dict, f)

    @classmethod
    def _get_or_create_key(cls) -> bytes:
        """Get or create encryption key."""
        key_path = cls.get_key_path()

        if key_path.exists():
            # Use a try-except block to handle any potential issues
            try:
                key_data = key_path.read_bytes()
                return key_data
            except Exception:
                # If reading fails, create a new key
                pass

        # Create new key
        key = Fernet.generate_key()
        key_path.write_bytes(key)
        key_path.chmod(0o600)  # Restrict permissions
        return key

    @classmethod
    def _encrypt_keys(cls, keys: dict[str, str | None]) -> dict[str, str]:
        """Encrypt API keys."""
        key = cls._get_or_create_key()
        fernet = Fernet(key)

        encrypted = {}
        for name, value in keys.items():
            if value:
                encrypted[name] = fernet.encrypt(value.encode()).decode()

        return encrypted

    @classmethod
    def _decrypt_keys(cls, encrypted_keys: dict[str, str]) -> dict[str, str]:
        """Decrypt API keys."""
        key = cls._get_or_create_key()
        fernet = Fernet(key)

        decrypted = {}
        for name, value in encrypted_keys.items():
            with contextlib.suppress(Exception):
                decrypted[name] = fernet.decrypt(value.encode()).decode()

        return decrypted

    def get_api_key(self, provider: AIProvider | None = None) -> str | None:
        """Get API key for the specified provider."""
        if provider is None:
            provider = self.ai.provider

        key_map = {
            AIProvider.ZHIPUAI: self.zhipuai_api_key,
            AIProvider.OPENAI: self.openai_api_key,
            AIProvider.CLAUDE: self.anthropic_api_key,
            AIProvider.DEEPSEEK: self.deepseek_api_key,
        }

        key = key_map.get(provider)
        if not key:
            # Try environment variable
            env_var_map = {
                AIProvider.ZHIPUAI: "ZHIPUAI_API_KEY",
                AIProvider.OPENAI: "OPENAI_API_KEY",
                AIProvider.CLAUDE: "ANTHROPIC_API_KEY",
                AIProvider.DEEPSEEK: "DEEPSEEK_API_KEY",
            }
            key = os.getenv(env_var_map.get(provider, ""))

        return key

    def set_api_key(self, provider: AIProvider, api_key: str) -> None:
        """Set API key for the specified provider."""
        if provider == AIProvider.ZHIPUAI:
            self.zhipuai_api_key = api_key
        elif provider == AIProvider.OPENAI:
            self.openai_api_key = api_key
        elif provider == AIProvider.CLAUDE:
            self.anthropic_api_key = api_key
        elif provider == AIProvider.DEEPSEEK:
            self.deepseek_api_key = api_key

        self.save()

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.ai = AIConfig()
        self.terminal = TerminalConfig()
        self.output = OutputConfig()
        self.behavior = BehaviorConfig()
        self.save()
