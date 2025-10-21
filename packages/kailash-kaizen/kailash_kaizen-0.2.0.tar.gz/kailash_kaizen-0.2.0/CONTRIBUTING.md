# Contributing to Kaizen AI

Thank you for your interest in contributing to Kaizen AI!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/kaizen.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest tests/`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
flake8 src/ tests/

# Run type checking
mypy src/
```

## Code Standards

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for all public APIs
- Include tests for new features
- Update documentation as needed

## Testing Requirements

- All tests must pass before merging
- New features require tests
- Maintain >95% test coverage
- Follow TDD methodology when possible

## Pull Request Process

1. Update documentation for any API changes
2. Add tests for new functionality
3. Ensure all CI checks pass
4. Request review from maintainers
5. Address any review feedback
6. Squash commits before merging

## Code of Conduct

Be respectful and inclusive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## Questions?

Open an issue or reach out to the maintainers.

Thank you for contributing!
