"""
Simplified configuration module using loguru-based logging system.
Replaces the complex stdlib logging + loguru approach with pure loguru.
"""

import os
import sys

import appdirs
import yaml
from loguru import logger

from netbox_network_importer import __appname__
from netbox_network_importer.logging_config import setup_logging

os.environ["XDG_CONFIG_DIRS"] = "/etc"
CONFIG_DIRS = (
    appdirs.user_config_dir(__appname__),
    appdirs.site_config_dir(__appname__),
)
CONFIG_FILENAME = "config.yml"


def get_config():
    """
    Get config file and load it with yaml
    :returns: loaded config in yaml, as a dict object
    """
    if getattr(get_config, "cache", None):
        return get_config.cache

    if os.environ.get("CONFIG_FOLDER_PATH"):
        config_path = os.path.join(os.environ["CONFIG_FOLDER_PATH"], CONFIG_FILENAME)
    else:
        for d in CONFIG_DIRS:
            config_path = os.path.join(d, CONFIG_FILENAME)
            if os.path.isfile(config_path):
                break

    try:
        with open(config_path, "r") as config_file:
            conf = yaml.safe_load(config_file)
            get_config.cache = conf
            return conf
    except FileNotFoundError as e:
        logger.debug(e)
        if os.environ.get("CONFIG_FOLDER_PATH"):
            logger.error(
                "Configuration file not found at {}.".format(
                    os.environ["CONFIG_FOLDER_PATH"]
                )
            )
        else:
            logger.error(
                "No configuration file can be found. Please create a "
                "config.yml in one of these directories:\n"
                "{}".format(", ".join(CONFIG_DIRS))
            )
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        sys.exit(1)


def clear_config_cache():
    """
    Clear the cached configuration, forcing reload on next get_config() call
    """
    if hasattr(get_config, "cache"):
        delattr(get_config, "cache")


def setup_logger(file: bool = True, stderr: bool = True):
    """
    Setup logger using the new loguru-based system

    Args:
        file: Enable file logging
        stderr: Enable console logging
    """
    try:
        config = get_config()
        setup_logging(config, enable_file_logging=file, enable_console_logging=stderr)
    except Exception as e:
        # Fallback to basic loguru setup if config fails
        logger.remove()
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
        )
        logger.error(f"Failed to setup logging from config: {e}")
        raise


# Utility functions for component-specific logging
def get_napalm_logger(host: str):
    """Get logger for NAPALM operations"""
    from netbox_network_importer.logging_config import NetworkLogger

    return NetworkLogger(host, "napalm")


def get_netbox_logger(operation: str):
    """Get logger for NetBox operations"""
    from netbox_network_importer.logging_config import get_component_logger

    return get_component_logger("netbox").bind(operation=operation)


def get_sync_logger(host: str, task: str):
    """Get logger for synchronization operations"""
    from netbox_network_importer.logging_config import NetworkLogger

    return NetworkLogger(host, f"sync_{task}")
