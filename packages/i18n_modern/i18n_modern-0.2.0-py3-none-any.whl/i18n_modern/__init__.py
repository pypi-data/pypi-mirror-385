"""
Python i18n Modern - A modern internationalization library for Python.

Inspired by i18n_modern for JavaScript.
"""

from ._accel import format_value_fast, get_deep_value_fast
from .ast_evaluator import ASTExpressionEvaluator
from .conditional_evaluator import ConditionalKeyEvaluator
from .i18n import I18nModern
from .types import FormatParam, Locales
from .value_substitution import ValueSubstitutor

__version__ = "0.3.0"
__all__ = [
    "I18nModern",
    "Locales",
    "FormatParam",
    # Optional fast-path helpers (no-op if Cython ext unavailable)
    "get_deep_value_fast",
    "format_value_fast",
    # AST-based evaluation components
    "ASTExpressionEvaluator",
    "ConditionalKeyEvaluator",
    "ValueSubstitutor",
]
