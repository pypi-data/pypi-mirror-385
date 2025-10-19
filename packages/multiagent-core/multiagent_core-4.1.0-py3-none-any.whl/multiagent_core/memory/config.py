"""Memory System Configuration

Handles configuration settings, validation, and defaults for the memory system.
"""

from typing import Dict, Any, Optional
import os
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class MemoryConfig:
    """Configuration manager for the memory system.
    
    Handles loading, validation, and access to memory system settings.
    """
    
    DEFAULT_CONFIG = {
        "storage": {
            "vector_db": {
                "type": "chromadb",
                "persist_directory": ".memory/chroma",
                "collection_name": "conversations"
            },
            "metadata_db": {
                "type": "sqlite",
                "database_path": ".memory/metadata.db"
            }
        },
        "performance": {
            "retrieval_timeout_ms": 500,
            "search_timeout_ms": 1000,
            "max_results": 50,
            "embedding_batch_size": 100
        },
        "cleanup": {
            "retention_days": 90,
            "min_confidence": 0.3,
            "auto_cleanup": True,
            "cleanup_interval_hours": 24
        },
        "features": {
            "semantic_search": True,
            "auto_associations": True,
            "pattern_learning": True,
            "cross_agent_sharing": True
        },
        "agents": {
            "supported_types": ["copilot", "claude", "gemini", "qwen", "codex"],
            "default_confidence": 0.8
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Optional path to custom config file
        """
        self.config_path = config_path
        self._config = self.DEFAULT_CONFIG.copy()
        self._load_config()
        
    def _load_config(self) -> None:
        """Load configuration from file or environment."""
        # Try to load from specified path
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    custom_config = json.load(f)
                self._merge_config(custom_config)
                logger.info(f"Loaded config from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
                
        # Try to load from default locations
        default_paths = [
            ".memory/config.json",
            os.path.expanduser("~/.multiagent/memory.json"),
            "/etc/multiagent/memory.json"
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        custom_config = json.load(f)
                    self._merge_config(custom_config)
                    logger.info(f"Loaded config from {path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load config from {path}: {e}")
                    
        # Load from environment variables
        self._load_env_config()
        
    def _merge_config(self, custom_config: Dict[str, Any]) -> None:
        """Merge custom configuration with defaults."""
        def merge_dict(base: Dict, custom: Dict) -> Dict:
            result = base.copy()
            for key, value in custom.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
            
        self._config = merge_dict(self._config, custom_config)
        
    def _load_env_config(self) -> None:
        """Load configuration from environment variables."""
        env_mapping = {
            "MEMORY_STORAGE_TYPE": ["storage", "vector_db", "type"],
            "MEMORY_PERSIST_DIR": ["storage", "vector_db", "persist_directory"],
            "MEMORY_RETENTION_DAYS": ["cleanup", "retention_days"],
            "MEMORY_MIN_CONFIDENCE": ["cleanup", "min_confidence"],
            "MEMORY_AUTO_CLEANUP": ["cleanup", "auto_cleanup"],
        }
        
        for env_var, config_path in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value:
                # Navigate to the nested config location
                current = self._config
                for key in config_path[:-1]:
                    current = current.setdefault(key, {})
                
                # Convert value to appropriate type
                final_key = config_path[-1]
                if final_key in ["retention_days", "cleanup_interval_hours"]:
                    current[final_key] = int(env_value)
                elif final_key in ["min_confidence"]:
                    current[final_key] = float(env_value)
                elif final_key in ["auto_cleanup"]:
                    current[final_key] = env_value.lower() in ["true", "1", "yes"]
                else:
                    current[final_key] = env_value
                    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key path.
        
        Args:
            key_path: Dot-separated path (e.g., "storage.vector_db.type")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value by dot-notation key path.
        
        Args:
            key_path: Dot-separated path
            value: Value to set
        """
        keys = key_path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value
        
    def validate(self) -> bool:
        """Validate the current configuration.
        
        Returns:
            bool: True if configuration is valid
        """
        try:
            # Validate required sections
            required_sections = ["storage", "performance", "cleanup", "features", "agents"]
            for section in required_sections:
                if section not in self._config:
                    logger.error(f"Missing required config section: {section}")
                    return False
                    
            # Validate storage configuration
            storage_type = self.get("storage.vector_db.type")
            if storage_type not in ["chromadb"]:
                logger.error(f"Unsupported storage type: {storage_type}")
                return False
                
            # Validate performance settings
            if self.get("performance.retrieval_timeout_ms", 0) <= 0:
                logger.error("Invalid retrieval timeout")
                return False
                
            # Validate cleanup settings
            retention_days = self.get("cleanup.retention_days", 0)
            if retention_days <= 0:
                logger.error("Invalid retention days")
                return False
                
            # Validate agent types
            supported_agents = self.get("agents.supported_types", [])
            if not supported_agents:
                logger.error("No supported agent types configured")
                return False
                
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
            
    def save(self, path: Optional[str] = None) -> bool:
        """Save current configuration to file.
        
        Args:
            path: Optional path to save to (defaults to loaded path)
            
        Returns:
            bool: True if saved successfully
        """
        save_path = path or self.config_path or ".memory/config.json"
        
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Configuration saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
            
    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        return self._config.copy()
        
    def __repr__(self) -> str:
        return f"MemoryConfig(path={self.config_path})"