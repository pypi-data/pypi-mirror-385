"""Configuration manager for loading, merging, and validating settings.

This module provides the `ConfigManager` class, which handles YAML configuration
files by merging default and user-provided settings and validating them against
Pydantic models.

Example:
    >>> from culicidaelab.core.config_manager import ConfigManager
    >>> # Initialize with default settings
    >>> manager = ConfigManager()
    >>> config = manager.get_config()
    >>> print(config.app_settings.environment)

    >>> # Override with user settings
    >>> user_manager = ConfigManager(user_config_dir="/path/to/user/conf")
    >>> user_config = user_manager.get_config()
"""

from __future__ import annotations

import inspect
from importlib import resources
from pathlib import Path
from types import ModuleType
from typing import Any, TypeAlias, TypeVar, Union, cast

import yaml
from omegaconf import OmegaConf
from pydantic import ValidationError

from culicidaelab.core.config_models import CulicidaeLabConfig

ConfigDict: TypeAlias = dict[str, Any]
"""Type alias for a dictionary representing a configuration."""

ConfigPath: TypeAlias = Union[Path, ModuleType, str, None]
"""Type alias for a path to a configuration file or directory."""

T = TypeVar("T")
"""Generic type variable."""


def _deep_merge(source: dict, destination: dict) -> dict:
    """Recursively merges two dictionaries. Source values overwrite destination.

    Args:
        source (dict): The dictionary with values to merge.
        destination (dict): The dictionary to be merged into.

    Returns:
        dict: The merged dictionary.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            _deep_merge(value, node)
        else:
            destination[key] = value
    return destination


class ConfigManager:
    """Handles loading, merging, and validating configurations for the library.

    This manager implements a robust loading strategy:
    1. Loads default YAML configurations bundled with the library.
    2. Loads user-provided YAML configurations from a specified directory.
    3. Merges the user's configuration on top of the defaults.
    4. Validates the final merged configuration against Pydantic models.

    Attributes:
        user_config_dir (Path | None): The user configuration directory.
        default_config_path (Path): The path to the default config directory.
        config (CulicidaeLabConfig): The validated configuration object.
    """

    def __init__(self, user_config_dir: str | Path | None = None):
        """Initializes the ConfigManager.

        Args:
            user_config_dir (str | Path, optional): Path to a directory containing
                user-defined YAML configuration files. These will override the
                defaults. Defaults to None.
        """
        self.user_config_dir = Path(user_config_dir) if user_config_dir else None
        self.default_config_path = self._get_default_config_path()
        self.config: CulicidaeLabConfig = self._load()

    def get_config(self) -> CulicidaeLabConfig:
        """Returns the fully validated Pydantic configuration object.

        Returns:
            CulicidaeLabConfig: The `CulicidaeLabConfig` Pydantic model instance.
        """
        return self.config

    def instantiate_from_config(
        self,
        config_obj: Any,
        extra_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Instantiates a Python object from its Pydantic config model.

        The config model must have a `target` field specifying the fully
        qualified class path (e.g., 'my_module.my_class.MyClass').

        Args:
            config_obj (Any): A Pydantic model instance (e.g., a predictor config).
            extra_params (dict[str, Any] | None, optional): A dictionary of
                extra parameters to inject into the constructor. Defaults to None.
            **kwargs (Any): Additional keyword arguments to pass to the object's
                constructor, overriding any existing parameters in the config.

        Returns:
            Any: An instantiated Python object.

        Raises:
            ValueError: If the `target` key is not found in the config object.
            ImportError: If the class could not be imported and instantiated.
        """
        if not hasattr(config_obj, "target"):
            raise ValueError("Target key 'target' not found in configuration object")

        targetpath = config_obj.target
        config_params = config_obj.model_dump()
        config_params.pop("target", None)
        final_params = {}
        if extra_params:
            final_params.update(extra_params)
        final_params.update(config_params)
        final_params.update(kwargs)

        try:
            module_path, class_name = targetpath.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)

            sig = inspect.signature(cls)

            has_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())

            if not has_kwargs:
                # Filter final_params to only include keys that are in the signature
                allowed_keys = set(sig.parameters.keys())
                filtered_params = {k: v for k, v in final_params.items() if k in allowed_keys}
            else:
                filtered_params = final_params

            return cls(**filtered_params)
        except (ValueError, ImportError, AttributeError, TypeError) as e:
            raise ImportError(
                f"Could not import and instantiate '{targetpath}': {e}",
            )

    def save_config(self, file_path: str | Path) -> None:
        """Saves the current configuration state to a YAML file.

        This is useful for exporting the fully merged and validated config.

        Args:
            file_path (str | Path): The path where the YAML config will be saved.
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        config_dict = self.config.model_dump(mode="json")
        OmegaConf.save(config=config_dict, f=path)

    def _get_default_config_path(self) -> Path:
        """Reliably finds the path to the bundled 'conf' directory.

        Returns:
            Path: The absolute path to the default configuration directory.

        Raises:
            FileNotFoundError: If the default 'conf' directory cannot be found.
        """
        try:
            files = resources.files("culicidaelab")
            # Check for Traversable with _path (for installed packages)
            if hasattr(files, "_path"):
                return Path(files._path) / "conf"
            # Otherwise, use string representation (for zip files, etc.)
            else:
                return Path(str(files)) / "conf"
        except (ModuleNotFoundError, FileNotFoundError):
            # Fallback for development mode
            dev_path = Path(__file__).parent.parent / "conf"
            if dev_path.exists():
                return dev_path
            raise FileNotFoundError(
                "Could not find the default 'conf' directory. "
                "Ensure the 'culicidaelab' package is installed correctly or "
                "you are in the project root.",
            )

    def _load(self) -> CulicidaeLabConfig:
        """Executes the full load, merge, and validation process.

        Returns:
            CulicidaeLabConfig: The validated configuration object.

        Raises:
            ValidationError: If the merged configuration fails Pydantic validation.
        """
        default_config_dict = self._load_config_from_dir(
            cast(Path, self.default_config_path),
        )
        user_config_dict = self._load_config_from_dir(self.user_config_dir)

        # User configs override defaults
        merged_config = _deep_merge(user_config_dict, default_config_dict)

        try:
            validated_config = CulicidaeLabConfig(**merged_config)
            return validated_config
        except ValidationError as e:
            print(
                "FATAL: Configuration validation failed. Please check your " "YAML files or environment variables.",
            )
            print(e)
            raise

    def _load_config_from_dir(self, config_dir: Path | None) -> ConfigDict:
        """Loads all YAML files from a directory into a nested dictionary.

        The dictionary structure mirrors the directory structure.

        Args:
            config_dir (Path | None): Directory containing YAML config files, or None.

        Returns:
            ConfigDict: A nested dictionary containing the loaded configuration.
        """
        config_dict: ConfigDict = {}
        if config_dir is None or not config_dir.is_dir():
            return config_dict

        for yaml_file in config_dir.glob("**/*.yaml"):
            try:
                with yaml_file.open("r") as f:
                    data = yaml.safe_load(f)
                    if data is None:
                        continue

                relative_path = yaml_file.relative_to(config_dir)
                keys = list(relative_path.parts[:-1]) + [relative_path.stem]

                d = config_dict
                for key in keys[:-1]:
                    d = d.setdefault(key, {})
                d[keys[-1]] = data
            except Exception as e:
                print(f"Warning: Could not load or parse {yaml_file}: {e}")
        return config_dict
