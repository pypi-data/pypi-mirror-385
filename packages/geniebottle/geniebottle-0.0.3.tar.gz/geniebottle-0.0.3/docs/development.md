# Development Guide

Welcome to the Genie Bottle development guide! This document will help you set up your development environment and contribute to the project.

## Prerequisites

- Python 3.7 or higher
- Git

If you don't have Python installed, the `bottle` CLI will provide platform-specific installation instructions when you run `bottle install`.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/jakemanger/geniebottle.git
cd geniebottle
```

### 2. Set Up Development Environment

The `bottle` CLI tool makes development setup easy:

**macOS/Linux/WSL:**

```bash
./bottle install
./bottle link    # Make 'bottle' globally available
```

**Windows:**

```bash
bottle.bat install
bottle.bat link  # Make 'bottle' globally available
```

The install command will:

- Check for Python 3.7+ (and provide installation instructions if needed)
- Create a virtual environment in `venv/`
- Install the package in editable mode
- Install all development dependencies

The link command adds `bottle` to your PATH so you can run `bottle` from anywhere instead of `./bottle`.

### 3. Start Development

Now you can use `bottle` commands from anywhere!

**Run the agent example + docs server:**

```bash
bottle dev
```

This starts:

- Agent example (in the terminal)
- Documentation server at <http://127.0.0.1:8000>

Press `Ctrl+C` to stop both servers.

## Beard CLI Reference

The `bottle` command provides npm-style development commands:

### Installation & Setup

```bash
bottle install          # Set up virtual environment and install dependencies
bottle link             # Make bottle globally available in PATH
bottle clean            # Remove venv, cache files, and build artifacts
```

### Development Servers

```bash
bottle dev              # Start agent + docs server concurrently
bottle agent            # Run just the agent example
bottle docs             # Run just the documentation server
```

### Running Examples

```bash
bottle list             # List all available examples
bottle open chat         # Run the chat example
bottle open agent        # Run the agent example
bottle open <name>       # Run any example by name (without .py extension)
```

### Testing & Documentation

```bash
bottle test             # Run tests with pytest
bottle test -v          # Run tests with verbose output
bottle build-docs       # Build static documentation to site/
```

### Getting Help

```bash
bottle help             # Show all available commands
```

## Project Structure

```
geniebottle/
├── magic/                 # Main package source code
│   ├── __init__.py
│   ├── spellbooks/        # Model integrations
│   └── ...
├── examples/              # Example scripts
│   ├── agent.py           # Interactive agent example
│   ├── chat.py            # Simple chat example
│   └── ...
├── docs/                  # Documentation source
├── tests/                 # Test files
├── bottle.py               # Cross-platform CLI script
├── bottle                  # Unix wrapper
├── bottle.bat              # Windows wrapper
└── pyproject.toml         # Package configuration
```

## Development Workflow

### Making Changes

1. Create a new branch for your feature/fix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes to the code

3. Test your changes:

   ```bash
   bottle test
   ```

4. Run the examples to verify:

   ```bash
   bottle open agent
   ```

### Adding New Examples

1. Create a new Python file in `examples/`:

   ```bash
   touch examples/my_example.py
   ```

2. Write your example code

3. Test it:

   ```bash
   bottle open my_example
   ```

### Updating Documentation

1. Edit documentation files in `docs/`

2. Start the docs server to preview:

   ```bash
   bottle docs
   ```

3. Visit <http://127.0.0.1:8000> to see your changes

4. Build static docs:

   ```bash
   bottle build-docs
   ```

## Platform-Specific Notes

### Windows

- Use `bottle.bat` instead of `./bottle`
- If you have Git Bash or WSL, you can also use `./bottle`
- Python is typically installed from python.org or using `winget`

### macOS

- Python 3 can be installed via Homebrew: `brew install python3`
- The `bottle` script will work natively

### Linux

- Python 3 is usually pre-installed or available via package manager
- May need to install `python3-venv`: `sudo apt install python3-venv`

## Troubleshooting

### "Python not found" error

Run `bottle install` and follow the platform-specific installation instructions provided.

### Virtual environment issues

Clean and reinstall:

```bash
bottle clean
bottle install
```

### Permission denied (Unix/macOS)

Make the script executable:

```bash
chmod +x bottle
```

### Import errors

Make sure you're using the virtual environment's Python:

```bash
bottle install  # Reinstall dependencies
```

## Contributing

We welcome contributions! Here's how to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly (`bottle test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

### Testing

- Add tests for new features in `tests/`
- Ensure all tests pass before submitting PR
- Test on your platform (Windows/macOS/Linux)

## Getting Help

- Check the [documentation](https://github.com/jakemanger/geniebottle#readme)
- Open an [issue](https://github.com/jakemanger/geniebottle/issues)
- Join the discussion

## License

Genie Bottle is licensed under the Mozilla Public License 2.0. See [LICENSE](./LICENSE) for details.
