#!/usr/bin/env python3
"""Example usage of i18n_modern library."""

import sys
from pathlib import Path

# Add parent directory to path to import i18n_modern
sys.path.insert(0, str(Path(__file__).parent.parent))

from i18n_modern import I18nModern


def example_basic():
    """Basic translation example."""
    print("=== Basic Translation ===")
    
    locales = {
        "welcome": "Welcome to our app!",
        "greeting": "Hello, [name]!",
    }
    
    i18n = I18nModern("en", locales)
    print(i18n.get("welcome"))
    print(i18n.get("greeting", values={"name": "World"}))
    print()


def example_nested():
    """Nested keys example."""
    print("=== Nested Keys ===")
    
    locales = {
        "messages": {
            "success": "Operation successful",
            "error": "An error occurred"
        }
    }
    
    i18n = I18nModern("en", locales)
    print(i18n.get("messages.success"))
    print(i18n.get("messages.error"))
    print()


def example_conditional():
    """Conditional translations example."""
    print("=== Conditional Translations ===")
    
    locales = {
        "items": {
            "0": "No items",
            "1": "One item",
            "default": "[count] items"
        },
        "age_group": {
            "[age] < 13": "Child",
            "[age] >= 13 && [age] < 18": "Teenager",
            "[age] >= 18": "Adult",
            "default": "Unknown"
        }
    }
    
    i18n = I18nModern("en", locales)
    
    # Items count
    for count in [0, 1, 5, 10]:
        print(f"Count {count}: {i18n.get('items', values={'count': count})}")
    
    print()
    
    # Age groups
    for age in [10, 15, 25]:
        print(f"Age {age}: {i18n.get('age_group', values={'age': age})}")
    
    print()


def example_file_loading():
    """File loading example."""
    print("=== File Loading ===")
    
    # JSON
    try:
        i18n_en = I18nModern("en", "examples/locales/en.json")
        print(f"EN (JSON): {i18n_en.get('welcome')}")
        print(f"EN (JSON): {i18n_en.get('greeting', values={'name': 'Alice'})}")
    except FileNotFoundError:
        print("English locale file not found")
    
    # YAML
    try:
        i18n_es = I18nModern("es", "examples/locales/es.yaml")
        print(f"ES (YAML): {i18n_es.get('welcome')}")
        print(f"ES (YAML): {i18n_es.get('greeting', values={'name': 'Juan'})}")
    except (FileNotFoundError, ImportError) as e:
        print(f"Spanish locale error: {e}")
    
    # TOML
    try:
        i18n_fr = I18nModern("fr", "examples/locales/fr.toml")
        print(f"FR (TOML): {i18n_fr.get('welcome')}")
        print(f"FR (TOML): {i18n_fr.get('greeting', values={'name': 'Marie'})}")
    except (FileNotFoundError, ImportError) as e:
        print(f"French locale error: {e}")
    
    print()


def example_multiple_locales():
    """Multiple locales example."""
    print("=== Multiple Locales ===")
    
    i18n = I18nModern("en")
    
    try:
        i18n.load_from_file("examples/locales/en.json", "en")
        i18n.load_from_file("examples/locales/es.yaml", "es")
        
        # English
        print(f"EN: {i18n.get('greeting', values={'name': 'World'})}")
        
        # Spanish
        print(f"ES: {i18n.get('greeting', locale='es', values={'name': 'Mundo'})}")
        
        # Change default locale
        i18n.default_locale = "es"
        print(f"ES (default): {i18n.get('welcome')}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def main():
    """Run all examples."""
    print("Python i18n Modern - Examples\n")
    
    example_basic()
    example_nested()
    example_conditional()
    example_file_loading()
    example_multiple_locales()
    
    print("Done!")


if __name__ == "__main__":
    main()
