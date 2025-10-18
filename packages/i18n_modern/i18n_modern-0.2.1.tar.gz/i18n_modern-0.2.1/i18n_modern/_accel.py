"""Optional acceleration layer for hot paths.

This module tries to import a Cython-compiled extension to speed up
selected operations. If not available, it falls back to pure-Python
implementations from :mod:`i18n_modern.helpers`.
"""

from __future__ import annotations

import importlib
from collections.abc import Mapping
from typing import Protocol, cast

_has_accel: bool = False
_mod = None


def _try_import() -> None:
    global _has_accel, _mod
    if _has_accel:
        return
    try:  # pragma: no cover - optional fast path
        _mod = importlib.import_module("i18n_modern._cy_helpers")
        _has_accel = True
        return
    except Exception:
        _has_accel = False


class _CyGetDeep(Protocol):
    def __call__(self, obj: Mapping[str, object], path: str) -> object: ...  # pragma: no cover - typing only


class _CyFormatValue(Protocol):
    def __call__(self, string: str, values: Mapping[str, object]) -> str: ...  # pragma: no cover - typing only


def get_deep_value_fast(obj: Mapping[str, object] | None, path: str) -> tuple[bool, object | None]:
    """Fast path for deep dict traversal if available.

    Falls back to returning a sentinel indicating no fast path.
    """

    _try_import()
    if _has_accel and obj is not None and _mod is not None:  # pragma: no cover - exercised in benches
        try:
            func = cast(_CyGetDeep, getattr(_mod, "cy_get_deep_value"))
            return True, func(obj, path)
        except Exception:
            return False, None
    return False, None


def format_value_fast(string: str, values: Mapping[str, object] | None) -> tuple[bool, str]:
    """Fast path for placeholder substitution if available.

    Returns None when the fast path isn't available.
    """

    _try_import()
    if _has_accel and values and _mod is not None:  # pragma: no cover - exercised in benches
        try:
            func = cast(_CyFormatValue, getattr(_mod, "cy_format_value"))
            return True, func(string, values)
        except Exception:
            return False, string
    return False, string


__all__ = ["get_deep_value_fast", "format_value_fast"]
