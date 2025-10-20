"""Configuration management for AnyTask CLI."""

import json
import os
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class EnvironmentConfig(BaseModel):
    """Configuration for a single environment."""

    api_url: str
    auth_token: Optional[str] = None
    agent_key: Optional[str] = None
    default_workspace: Optional[str] = None


class GlobalConfig(BaseModel):
    """Global CLI configuration."""

    current_environment: str = "prod"
    environments: dict[str, EnvironmentConfig] = Field(default_factory=dict)
    sync_interval: int = 15
    editor: str = "vim"
    color_scheme: str = "auto"

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the path to the global config file."""
        # Use XDG_CONFIG_HOME if set, otherwise ~/.config
        config_home = os.getenv("XDG_CONFIG_HOME")
        if config_home:
            config_dir = Path(config_home) / "anyt"
        else:
            config_dir = Path.home() / ".config" / "anyt"

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    @classmethod
    def load(cls) -> "GlobalConfig":
        """Load configuration from file."""
        config_path = cls.get_config_path()

        if not config_path.exists():
            # Create default config with prod and dev environments
            config = cls(
                current_environment="prod",
                environments={
                    "prod": EnvironmentConfig(
                        api_url="http://anyt.up.railway.app",
                    ),
                    "dev": EnvironmentConfig(
                        api_url="http://localhost:8000",
                    ),
                },
            )
            config.save()
            return config

        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return cls(**data)
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {config_path}: {e}")

    def save(self) -> None:
        """Save configuration to file."""
        config_path = self.get_config_path()

        try:
            with open(config_path, "w") as f:
                json.dump(self.model_dump(), f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save config to {config_path}: {e}")

    def get_current_env(self) -> EnvironmentConfig:
        """Get the current environment configuration."""
        env = self.environments.get(self.current_environment)
        if not env:
            raise ValueError(
                f"Environment '{self.current_environment}' not found in config"
            )
        return env

    def add_environment(
        self, name: str, api_url: str, make_active: bool = False
    ) -> None:
        """Add a new environment."""
        self.environments[name] = EnvironmentConfig(api_url=api_url)
        if make_active:
            self.current_environment = name
        self.save()

    def switch_environment(self, name: str) -> None:
        """Switch to a different environment."""
        if name not in self.environments:
            raise ValueError(f"Environment '{name}' not found in config")
        self.current_environment = name
        self.save()

    def remove_environment(self, name: str) -> None:
        """Remove an environment."""
        if name not in self.environments:
            raise ValueError(f"Environment '{name}' not found in config")

        # Don't allow removing the current environment
        if name == self.current_environment:
            raise ValueError(
                f"Cannot remove current environment '{name}'. "
                "Switch to a different environment first."
            )

        del self.environments[name]
        self.save()

    def get_effective_config(self) -> dict[str, Any]:
        """Get effective configuration including environment variable overrides."""
        config = {
            "environment": self.current_environment,
            "api_url": None,
            "auth_token": None,
            "agent_key": None,
        }

        # Start with file config
        env_config = self.get_current_env()
        config["api_url"] = env_config.api_url

        # Load agent_key if present
        if env_config.agent_key:
            config["agent_key"] = env_config.agent_key

        # Load auth_token if present
        if env_config.auth_token:
            # Detect if auth_token is actually an agent key
            if env_config.auth_token.startswith("anyt_agent_"):
                config["agent_key"] = env_config.auth_token
                config["auth_token"] = None
            else:
                config["auth_token"] = env_config.auth_token

        # Override with environment variables (highest priority)
        if api_url := os.getenv("ANYT_API_URL"):
            config["api_url"] = api_url

        if env_name := os.getenv("ANYT_ENV"):
            config["environment"] = env_name
            # Reload env config if environment was overridden
            if env_name in self.environments:
                env_config = self.environments[env_name]
                config["api_url"] = env_config.api_url

                # Load agent_key and auth_token from the overridden environment
                if env_config.agent_key:
                    config["agent_key"] = env_config.agent_key
                if env_config.auth_token:
                    # Detect if auth_token is actually an agent key
                    if env_config.auth_token.startswith("anyt_agent_"):
                        config["agent_key"] = env_config.auth_token
                        config["auth_token"] = None
                    else:
                        config["auth_token"] = env_config.auth_token

        if auth_token := os.getenv("ANYT_AUTH_TOKEN"):
            config["auth_token"] = auth_token
            # Clear agent_key if auth_token is set via env var
            config["agent_key"] = None

        if agent_key := os.getenv("ANYT_AGENT_KEY"):
            config["agent_key"] = agent_key
            # Clear auth_token if agent_key is set via env var
            config["auth_token"] = None

        return config


class WorkspaceConfig(BaseModel):
    """Local workspace configuration stored in anyt.json."""

    workspace_id: str
    name: str
    api_url: str
    last_sync: Optional[str] = None
    current_project_id: Optional[int] = None
    workspace_identifier: Optional[str] = None

    @classmethod
    def get_config_path(cls, directory: Optional[Path] = None) -> Path:
        """Get the path to the workspace config file."""
        if directory is None:
            directory = Path.cwd()

        return directory / ".anyt" / "anyt.json"

    @classmethod
    def load(cls, directory: Optional[Path] = None) -> Optional["WorkspaceConfig"]:
        """Load workspace configuration from file."""
        config_path = cls.get_config_path(directory)

        if not config_path.exists():
            return None

        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return cls(**data)
        except Exception:
            return None

    def save(self, directory: Optional[Path] = None) -> None:
        """Save workspace configuration to file."""
        config_path = self.get_config_path(directory)

        # Ensure .anyt directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, "w") as f:
                json.dump(self.model_dump(), f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save workspace config: {e}")


class ActiveTaskConfig(BaseModel):
    """Active task configuration stored in .anyt/active_task.json."""

    identifier: str
    title: str
    picked_at: str
    workspace_id: int
    project_id: int

    @classmethod
    def get_config_path(cls, directory: Optional[Path] = None) -> Path:
        """Get the path to the active task config file."""
        if directory is None:
            directory = Path.cwd()

        anyt_dir = directory / ".anyt"
        anyt_dir.mkdir(exist_ok=True)
        return anyt_dir / "active_task.json"

    @classmethod
    def load(cls, directory: Optional[Path] = None) -> Optional["ActiveTaskConfig"]:
        """Load active task configuration from file."""
        config_path = cls.get_config_path(directory)

        if not config_path.exists():
            return None

        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return cls(**data)
        except Exception:
            return None

    def save(self, directory: Optional[Path] = None) -> None:
        """Save active task configuration to file."""
        config_path = self.get_config_path(directory)

        try:
            with open(config_path, "w") as f:
                json.dump(self.model_dump(), f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save active task config: {e}")

    @classmethod
    def clear(cls, directory: Optional[Path] = None) -> None:
        """Clear the active task by removing the config file."""
        config_path = cls.get_config_path(directory)
        if config_path.exists():
            config_path.unlink()
