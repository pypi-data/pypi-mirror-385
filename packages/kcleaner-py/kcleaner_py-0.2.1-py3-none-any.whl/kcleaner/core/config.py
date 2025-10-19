from pathlib import Path
import json
from typing import Union, Dict, Any
from .styles import SmartStyles as st
from .types import ConfigData
from ..utils.validator import SystemValidator
from .exceptions import SystemPermissionError, ConfigurationError, FileSystemError
from ..utils.file_utils import FileSystemHandler


class ConfigManager:
    """Kcleaner configuration manager"""

    def __init__(self):
        self.CONFIG_PATH = Path(__file__).home() / ".kcleaner" / "kcleaner_config.json"

        self.fh = FileSystemHandler()

        # ensure config dir exists
        self.fh.ensure_directory(self.CONFIG_PATH.parent)

        self.config = ConfigData()

    def __enter__(self):
        access, error = SystemValidator().validate_file_permissions(
            self.CONFIG_PATH.parent
        )
        if not access:
            raise SystemPermissionError("Permission error while accessing config path.")

    def set_config(
        self, key: str, value: str | int | float, extend: bool = True
    ) -> ConfigData:
        """
        Modifies theConfigData statically--does not update config file
        Args:
            key - str
            value - Union[str, int, float]
            extend weather to append to or extend current config valuesor replace
        Returns:
            ConfigDta object
        """
        if key not in self.config.__dict__.keys():
            raise ConfigurationError(f"The key: {key} is not valid configuration.")
        if extend:
            cf_dict = self.config.__dict__[key] = value
        else:
            cf_dict = self.config.__dict__[key] = value
        self.config = cf_dict

        return self.config

    def _update_file_config(self, config: Dict[str, Any]) -> object:
        """
        Updates the config file
        Args:
            config - dict
        Returns:
            ConfigDta object
        """
        try:
            with open(self.CONFIG_PATH, "w") as f:
                json.dump(config, f, indent=4)
            print(f"{st.INFO} Created default config at {self.CONFIG_PATH}")
        except Exception as e:
            raise FileSystemError(f"Could not write config file: {e}")

        return self.config

    def get_config(self, key: str) -> object:
        """
        Args:
            key -> str
        Returns:
            Default config defined in ConfigData object
        """
        if key not in self.config.__dict__.keys():
            raise ConfigurationError(f"Invalid configuration: {key}")
        return self.config.__dict__[key]

    def _config_to_dict(self, config: ConfigData = None) -> dict:
        """
        Args:
            key -> str
        Returns:
            Default config defined in ConfigData object
        """
        return config.__dict__.copy() if config else self.config.__dict__.copy()

    def load_config(self) -> object:
        """
        Loads config options from config file if it exists. Otherwise retruns
            ConfigData defaults and updates config file
        """
        if self.CONFIG_PATH.exists():
            with open(self.CONFIG_PATH, "r") as f:
                return json.load(f)
        else:
            return self._update_file_config(self.config.__dict__.copy())
