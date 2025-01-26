# Contributing to Rhesis SDK

Thank you for your interest in contributing to Rhesis SDK! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/rhesis-ai/rhesis-sdk.git
cd rhesis-sdk
```

2. Install Poetry (our dependency manager):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies including development tools:
```bash
poetry install --with dev
```

Optionally, you can install the development tools and documentation:
```bash
poetry install --with dev,docs
```

## Development Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Enable pre-commit hooks:
```bash
poetry run pre-commit install
```

3. Make your changes and ensure all checks pass:
```bash
poetry run black .        # Format code
poetry run flake8        # Lint code
poetry run mypy          # Type check
poetry run pytest        # Run tests
```

4. Commit your changes:
```bash
git add .
git commit -m "feat: your descriptive commit message"
```

5. Push your changes and create a Pull Request:
```bash
git push origin feature/your-feature-name
```

## Pull Request Guidelines

- Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages
- Include tests for new features
- Update documentation as needed
- Ensure all checks pass before requesting review

## Code Style

We use several tools to maintain code quality:
- [Black](https://black.readthedocs.io/) for code formatting
- [Flake8](https://flake8.pycqa.org/) for style guide enforcement
- [MyPy](https://mypy.readthedocs.io/) for static type checking
- [Pre-commit](https://pre-commit.com/) for automated checks

## Testing

- Write tests for all new features and bug fixes
- Tests should be placed in the `tests/` directory
- Run the test suite with `poetry run pytest`

## Documentation

- Update documentation for any changed functionality
- Include docstrings for new functions and classes
- Keep the README.md up to date with any user-facing changes

## Questions or Need Help?

If you have questions or need help with the contribution process:
- Contact us at support@rhesis.ai
- Create an issue in the repository
- Check our [documentation](https://docs.rhesis.ai) 