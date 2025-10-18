"""
Module to get translation from locales.

Author: Uriel Curiel <urielcurrel@outlook.com>
"""

import json
import logging
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import cast

from i18n_modern.helpers import eval_key, format_value, get_deep_value, merge_deep
from i18n_modern.types import FormatParam, LocaleDict, Locales, LocaleValue

yaml_available = False
try:
    import yaml

    yaml_available = True
except ImportError:
    yaml = None

toml_available = False
try:
    import tomli

    toml_available = True
except ImportError:
    tomli = None


class I18nModern:
    """
    Gets the translation from a locales variable.

    Args:
        default_locale: The default locale
        locales: The locales variable (dict) or path to locale file
    """

    def __init__(self, default_locale: str, locales: LocaleDict | str | None = None):
        self._locales: Locales = {}
        self._default_locale: str = default_locale
        # Increased cache size for better performance (was unbounded)
        self._previous_translations: dict[tuple[object, ...], str] = {}
        self._cache_max_size: int = 2048  # Limit cache size to prevent unbounded growth

        if locales:
            if isinstance(locales, str):
                self.load_from_file(locales, default_locale)
            else:
                self.load_from_value(locales, default_locale)

    @property
    def default_locale(self) -> str:
        """Get the default locale."""
        return self._default_locale

    @default_locale.setter
    def default_locale(self, value: str):
        """Set the default locale."""
        self._default_locale = value

    def load_from_file(self, file_path: str, locale_identify: str):
        """
        Load locales from a file (JSON, YAML, or TOML).

        Args:
            file_path: Path to the locale file
            locale_identify: Locale identifier
        """
        path: Path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Locale file not found: {file_path}")

        suffix: str = path.suffix.lower()

        if suffix == ".json":
            # Try memory-mapped style reading for very large files
            try:
                import mmap

                with open(path, "rb") as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        data = cast(LocaleDict, json.loads(mm.read().decode("utf-8")))
            except Exception:
                with open(path, "r", encoding="utf-8") as f:
                    data = cast(LocaleDict, json.load(f))
        elif suffix in [".yaml", ".yml"]:
            if not yaml_available or yaml is None:
                raise ImportError("PyYAML is required for YAML support. Install with: pip install pyyaml")
            with open(path, "r", encoding="utf-8") as f:
                data = cast(LocaleDict, yaml.safe_load(f))  # type: ignore
        elif suffix == ".toml":
            if not toml_available or tomli is None:
                raise ImportError("tomli is required for TOML support. Install with: pip install tomli")
            with open(path, "rb") as f:
                data = cast(LocaleDict, tomli.load(f))  # type: ignore
        else:
            raise ValueError(f"Unsupported file format: {suffix}. Supported formats: .json, .yaml, .yml, .toml")

        self._locales[locale_identify] = merge_deep(self._locales.get(self._default_locale), data)

    def _load_path(self, path: Path) -> LocaleDict:
        """Load a single locale file from a path with mmap optimization for JSON."""
        suffix = path.suffix.lower()
        if suffix == ".json":
            try:
                import mmap

                with open(path, "rb") as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        return cast(LocaleDict, json.loads(mm.read().decode("utf-8")))
            except Exception:
                with open(path, "r", encoding="utf-8") as f:
                    return cast(LocaleDict, json.load(f))
        if suffix in [".yaml", ".yml"]:
            if not yaml_available or yaml is None:
                raise ImportError("PyYAML is required for YAML support. Install with: pip install pyyaml")
            with open(path, "r", encoding="utf-8") as f:
                return cast(LocaleDict, yaml.safe_load(f))  # type: ignore
        if suffix == ".toml":
            if not toml_available or tomli is None:
                raise ImportError("tomli is required for TOML support. Install with: pip install tomli")
            with open(path, "rb") as f:
                return cast(LocaleDict, tomli.load(f))  # type: ignore
        raise ValueError(f"Unsupported file format: {suffix}. Supported formats: .json, .yaml, .yml, .toml")

    def load_from_directory(self, directory_path: str, locale_identify: str | None = None) -> None:
        """
        Load all locale files from a directory concurrently.

        Files are merged together and stored under the specified locale.
        Supports JSON, YAML (yml/yaml), and TOML formats.

        Args:
            directory_path: Path to the directory containing locale files
            locale_identify: Locale identifier. If None, uses the directory name

        Raises:
            FileNotFoundError: If directory does not exist
            ValueError: If directory contains no supported locale files
        """
        path = Path(directory_path)

        if not path.exists():
            raise FileNotFoundError(f"Locale directory not found: {directory_path}")

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")

        # Use directory name as locale if not specified
        if locale_identify is None:
            locale_identify = path.name

        # Find all supported locale files
        supported_extensions = {".json", ".yaml", ".yml", ".toml"}
        locale_files = [f for f in path.iterdir() if f.is_file() and f.suffix.lower() in supported_extensions]

        if not locale_files:
            raise ValueError(
                f"No supported locale files found in directory: {directory_path}. "
                f"Supported formats: {', '.join(supported_extensions)}"
            )

        # Load all files concurrently
        results: list[tuple[str, LocaleDict]] = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._task_load_locale, str(f), locale_identify) for f in locale_files]
            for fut in as_completed(futures):
                results.append(fut.result())

        # Merge all loaded data into a single locale entry
        merged_data: LocaleDict = {}
        for _, data in results:
            merged_data = merge_deep(merged_data, data)

        self._locales[locale_identify] = merge_deep(self._locales.get(self._default_locale), merged_data)

    def _task_load_locale(self, file_path: str, locale: str) -> tuple[str, LocaleDict]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Locale file not found: {file_path}")
        return locale, self._load_path(path)

    def load_many(self, files: Iterable[tuple[str, str]], max_workers: int | None = None) -> None:
        """Load multiple locale files concurrently.

        Args:
            files: Iterable of tuples (file_path, locale_identify)
            max_workers: Optional maximum number of worker threads
        """

        # Load in parallel and merge safely once complete
        results: list[tuple[str, LocaleDict]] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._task_load_locale, fp, loc) for fp, loc in files]
            for fut in as_completed(futures):
                results.append(fut.result())

        # Merge results into _locales
        for locale, data in results:
            self._locales[locale] = merge_deep(self._locales.get(self._default_locale), data)

    def load_from_value(self, locales: LocaleDict, locale_identify: str):
        """
        Load locales from a dictionary value.

        Args:
            locales: The locales dictionary
            locale_identify: Locale identifier
        """
        self._locales[locale_identify] = merge_deep(self._locales.get(self._default_locale), locales)

    def get(self, key: str, locale: str | None = None, values: FormatParam | None = None) -> str:
        """
        Get a translation with memoization from a key and format params.

        Args:
            key: Translation key (supports dot notation)
            locale: Optional locale override
            values: Optional values for placeholder replacement

        Returns:
            Translated string
        """
        try:
            locale = locale or self._default_locale
            values_tuple = tuple(sorted(values.items())) if values else None
            cache_key = (key, locale, values_tuple)

            if cache_key in self._previous_translations:
                return self._previous_translations[cache_key]

            if locale not in self._locales:
                raise KeyError(f"Locale '{locale}' not found in locales")

            translation: LocaleValue | None = get_deep_value(self._locales[locale], key)

            if translation is None:
                raise KeyError(f"Translation key '{key}' not found in locale '{locale}'")

            result = self._get_translation(translation, values)

            # Bounded cache - prevent unbounded growth
            if len(self._previous_translations) >= self._cache_max_size:
                # Simple FIFO eviction: remove oldest items (first half)
                keys_to_remove = list(self._previous_translations.keys())[: self._cache_max_size // 4]
                for k in keys_to_remove:
                    del self._previous_translations[k]

            self._previous_translations[cache_key] = result
            return result

        except Exception as error:
            logging.warning("Error: the key '%s' is not defined in locales - %s", key, error)
            return key

    def _get_translation(
        self, translation: LocaleValue, values: FormatParam | None = None, default_translation: str | None = None
    ) -> str:
        """
        Get a translation from object and format it.

        Args:
            translation: Translation value (string or dict)
            values: Optional values for placeholder replacement
            default_translation: Optional default translation

        Returns:
            Formatted translation string
        """
        if isinstance(translation, dict) and "default" in translation:
            default_translation = str(translation["default"])

        if not isinstance(translation, str):
            # Find matching key based on condition
            for key in translation.keys():  # type: ignore
                if eval_key(key, values):  # type: ignore
                    return self._get_translation(
                        translation[key],
                        values,
                        default_translation,  # type: ignore
                    )

            # Return default if no key matches
            if default_translation:
                return self._get_translation(default_translation, values, default_translation)  # type: ignore
            return ""

        return format_value(translation, values)
