# Contributing to Python i18n Modern

Thank you for your interest in contributing to Python i18n Modern!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/UrielCuriel/python_i18n_modern.git
   cd python_i18n_modern
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[all]"
   ```

## Running Tests

Run the test suite:
```bash
python tests/test_i18n.py
```

## Running Examples

Try the examples:
```bash
python examples/example.py
python main.py
```

## Code Style

- Follow PEP 8 guidelines
- Add type hints where appropriate
- Include docstrings for public functions and classes
- Keep functions focused and modular

## Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Bug Reports

Please include:
- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior

## Feature Requests

Feel free to open an issue describing:
- The feature you'd like to see
- Why it would be useful
- Example use cases

Thank you for contributing!
