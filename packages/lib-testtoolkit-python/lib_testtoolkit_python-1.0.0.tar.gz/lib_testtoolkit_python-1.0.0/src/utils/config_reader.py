"""
A utility for reading and accessing configuration values from YAML files.
Supports environment variable substitution using Mustache templating.
"""

import os
import yaml
import pystache
from typing import Any, Dict, Optional, Union


class ConfigReader:
    """
    A utility for reading and accessing configuration values from YAML files.
    Supports environment variable substitution using Mustache templating.
    """
    
    # Default config location
    DEFAULT_CONFIG_FILE = "config/config.yaml"
    
    _instance: Optional['ConfigReader'] = None
    
    def __init__(self, config_file: str = DEFAULT_CONFIG_FILE):
        """
        Initialize ConfigReader with a configuration file.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    @classmethod
    def get_instance(cls) -> 'ConfigReader':
        """
        Gets the singleton instance of the ConfigReader.
        
        Returns:
            The ConfigReader instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """
        Resets the singleton instance. Useful for testing or when
        configuration needs to be reloaded.
        """
        cls._instance = None
    
    @classmethod
    def with_config_file(cls, config_file_path: str) -> 'ConfigReader':
        """
        Creates a ConfigReader instance with a custom configuration file path.
        
        Args:
            config_file_path: The path to the configuration file
            
        Returns:
            A new ConfigReader instance
        """
        cls.reset()
        cls._instance = cls(config_file_path)
        return cls._instance
    
    def _load_config(self) -> None:
        """Load configuration from the specified file."""
        self.config = self.load_configuration(self.config_file)
    
    def load_configuration(self, config_file_name: str) -> Dict[str, Any]:
        """
        Loads configuration from a specified YAML file.
        
        Args:
            config_file_name: The path to the configuration file
            
        Returns:
            A dictionary of configuration properties
            
        Raises:
            RuntimeError: If the configuration file cannot be found or loaded
        """
        try:
            # Try to find the file in different locations
            file_path = self._find_config_file(config_file_name)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Create a context map with environment variables
            context = self._create_environment_context()
            
            # Process the template using Mustache
            rendered_content = pystache.render(content, context)
            
            # Load the processed YAML
            config = yaml.safe_load(rendered_content)
            return config if config is not None else {}
            
        except FileNotFoundError:
            raise RuntimeError(f"Unable to find {config_file_name}")
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML configuration: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading configuration properties: {e}")
    
    def _find_config_file(self, config_file_name: str) -> str:
        """
        Find the configuration file in different possible locations.
        
        Args:
            config_file_name: Name of the configuration file
            
        Returns:
            Path to the found configuration file
            
        Raises:
            FileNotFoundError: If file is not found in any location
        """
        # Try different locations
        locations = [
            config_file_name,  # As provided
            os.path.join(os.getcwd(), config_file_name),  # Current directory
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', config_file_name),  # Relative to module
        ]
        
        for location in locations:
            if os.path.exists(location):
                return location
        
        raise FileNotFoundError(f"Configuration file {config_file_name} not found in any location")
    
    def _create_environment_context(self) -> Dict[str, str]:
        """
        Create a context map with environment variables for Mustache templating.
        
        Returns:
            Dictionary containing environment variables
        """
        return dict(os.environ)
    
    def get_base_url(self) -> Optional[str]:
        """
        Gets the base URL from the configuration.
        
        Returns:
            The base URL string or None if not found
        """
        return self.get_property("base_url")
    
    def get_property(self, key: str, default_value: Optional[str] = None) -> Optional[str]:
        """
        Gets a property from the configuration.
        
        Args:
            key: The property key
            default_value: The default value to return if the key is not found
            
        Returns:
            The property value as a string, or default_value if not found
        """
        value = self.config.get(key)
        if value is not None:
            return str(value)
        return default_value
    
    def get_int_property(self, key: str, default_value: int = 0) -> int:
        """
        Gets an integer property from the configuration.
        
        Args:
            key: The property key
            default_value: The default value to return if the key is not found or invalid
            
        Returns:
            The property value as an integer, or default_value if not found or invalid
        """
        value = self.get_property(key)
        if value is None:
            return default_value
        
        try:
            return int(value)
        except ValueError:
            return default_value
    
    def get_boolean_property(self, key: str, default_value: bool = False) -> bool:
        """
        Gets a boolean property from the configuration.
        
        Args:
            key: The property key
            default_value: The default value to return if the key is not found
            
        Returns:
            The property value as a boolean, or default_value if not found
        """
        value = self.get_property(key)
        if value is None:
            return default_value
        
        # Handle various boolean representations
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'on')
        
        return bool(value)
    
    def get_float_property(self, key: str, default_value: float = 0.0) -> float:
        """
        Gets a float property from the configuration.
        
        Args:
            key: The property key
            default_value: The default value to return if the key is not found or invalid
            
        Returns:
            The property value as a float, or default_value if not found or invalid
        """
        value = self.get_property(key)
        if value is None:
            return default_value
        
        try:
            return float(value)
        except ValueError:
            return default_value
    
    def get_list_property(self, key: str, default_value: Optional[list] = None) -> list:
        """
        Gets a list property from the configuration.
        
        Args:
            key: The property key
            default_value: The default value to return if the key is not found
            
        Returns:
            The property value as a list, or default_value if not found
        """
        if default_value is None:
            default_value = []
        
        value = self.config.get(key)
        if value is None:
            return default_value
        
        if isinstance(value, list):
            return value
        
        # Try to convert single value to list
        return [value]
    
    def get_config(self) -> Dict[str, Any]:
        """
        Gets the entire configuration as a dictionary.
        
        Returns:
            A copy of the configuration dictionary
        """
        return self.config.copy()
    
    def has_property(self, key: str) -> bool:
        """
        Check if a property exists in the configuration.
        
        Args:
            key: The property key to check
            
        Returns:
            True if the property exists, False otherwise
        """
        return key in self.config
    
    def get_nested_property(self, key_path: str, separator: str = ".", default_value: Any = None) -> Any:
        """
        Gets a nested property from the configuration using dot notation.
        
        Args:
            key_path: The property key path (e.g., "database.host")
            separator: The separator used in the key path
            default_value: The default value to return if the key is not found
            
        Returns:
            The property value or default_value if not found
        """
        keys = key_path.split(separator)
        current = self.config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default_value
        
        return current 