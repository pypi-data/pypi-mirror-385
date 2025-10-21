"""
Configuration classes for the Azcore..

This module provides configuration management with YAML and environment
variable support, validation, and type safety.
"""

from typing import Optional, Dict, Any
from pathlib import Path
import yaml
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
import logging

logger = logging.getLogger(__name__)


class Config:
    """
    Main configuration class for the Azcore..
    
    Supports loading from YAML files and environment variables with
    validation and type conversion.
    
    Example:
        >>> config = Config.from_yaml("config.yml")
        >>> llm = config.get_llm()
        >>> embeddings = config.get_embeddings()
    """
    
    def __init__(self, config_dict: Dict[str, Any]):
        """
        Initialize configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
        """
        self._config = config_dict
        self._logger = logging.getLogger(self.__class__.__name__)
        
        self._logger.info("Configuration initialized")
    
    @classmethod
    def from_yaml(cls, config_path: str | Path) -> 'Config':
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Config instance
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        
        logger.info(f"Loaded configuration from {config_path}")
        
        return cls(config_dict)
    
    @classmethod
    def from_env(cls, env_file: str | Path = ".env") -> 'Config':
        """
        Load configuration from environment variables.
        
        Args:
            env_file: Path to .env file (default: .env)
            
        Returns:
            Config instance
        """
        load_dotenv(env_file)
        
        config_dict = {
            "llm": {
                "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.5")),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "fast_llm": {
                "model": os.getenv("FAST_LLM_MODEL", "gpt-4o-mini"),
                "temperature": float(os.getenv("FAST_LLM_TEMPERATURE", "0.5")),
            },
            "coordinator_llm": {
                "model": os.getenv("COORDINATOR_LLM_MODEL", "gpt-4o-mini"),
                "temperature": float(os.getenv("COORDINATOR_LLM_TEMPERATURE", "0")),
            },
            "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
        }
        
        logger.info("Loaded configuration from environment variables")
        
        return cls(config_dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation: "llm.model")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._logger.debug(f"Set config: {key} = {value}")
    
    def get_llm(
        self,
        llm_key: str = "llm",
        provider: str = "openai"
    ) -> BaseChatModel:
        """
        Get a language model from configuration.
        
        Args:
            llm_key: Configuration key for LLM settings (default: "llm")
            provider: LLM provider (default: "openai")
            
        Returns:
            Configured language model
            
        Raises:
            ValueError: If provider is not supported
        """
        llm_config = self.get(llm_key, {})
        
        if provider == "openai":
            return ChatOpenAI(
                model=llm_config.get("model", "gpt-4o-mini"),
                temperature=llm_config.get("temperature", 0.5),
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def get_embeddings(
        self,
        provider: str = "openai"
    ) -> Embeddings:
        """
        Get embeddings model from configuration.
        
        Args:
            provider: Embeddings provider (default: "openai")
            
        Returns:
            Configured embeddings model
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider == "openai":
            model = self.get("embedding_model", "text-embedding-3-large")
            return OpenAIEmbeddings(model=model)
        else:
            raise ValueError(f"Unsupported embeddings provider: {provider}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()
    
    def save(self, output_path: str | Path) -> None:
        """
        Save configuration to YAML file.
        
        Args:
            output_path: Path to save configuration
        """
        output_path = Path(output_path)
        
        with open(output_path, 'w') as file:
            yaml.dump(self._config, file, default_flow_style=False)
        
        self._logger.info(f"Saved configuration to {output_path}")
    
    def __repr__(self) -> str:
        return f"Config(keys={list(self._config.keys())})"


def load_config(
    config_path: Optional[str | Path] = None,
    env_file: Optional[str | Path] = None
) -> Config:
    """
    Load configuration from file or environment.
    
    Priority:
    1. YAML file if config_path provided
    2. Environment variables if env_file provided
    3. Default .env in current directory
    
    Args:
        config_path: Optional path to YAML config file
        env_file: Optional path to .env file
        
    Returns:
        Config instance
    """
    if config_path:
        return Config.from_yaml(config_path)
    elif env_file:
        return Config.from_env(env_file)
    else:
        # Try default locations
        if Path("config.yml").exists():
            return Config.from_yaml("config.yml")
        elif Path(".env").exists():
            return Config.from_env(".env")
        else:
            logger.warning("No configuration file found, using defaults")
            return Config({})
