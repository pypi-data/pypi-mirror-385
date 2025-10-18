"""Type definitions for :mod:`i18n_modern`."""

from typing import TypeAlias

LocaleValue: TypeAlias = "str | LocaleDict"
LocaleDict: TypeAlias = dict[str, LocaleValue]
Locales: TypeAlias = dict[str, LocaleDict]

FormatValue: TypeAlias = bool | float | int | str
FormatParam: TypeAlias = dict[str, FormatValue]

__all__ = [
    "FormatParam",
    "FormatValue",
    "LocaleDict",
    "LocaleValue",
    "Locales",
]
