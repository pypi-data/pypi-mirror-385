"""Helper functions for i18n_modern.

Optimizations added:
- Visitor object pooling for deep traversal
- Optional fast paths via Cython (see :mod:`i18n_modern._accel`)
- Modular AST-based conditional evaluation
- Separate value substitution system
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from typing import cast

from ._accel import format_value_fast, get_deep_value_fast
from .conditional_evaluator import ConditionalKeyEvaluator
from .types import FormatParam, LocaleDict, LocaleValue
from .value_substitution import ValueSubstitutor


class TreePathVisitor:
    """Visitor for traversing nested mapping structures using path segments."""

    segments: list[str]
    segment_index: int

    def __init__(self, segments: list[str]) -> None:
        """
        Initialize visitor with path segments.

        Args:
            segments: Path segments to traverse (e.g., ["user", "profile", "name"])
        """
        self.segments = segments
        self.segment_index = 0

    def reset(self, segments: list[str]) -> None:
        """Reset the visitor to reuse the same instance from a pool."""
        self.segments = segments
        self.segment_index = 0

    def visit(self, node: LocaleValue | None) -> LocaleValue | None:
        """
        Visit a node in the tree structure.

        Args:
            node: Current node to visit

        Returns:
            The value at the path or None if not found
        """
        if self.segment_index >= len(self.segments) or node is None:
            return node if self.segment_index >= len(self.segments) else None

        if not isinstance(node, Mapping):
            return None

        current_key = self.segments[self.segment_index]
        next_node = node.get(current_key)

        if next_node is None:
            return None

        self.segment_index += 1
        return self.visit(next_node)


class _TreePathVisitorPool:
    """Optimized pool for TreePathVisitor instances with pre-allocated instances.

    This pool is intentionally simple (LIFO) and not thread-safe. Each thread
    using get_deep_value should maintain its own instances through the GIL.
    """

    def __init__(self, maxsize: int = 128, prealloc: int = 32) -> None:
        self._pool: deque[TreePathVisitor] = deque()
        self._max: int = maxsize
        # Pre-allocate a set of visitors
        for _ in range(prealloc):
            self._pool.append(TreePathVisitor([]))

    def acquire(self, segments: list[str]) -> TreePathVisitor:
        try:
            visitor = self._pool.pop()
            visitor.reset(segments)
            return visitor
        except IndexError:
            return TreePathVisitor(segments)

    def release(self, visitor: TreePathVisitor) -> None:
        # Avoid holding onto large segment lists
        visitor.reset([])
        if len(self._pool) < self._max:
            self._pool.append(visitor)


_VISITOR_POOL = _TreePathVisitorPool()


def get_deep_value(obj: LocaleValue | None, path: str) -> LocaleValue | None:
    """
    Get value from deep object using dot notation.

    Args:
        obj: Object to get value from
        path: Path to object (e.g., "user.profile.name")

    Returns:
        The value at the specified path or None
    """
    if not path:
        return None

    # Try accelerated path first (no-op if not available)
    if isinstance(obj, Mapping):
        ok, result = get_deep_value_fast(cast(Mapping[str, object] | None, obj), path)
        if ok:
            return cast(LocaleValue | None, result)

    segments: list[str] = path.split(".")
    visitor = _VISITOR_POOL.acquire(segments)
    try:
        return visitor.visit(obj)
    finally:
        _VISITOR_POOL.release(visitor)


def _get_from_segments(current: LocaleValue | None, segments: list[str]) -> LocaleValue | None:
    """Recursive helper to walk nested mappings using the provided path segments."""

    if not segments:
        return current

    if not isinstance(current, Mapping):
        return None

    next_value: object | None = current.get(segments[0])
    if next_value is None:
        return None

    return _get_from_segments(next_value, segments[1:])


def eval_key(key: str, values: FormatParam | None = None) -> bool:
    """
    Evaluate a key object string against values.

    Args:
        key: Key to evaluate
        values: Object to eval key against

    Returns:
        Boolean result of evaluation
    """
    return ConditionalKeyEvaluator.evaluate(key, values)


def format_value(string: str, values: FormatParam | None = None) -> str:
    """
    Replace [value] in string with actual values.

    Args:
        string: String with placeholders like [key]
        values: Dictionary with replacement values

    Returns:
        Formatted string
    """
    if values is None or not values:
        return string

    # Accelerated fast path if available
    ok, s = format_value_fast(string, values)
    if ok:
        return s

    return ValueSubstitutor.substitute(string, values)


def is_safe_string(string: str) -> bool:
    """
    Validate that the string does not include Python reserved words.

    Args:
        string: String to validate

    Returns:
        True if string is safe to evaluate
    """
    return ConditionalKeyEvaluator.is_safe_expression(string)


def merge_deep(obj1: Mapping[str, LocaleValue] | None, obj2: Mapping[str, LocaleValue]) -> LocaleDict:
    """
    Merge deep objects recursively.

    Args:
        obj1: First object to merge
        obj2: Second object to merge

    Returns:
        Merged object
    """
    merged: LocaleDict = {}

    if obj1:
        merged.update(obj1)

    for key, value in obj2.items():
        existing = merged.get(key)

        if isinstance(value, Mapping):
            value_mapping = cast(Mapping[str, LocaleValue], value)
            existing_mapping = (
                cast(Mapping[str, LocaleValue] | None, existing) if isinstance(existing, Mapping) else None
            )
            merged[key] = merge_deep(existing_mapping, value_mapping)
        else:
            merged[key] = value

    return merged


class DictMergeVisitor:
    """Visitor pattern for merging nested dictionaries efficiently."""

    merged: LocaleDict

    def __init__(self) -> None:
        """Initialize the merge visitor."""
        self.merged = {}

    def visit(self, obj1: Mapping[str, LocaleValue] | None, obj2: Mapping[str, LocaleValue]) -> LocaleDict:
        """
        Visit and merge two dictionaries.

        Args:
            obj1: First dictionary to merge
            obj2: Second dictionary to merge

        Returns:
            Merged dictionary
        """
        if obj1:
            self.merged.update(obj1)

        for key, value in obj2.items():
            existing = self.merged.get(key)
            self.merged[key] = self._merge_value(existing, value)

        return self.merged

    def _merge_value(self, existing: LocaleValue | None, new_value: LocaleValue) -> LocaleValue:
        """
        Merge a single value, recursing for nested dictionaries.

        Args:
            existing: Existing value
            new_value: New value to merge

        Returns:
            Merged value
        """
        if isinstance(new_value, Mapping):
            value_mapping = cast(Mapping[str, LocaleValue], new_value)
            existing_mapping = cast(Mapping[str, LocaleValue], existing) if isinstance(existing, Mapping) else None
            visitor = DictMergeVisitor()
            return visitor.visit(existing_mapping, value_mapping)

        return new_value
