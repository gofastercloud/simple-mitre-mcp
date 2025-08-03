"""
Configuration file loading and validation for the MCP server.

This module handles loading and validating YAML configuration files
for data sources, entity schemas, and tool definitions.
"""

import os
import yaml
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """
    Load all configuration files and merge them into a single configuration.

    Returns:
        dict: Merged configuration from all config files

    Raises:
        FileNotFoundError: If required config files are missing
        yaml.YAMLError: If config files contain invalid YAML
    """
    config = {}

    # Load data sources configuration
    data_sources_path = 'config/data_sources.yaml'
    if os.path.exists(data_sources_path):
        with open(data_sources_path, 'r') as f:
            data_sources_config = yaml.safe_load(f)
            config['data_sources'] = data_sources_config.get('data_sources', {})
            logger.info(f"Loaded {len(config['data_sources'])} data sources")
    else:
        logger.warning(f"Data sources config file not found: {data_sources_path}")
        config['data_sources'] = {}

    # Load entity schemas configuration
    entity_schemas_path = 'config/entity_schemas.yaml'
    if os.path.exists(entity_schemas_path):
        with open(entity_schemas_path, 'r') as f:
            entity_schemas_config = yaml.safe_load(f)
            config['entity_schemas'] = entity_schemas_config.get('entity_schemas', {})
            logger.info(f"Loaded {len(config['entity_schemas'])} entity schemas")
    else:
        logger.warning(f"Entity schemas config file not found: {entity_schemas_path}")
        config['entity_schemas'] = {}

    # Load tools configuration if it exists
    tools_path = 'config/tools.yaml'
    if os.path.exists(tools_path):
        with open(tools_path, 'r') as f:
            tools_config = yaml.safe_load(f)
            config['tools'] = tools_config.get('tools', {})
            logger.info(f"Loaded {len(config['tools'])} tool configurations")
    else:
        logger.info(f"Tools config file not found: {tools_path} (optional)")
        config['tools'] = {}

    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate the loaded configuration for required fields and structure.

    Args:
        config: Configuration dictionary to validate

    Returns:
        bool: True if configuration is valid

    Raises:
        ValueError: If configuration is invalid
    """
    # Validate data sources
    if 'data_sources' not in config:
        raise ValueError("Missing 'data_sources' in configuration")

    for source_name, source_config in config['data_sources'].items():
        if 'url' not in source_config:
            raise ValueError(f"Data source '{source_name}' missing required 'url' field")
        if 'format' not in source_config:
            raise ValueError(f"Data source '{source_name}' missing required 'format' field")
        if 'entity_types' not in source_config:
            raise ValueError(f"Data source '{source_name}' missing required 'entity_types' field")

    # Validate entity schemas
    if 'entity_schemas' not in config:
        raise ValueError("Missing 'entity_schemas' in configuration")

    for schema_name, schema_config in config['entity_schemas'].items():
        if 'id_field' not in schema_config:
            raise ValueError(f"Entity schema '{schema_name}' missing required 'id_field'")
        if 'name_field' not in schema_config:
            raise ValueError(f"Entity schema '{schema_name}' missing required 'name_field'")
        if 'required_fields' not in schema_config:
            raise ValueError(f"Entity schema '{schema_name}' missing required 'required_fields'")

    logger.info("Configuration validation passed")
    return True


class ConfigLoader:
    """
    Configuration loader class for handling different types of configuration files.
    """

    def __init__(self):
        """Initialize the configuration loader."""
        self.config_dir = 'config'

    def load_tools_config(self) -> Dict[str, Any]:
        """
        Load tools configuration from tools.yaml file.

        Returns:
            dict: Tools configuration
        """
        tools_path = os.path.join(self.config_dir, 'tools.yaml')

        if not os.path.exists(tools_path):
            logger.warning(f"Tools config file not found: {tools_path}")
            return {'tools': {}}

        try:
            with open(tools_path, 'r') as f:
                tools_config = yaml.safe_load(f)
                logger.info(f"Loaded {len(tools_config.get('tools', {}))} tool configurations")
                return tools_config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing tools config file: {e}")
            return {'tools': {}}
        except Exception as e:
            logger.error(f"Error loading tools config file: {e}")
            return {'tools': {}}

    def load_data_sources_config(self) -> Dict[str, Any]:
        """
        Load data sources configuration from data_sources.yaml file.

        Returns:
            dict: Data sources configuration
        """
        data_sources_path = os.path.join(self.config_dir, 'data_sources.yaml')

        if not os.path.exists(data_sources_path):
            logger.warning(f"Data sources config file not found: {data_sources_path}")
            return {'data_sources': {}}

        try:
            with open(data_sources_path, 'r') as f:
                data_sources_config = yaml.safe_load(f)
                logger.info(f"Loaded {len(data_sources_config.get('data_sources', {}))} data sources")
                return data_sources_config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing data sources config file: {e}")
            return {'data_sources': {}}
        except Exception as e:
            logger.error(f"Error loading data sources config file: {e}")
            return {'data_sources': {}}
