# Nuha Project Setup Summary

## Project Overview

Nuha is an AI-powered terminal assistant that helps developers understand and debug command-line issues.

## Key Features Implemented

### 1. Multiple AI Provider Support

- **ZHIPUAI GLM** (default) - Chinese AI model
- **OpenAI GPT** - GPT-4 and GPT-3.5 models
- **Anthropic Claude** - Claude 3.5 Sonnet
- **DeepSeek** - Cost-effective alternative

Users can easily switch between providers using:

```bash
nuha setup --provider openai
nuha setup --provider claude
nuha setup --provider deepseek
```

### 2. Code Quality Tools

- **Ruff** for linting and formatting (replaces Black and Flake8)
- **Pyrefly** for type checking
- **Pytest** for testing with coverage
- All configured in `pyproject.toml`

### 3. Project Structure

```
nuha-cli/
├── nuha/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── explain.py
│   │       ├── analyze.py
│   │       ├── debug.py
│   │       ├── setup.py
│   │       └── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── ai_client.py
│   │   ├── terminal_reader.py
│   │   └── command_parser.py
│   └── utils/
│       ├── __init__.py
│       └── formatter.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_terminal_reader.py
│   └── test_command_parser.py
├── pyproject.toml
├── Makefile
├── setup_binary.py
├── install.sh
├── .gitignore
├── .env.example
├── LICENSE
├── CONTRIBUTING.md
├── README.md
└── .github/
    └── workflows/
        └── ci.yml
```

## Installation and Setup

### For Development:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run in dev mode
uv run nuha --help
```

### For Users:

```bash
# Install via pip (when published)
pip install nuha

# Or download binary from releases
curl -L https://github.com/u3n-ai/nuha/releases/latest/download/nuha -o nuha
chmod +x nuha
sudo mv nuha /usr/local/bin/
```

## Development Commands

### Using Make:

```bash
make install      # Install dependencies
make test         # Run tests
make lint         # Lint code
make format       # Format code
make type-check   # Type check
make all          # Run all checks
```

### Using UV directly:

```bash
uv run pytest                    # Run tests
uv run ruff format .            # Format code
uv run ruff check .             # Lint code
uv run ruff check --fix .       # Fix linting issues
uv run pyrefly check .         # Type check
```

## Configuration

### Config File Location:

`~/.nuha/config.toml`

### Example Configuration:

```toml
[ai]
provider = "zhipuai"
model = "glm-4.5-flash"
temperature = 0.3
max_tokens = 2000

[terminal]
history_limit = 50
auto_analyze = true
include_context = true

[output]
format = "rich"
color = true
verbose = false

[behavior]
auto_explain_errors = false
interactive_mode = true
save_analysis = true
```

### Environment Variables:

```bash
# API Keys
export ZHIPUAI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export DEEPSEEK_API_KEY="your-key"
```

## Usage Examples

### Explain Commands:

```bash
nuha explain "git push"
nuha explain --auto                    # Explain last command
nuha explain "npm install" --error "EACCES: permission denied"
```

### Analyze Patterns:

```bash
nuha analyze --session                 # Analyze current session
nuha analyze --pattern "permission"    # Search for pattern
```

### Interactive Debugging:

```bash
nuha debug --interactive
nuha debug "Docker container keeps crashing"
```

### Setup and Configuration:

```bash
nuha setup                            # Interactive setup
nuha setup --provider openai          # Setup specific provider
nuha config --show                    # Show configuration
nuha config --edit                    # Edit configuration
```

## CI/CD

GitHub Actions workflow configured for:

- Linting with Ruff
- Type checking with Pyrefly
- Testing on multiple Python versions (3.11-3.12)
- Testing on multiple platforms (Ubuntu, macOS, Windows)
- Code coverage reporting

## Key Optimizations

1. **Ruff Integration**: Fast, all-in-one linting and formatting
2. **Multiple AI Providers**: Flexibility to choose based on needs and budget
3. **Type Safety**: Full type hints with Pyrefly checking
4. **Modern Tooling**: UV for fast dependency management
5. **Binary Distribution**: PyInstaller for standalone executables
6. **Cross-platform**: Works on Linux, macOS, and Windows

## Next Steps

1. Install dependencies: `uv sync`
2. Setup API keys: `nuha setup`
3. Run tests: `make test`
4. Try it out: `uv run nuha explain --auto`

## Contributing

See `CONTRIBUTING.md` for development guidelines and workflow.

## License

MIT License - see `LICENSE` file for details.
