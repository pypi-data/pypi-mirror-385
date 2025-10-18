# Python i18n Modern - Project Summary

## Overview
Python i18n Modern is a modern internationalization (i18n) library for Python, inspired by the JavaScript version at https://github.com/UrielCuriel/i18n_modern.

## Key Features Implemented

### Core Functionality
- ✅ Translation management with nested keys (dot notation)
- ✅ Template string interpolation with `[placeholder]` syntax
- ✅ Conditional translations based on values
- ✅ Comparison operators (`<`, `>`, `>=`, `<=`, `==`, `!=`)
- ✅ Logical operators (`&&` converted to `and`, `||` to `or`)
- ✅ Built-in memoization for performance
- ✅ Deep object merging for locale inheritance
- ✅ Multiple locale support with runtime switching

### File Format Support
- ✅ JSON (built-in, no dependencies)
- ✅ YAML (optional: `pip install pyyaml`)
- ✅ TOML (optional: `pip install tomli` for Python < 3.11)

### Differences from JavaScript Version
1. **Local files only** - Removed URL loading (web loader) for security and simplicity
2. **Added TOML support** - In addition to JSON and YAML
3. **Python idioms** - Used Python conventions (`snake_case`, type hints, etc.)
4. **Logical operators** - Automatically converts `&&` to `and` and `||` to `or`

## Project Structure

```
python_i18n_modern/
├── i18n_modern/              # Main package
│   ├── __init__.py          # Package initialization
│   ├── i18n.py              # Core I18nModern class
│   ├── helpers.py           # Helper functions
│   └── types.py             # Type definitions
├── examples/                 # Usage examples
│   ├── example.py           # Comprehensive examples
│   └── locales/             # Example locale files
│       ├── en.json
│       ├── es.yaml
│       └── fr.toml
├── tests/                    # Test suite
│   └── test_i18n.py
├── main.py                   # Quick demo script
├── pyproject.toml           # Project metadata & dependencies
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick start guide
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
└── MANIFEST.in              # Package manifest
```

## API Reference

### I18nModern Class

```python
class I18nModern:
    def __init__(self, default_locale: str, locales: Optional[Union[Locales, str]] = None)
    def get(self, key: str, locale: Optional[str] = None, values: Optional[FormatParam] = None) -> str
    def load_from_file(self, file_path: str, locale_identify: str)
    def load_from_value(self, locales: Locales, locale_identify: str)
    
    @property
    def default_locale(self) -> str
    
    @default_locale.setter
    def default_locale(self, value: str)
```

## Usage Examples

### Basic
```python
from i18n_modern import I18nModern

i18n = I18nModern("en", {"greeting": "Hello, [name]!"})
print(i18n.get("greeting", values={"name": "World"}))  # Hello, World!
```

### Conditional
```python
locales = {
    "items": {
        "0": "No items",
        "1": "One item",
        "default": "[count] items"
    }
}
i18n = I18nModern("en", locales)
print(i18n.get("items", values={"count": 5}))  # 5 items
```

### Multiple Locales
```python
i18n = I18nModern("en")
i18n.load_from_file("locales/en.json", "en")
i18n.load_from_file("locales/es.yaml", "es")
print(i18n.get("greeting", locale="es", values={"name": "Mundo"}))
```

## Testing

All features are tested in `tests/test_i18n.py`:
- ✅ Basic translation
- ✅ Nested keys
- ✅ Conditional translations
- ✅ Comparison conditions
- ✅ Memoization
- ✅ Load from value
- ✅ Default locale property

Run tests: `python tests/test_i18n.py`

## Dependencies

### Required
- Python >= 3.8
- No required dependencies for basic JSON support

### Optional
- `pyyaml >= 6.0` - For YAML file support
- `tomli >= 2.0.0` - For TOML support (Python < 3.11 only)

## Installation

```bash
# Basic (JSON only)
pip install i18n_modern

# With all formats
pip install i18n_modern[all]
```

## Quick Start

1. Run the demo: `python main.py`
2. Run examples: `python examples/example.py`
3. Run tests: `python tests/test_i18n.py`
4. Read: `README.md` or `QUICKSTART.md`

## Development Status

✅ Core functionality complete and tested
✅ JSON, YAML, TOML support working
✅ Examples and documentation complete
✅ Ready for use in projects

## Future Enhancements (Optional)

- Add plural forms support (like gettext)
- Add interpolation function support
- Add locale fallback chains
- Add async file loading
- Add locale validation utilities
- Package and publish to PyPI

## License

MIT License - See LICENSE file

## Author

Uriel Curiel <urielcurrel@outlook.com>

Inspired by: https://github.com/UrielCuriel/i18n_modern
