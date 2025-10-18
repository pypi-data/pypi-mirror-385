# Quick Start Guide

## Installation

### Basic (JSON support only)
```bash
pip install i18n_modern
```

### With all format support
```bash
pip install i18n_modern[all]
```

## 5-Minute Tutorial

### 1. Basic Usage

```python
from i18n_modern import I18nModern

# Define your translations
locales = {
    "greeting": "Hello, [name]!",
    "welcome": "Welcome to the app"
}

# Initialize
i18n = I18nModern("en", locales)

# Get translations
print(i18n.get("welcome"))  # Welcome to the app
print(i18n.get("greeting", values={"name": "Alice"}))  # Hello, Alice!
```

### 2. Nested Translations

```python
locales = {
    "user": {
        "profile": {
            "title": "User Profile"
        }
    }
}

i18n = I18nModern("en", locales)
print(i18n.get("user.profile.title"))  # User Profile
```

### 3. Conditional Translations

```python
locales = {
    "items": {
        "0": "No items",
        "1": "One item",
        "default": "[count] items"
    }
}

i18n = I18nModern("en", locales)
print(i18n.get("items", values={"count": 0}))  # No items
print(i18n.get("items", values={"count": 5}))  # 5 items
```

### 4. Loading from Files

**en.json:**
```json
{
    "greeting": "Hello, [name]!",
    "farewell": "Goodbye!"
}
```

**Python:**
```python
i18n = I18nModern("en", "locales/en.json")
print(i18n.get("greeting", values={"name": "World"}))
```

### 5. Multiple Locales

```python
i18n = I18nModern("en")
i18n.load_from_file("locales/en.json", "en")
i18n.load_from_file("locales/es.json", "es")

# English
print(i18n.get("greeting", values={"name": "World"}))

# Spanish
print(i18n.get("greeting", locale="es", values={"name": "Mundo"}))

# Change default
i18n.default_locale = "es"
```

## Supported File Formats

- **JSON** (built-in)
- **YAML** (install with `pip install pyyaml`)
- **TOML** (install with `pip install tomli` for Python < 3.11)

## Running Examples

```bash
# Run the simple demo
python main.py

# Run comprehensive examples
python examples/example.py

# Run tests
python tests/test_i18n.py
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [examples/](examples/) directory for more use cases
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
