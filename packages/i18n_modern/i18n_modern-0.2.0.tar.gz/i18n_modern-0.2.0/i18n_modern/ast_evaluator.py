"""AST-based expression evaluator for conditional translation keys.

This module provides safe evaluation of boolean expressions using Python's AST,
supporting numeric and string comparisons with Python's native operators.
"""

from __future__ import annotations

import ast
import functools
from typing import Callable

from .types import FormatValue

# Mapping of AST comparison operators to their implementations
_STRING_COMPARATORS: dict[type[ast.cmpop], Callable[[str, str], bool]] = {
    ast.Gt: lambda a, b: a > b,
    ast.GtE: lambda a, b: a >= b,
    ast.Lt: lambda a, b: a < b,
    ast.LtE: lambda a, b: a <= b,
    ast.Eq: lambda a, b: a == b,
    ast.NotEq: lambda a, b: a != b,
}

_NUMERIC_COMPARATORS: dict[type[ast.cmpop], Callable[[float, float], bool]] = {
    ast.Gt: lambda a, b: a > b,
    ast.GtE: lambda a, b: a >= b,
    ast.Lt: lambda a, b: a < b,
    ast.LtE: lambda a, b: a <= b,
    ast.Eq: lambda a, b: a == b,
    ast.NotEq: lambda a, b: a != b,
}


class ASTExpressionEvaluator:
    """Evaluator for safe boolean expressions using Python AST."""

    @staticmethod
    @functools.lru_cache(maxsize=512)
    def parse(expression: str) -> ast.Expression | None:
        """Parse and cache the AST for a boolean expression.

        Args:
            expression: String expression to parse

        Returns:
            Parsed AST Expression or None if invalid syntax
        """
        try:
            node = ast.parse(expression, mode="eval")
            assert isinstance(node, ast.Expression)
            return node
        except (SyntaxError, AssertionError):
            return None

    @classmethod
    def evaluate(cls, expression: str) -> bool:
        """Safely evaluate a boolean expression.

        Args:
            expression: Boolean expression string

        Returns:
            Boolean result of evaluation
        """
        tree = cls.parse(expression)
        if tree is None:
            return False

        try:
            return cls._evaluate_node(tree.body)
        except (ValueError, TypeError):
            return False

    @classmethod
    def _evaluate_node(cls, node: ast.expr) -> bool:
        """Evaluate a parsed AST node representing a conditional expression.

        Args:
            node: AST expression node

        Returns:
            Boolean result

        Raises:
            ValueError: If node type is unsupported
        """
        if isinstance(node, ast.BoolOp):
            return cls._evaluate_bool_op(node)

        if isinstance(node, ast.Compare):
            return cls._evaluate_compare(node)

        if isinstance(node, ast.Constant) and isinstance(node.value, bool):
            return node.value

        raise ValueError(f"Unsupported node type: {type(node)}")

    @classmethod
    def _evaluate_bool_op(cls, node: ast.BoolOp) -> bool:
        """Evaluate boolean operations (and/or).

        Args:
            node: BoolOp AST node

        Returns:
            Boolean result
        """
        results = [cls._evaluate_node(value) for value in node.values]

        if isinstance(node.op, ast.And):
            return all(results)
        if isinstance(node.op, ast.Or):
            return any(results)

        raise ValueError(f"Unsupported boolean operator: {type(node.op)}")

    @classmethod
    def _evaluate_compare(cls, node: ast.Compare) -> bool:
        """Evaluate comparison operations.

        Args:
            node: Compare AST node

        Returns:
            Boolean result of comparison chain
        """
        left = cls._evaluate_operand(node.left)

        for operator, comparator in zip(node.ops, node.comparators):
            right = cls._evaluate_operand(comparator)
            if not cls._apply_comparison(operator, left, right):
                return False
            left = right

        return True

    @staticmethod
    def _evaluate_operand(node: ast.expr) -> FormatValue:
        """Evaluate an operand within a conditional expression.

        Args:
            node: AST expression node

        Returns:
            Evaluated value (bool, int, float, or str)

        Raises:
            ValueError: If operand type is unsupported
        """
        # Handle constants (literals)
        if isinstance(node, ast.Constant) and isinstance(node.value, (bool, int, float, str)):
            return node.value

        # Handle unary operations (+/-)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            operand = ASTExpressionEvaluator._evaluate_operand(node.operand)
            if isinstance(operand, (int, float)):
                return operand if isinstance(node.op, ast.UAdd) else -operand
            raise ValueError(f"Invalid unary operation on {type(operand)}")

        raise ValueError(f"Unsupported operand type: {type(node)}")

    @staticmethod
    def _apply_comparison(operator: ast.cmpop, left: FormatValue, right: FormatValue) -> bool:
        """Apply a comparison operator between two values.

        Args:
            operator: AST comparison operator
            left: Left operand
            right: Right operand

        Returns:
            Boolean result of comparison

        Raises:
            ValueError: If comparison is invalid
        """
        # Equality/inequality work on any types
        if isinstance(operator, ast.Eq):
            return left == right
        if isinstance(operator, ast.NotEq):
            return left != right

        # Ordering comparisons
        if isinstance(operator, (ast.Gt, ast.GtE, ast.Lt, ast.LtE)):
            return ASTExpressionEvaluator._compare_ordered(operator, left, right)

        raise ValueError(f"Unsupported comparison operator: {type(operator)}")

    @staticmethod
    def _compare_ordered(operator: ast.cmpop, left: FormatValue, right: FormatValue) -> bool:
        """Compare two values using an ordering operator.

        Args:
            operator: AST comparison operator
            left: Left operand
            right: Right operand

        Returns:
            Boolean result

        Raises:
            ValueError: If types are incompatible for ordering
        """
        op_type = type(operator)

        # String comparison
        if isinstance(left, str) and isinstance(right, str):
            comparator = _STRING_COMPARATORS.get(op_type)
            if comparator:
                return comparator(left, right)

        # Numeric comparison
        if isinstance(left, (int, float, bool)) and isinstance(right, (int, float, bool)):
            comparator = _NUMERIC_COMPARATORS.get(op_type)
            if comparator:
                return comparator(float(left), float(right))

        raise ValueError(f"Cannot compare {type(left)} with {type(right)}")
