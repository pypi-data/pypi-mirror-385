#!/usr/bin/env python3
"""Profiling script for i18n_modern performance evaluation."""

import cProfile
import pstats
from typing import cast

from i18n_modern import I18nModern
from i18n_modern.types import LocaleDict


def benchmark_translations():
    """Benchmark translation operations."""
    # Sample locales with conditional translations
    locales = {
        "welcome": "Welcome, [name]!",
        "items": {"0": "No items", "1": "One item", "default": "[count] items"},
        "age_group": {"[age] < 18": "Minor", "[age] >= 18": "Adult", "default": "Unknown"},
        "notifications": {
            "[count] == 0": "No notifications",
            "[count] > 10": "Many notifications",
            "default": "[count] notifications",
        },
    }

    i18n = I18nModern("en", cast(LocaleDict, locales))

    # Perform many translation operations
    operations = 10000

    for i in range(operations):
        # Basic translation
        _ = i18n.get("welcome", values={"name": "User"})

        # Conditional translations
        _ = i18n.get("items", values={"count": i % 100})
        _ = i18n.get("age_group", values={"age": i % 50})
        _ = i18n.get("notifications", values={"count": i % 20})


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    benchmark_translations()

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumulative")
    _ = stats.print_stats(20)  # Top 20 functions
