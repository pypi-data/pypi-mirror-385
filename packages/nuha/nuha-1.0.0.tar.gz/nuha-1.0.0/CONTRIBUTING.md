# Contributing to Nuha

Thank you for considering contributing to Nuha! We welcome contributions from the community.

## Development Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/u3n-ai/nuha.git
   cd nuha
   ```

2. **Install UV (if not already installed):**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies:**

   ```bash
   uv sync
   ```

4. **Run in development mode:**
   ```bash
   uv run nuha --help
   ```

## Development Workflow

### Running Tests

```bash
uv run pytest
```

### Code Formatting

We use Ruff for both linting and formatting:

```bash
# Format code
uv run ruff format .

# Check formatting
uv run ruff format --check .
```

### Linting

```bash
# Lint code
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

### Type Checking

```bash
uv run pyrefly check .
```

### Pre-commit Checks

Before committing, run all checks:

```bash
# Format
uv run ruff format .

# Lint and fix
uv run ruff check --fix .

# Type check
uv run pyrefly check .

# Run tests
uv run pytest
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for public APIs
- Keep functions focused and single-purpose
- Use meaningful variable names

## Pull Request Process

1. **Fork the repository** and create a new branch from `main`
2. **Make your changes** following the code style guidelines
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Run all checks** to ensure code quality
6. **Commit your changes** using conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `refactor:` for code refactoring
   - `test:` for test additions/changes
7. **Push to your fork** and submit a pull request

## Pull Request Guidelines

- Keep PRs focused on a single feature or bug fix
- Include tests for new functionality
- Update documentation for user-facing changes
- Ensure all CI checks pass
- Write clear PR descriptions explaining the changes

## Reporting Issues

When reporting issues, please include:

- Nuha version (`nuha --version`)
- Operating system and shell
- Steps to reproduce the issue
- Expected vs actual behavior
- Any error messages or logs

## Feature Requests

We welcome feature requests! Please:

- Check if the feature already exists or has been requested
- Clearly describe the use case
- Explain how it would benefit users
- Consider submitting a PR if you can implement it

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing opinions and experiences

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Join our community channels (links in README)

Thank you for contributing to Nuha! 🤖
