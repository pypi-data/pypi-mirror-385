# Contributing to FastAPI Teams Bot

Thank you for your interest in contributing to FastAPI Teams Bot! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/vishalgoel2/fastapi-teams-bot/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (Python version, OS, etc.)
   - Any relevant code snippets or error messages

### Suggesting Features

1. Check if the feature has been suggested in [Issues](https://github.com/vishalgoel2/fastapi-teams-bot/issues)
2. Create a new issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives you've considered
   - How it would benefit other users

### Pull Requests

1. **Fork the repository** and create your branch from `main`
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Set up development environment**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Make your changes**
   - Write clear, readable code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Run tests and linters**
   ```bash
   # Run tests
   pytest tests/ -v --cov=fastapi_teams_bot
   
   # Format code
   black src/ tests/
   
   # Check linting
   ruff check src/ tests/
   
   # Type checking
   mypy src/
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
   
   Use clear, descriptive commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for tests
   - `refactor:` for code refactoring

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Create a Pull Request**
   - Provide a clear title and description
   - Reference any related issues
   - Ensure all checks pass

## Development Guidelines

### Code Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting (line length: 88)
- Use type hints for all functions
- Write docstrings for all public functions and classes

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use meaningful test names
- Include both positive and negative test cases

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update examples if relevant
- Add entries to CHANGELOG.md

## Project Structure

```
fastapi-teams-bot/
├── src/fastapi_teams_bot/
│   ├── __init__.py      # Public API
│   ├── bot.py           # Main bot class
│   ├── config.py        # Configuration
│   ├── types.py         # Type definitions
│   └── handlers.py      # Message handlers
├── tests/               # Test suite
├── examples/            # Usage examples
└── docs/               # Documentation
```

## Release Process

1. Update version in `pyproject.toml` and `src/fastapi_teams_bot/__init__.py`
2. Update `CHANGELOG.md`
3. Create a git tag
4. Push tag to trigger automated release

## Questions?

Feel free to ask questions by:
- Opening an issue
- Starting a discussion
- Reaching out to maintainers

Thank you for contributing! 🎉
