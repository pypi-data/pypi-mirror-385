"""Simple demo of i18n_modern library."""

from i18n_modern import I18nModern


def main():
    """Run a simple demo of the library."""
    print("Python i18n Modern - Quick Demo\n")

    # Create a simple locales dictionary
    locales = {
        "welcome": "Welcome to Python i18n Modern!",
        "greeting": "Hello, [name]!",
        "farewell": "Goodbye, [name]!",
        "items": {"0": "You have no items", "1": "You have one item", "default": "You have [count] items"},
    }

    # Initialize i18n with English locale
    i18n = I18nModern("en", locales)

    # Basic translation
    print(i18n.get("welcome"))
    print(i18n.get("greeting", values={"name": "Developer"}))
    print(i18n.get("farewell", values={"name": "Developer"}))

    print()

    # Conditional translation
    print("Item counts:")
    for count in [0, 1, 5]:
        print(f"  {i18n.get('items', values={'count': count})}")

    print("\n✓ Demo complete! Check the README.md for more examples.")


if __name__ == "__main__":
    main()
