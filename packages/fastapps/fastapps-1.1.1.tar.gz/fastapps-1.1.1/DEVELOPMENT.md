# Development Guide

Quick reference for FastApps developers.

## Setup

```bash
# Clone repository
git clone https://github.com/fastapps-framework/fastapps.git
cd fastapps

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

## Daily Workflow

### Before You Start

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-feature
```

### While Developing

```bash
# Format code (do this often!)
black .

# Lint and auto-fix
ruff check --fix .

# Run tests
pytest

# Run specific test
pytest tests/test_widget.py -v

# Check coverage
pytest --cov=fastapps --cov-report=html
```

### Before Committing

```bash
# Run all checks
black .
ruff check .
pytest --cov=fastapps

# If all pass, commit
git add .
git commit -m "feat: add new feature"
```

## Code Formatting

### Black - Automatic Formatter

```bash
# Format all files
black .

# Check what would change (don't modify)
black --check .

# Format specific file/directory
black fastapps/core/
black fastapps/cli/commands/create.py
```

**Black is non-negotiable** - all code must be Black-formatted before merge.

### Ruff - Linter

```bash
# Lint all files
ruff check .

# Auto-fix issues
ruff check --fix .

# Lint specific file
ruff check fastapps/core/widget.py

# Show all violations (even fixed ones)
ruff check --show-fixes .
```

## Testing

### Running Tests

```bash
# All tests
pytest

# With verbose output
pytest -v

# Specific test file
pytest tests/test_widget.py

# Specific test function
pytest tests/test_widget.py::test_widget_creation

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run tests matching pattern
pytest -k "widget"
```

### Coverage

```bash
# Generate coverage report
pytest --cov=fastapps

# HTML coverage report
pytest --cov=fastapps --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Coverage with missing lines
pytest --cov=fastapps --cov-report=term-missing
```

### Writing Tests

```python
# tests/test_my_feature.py
import pytest
from fastapps import Widget


def test_simple_case():
    """Test description."""
    result = my_function()
    assert result == expected


@pytest.fixture
def sample_widget():
    """Reusable test fixture."""
    class TestWidget(Widget):
        def render(self):
            return {"message": "test"}
    return TestWidget()


def test_with_fixture(sample_widget):
    """Use the fixture."""
    assert sample_widget.render()["message"] == "test"


@pytest.mark.slow
def test_slow_operation():
    """Mark slow tests."""
    # This test takes a while
    pass


# Run without slow tests: pytest -m "not slow"
```

## Building and Packaging

```bash
# Install build tools
pip install build twine

# Build distribution packages
python -m build

# Check package validity
twine check dist/*

# Test upload to Test PyPI (optional)
twine upload --repository testpypi dist/*

# Install from built package (testing)
pip install dist/fastapps-*.whl
```

## Project Structure

```
fastapps/
├── fastapps/               # Main package
│   ├── __init__.py        # Package exports
│   ├── auth/              # Authentication system
│   ├── builder/           # Widget build system
│   ├── cli/               # CLI commands
│   │   ├── main.py       # CLI entry point
│   │   └── commands/     # Command implementations
│   ├── core/              # Core functionality
│   │   ├── widget.py     # Base widget class
│   │   └── server.py     # MCP server
│   ├── types/             # Type definitions
│   └── dev_server.py      # Development server
│
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Shared fixtures
│   ├── test_widget.py
│   └── test_import.py
│
├── examples/               # Example scripts
├── .github/                # GitHub Actions workflows
│   └── workflows/
│
├── pyproject.toml          # Project configuration
├── setup.py                # Legacy setup file
├── pytest.ini              # Pytest configuration
├── CONTRIBUTING.md         # Contribution guidelines
├── CODE_STYLE.md           # Code style guide
└── README.md               # Project readme
```

## Common Tasks

### Adding a New Widget Feature

1. **Write the code** in appropriate module
2. **Add tests** in `tests/`
3. **Update exports** in `fastapps/__init__.py` if needed
4. **Format and lint**:
   ```bash
   black .
   ruff check --fix .
   ```
5. **Run tests**: `pytest`
6. **Update docs** if API changed

### Adding a New CLI Command

1. **Create command file** in `fastapps/cli/commands/`
2. **Import in** `fastapps/cli/main.py`
3. **Add tests** in `tests/`
4. **Update CLI examples** in README.md

### Fixing a Bug

1. **Write a failing test** that demonstrates the bug
2. **Fix the bug**
3. **Verify test passes**
4. **Add regression test** if appropriate
5. **Format and commit**

## Debugging

### Interactive Debugging

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()

# Run pytest with pdb
pytest --pdb  # Drop into debugger on failure
pytest --pdb -x  # Stop on first failure
```

### Print Debugging

```python
# Use rich for better output
from rich import print as rprint
from rich.console import Console

console = Console()

# Pretty print
rprint({"key": "value", "list": [1, 2, 3]})

# With colors
console.print("[bold red]Error![/bold red]")
console.print("[green]Success![/green]")

# Print with inspect
from rich import inspect
inspect(my_object, methods=True)
```

### Logging

```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use in code
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## Git Workflow

### Feature Development

```bash
# 1. Start from main
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes, commit often
git add .
git commit -m "feat: add initial implementation"

# 4. Keep up to date with main
git fetch upstream
git rebase upstream/main

# 5. Push to your fork
git push origin feature/my-feature

# 6. Create pull request on GitHub
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>(<scope>): <description>

# Types:
feat: New feature
fix: Bug fix
docs: Documentation
style: Code style (formatting)
refactor: Code refactoring
test: Tests
chore: Maintenance

# Examples:
git commit -m "feat(cli): add create command"
git commit -m "fix(widget): resolve render issue"
git commit -m "docs(readme): update installation steps"
git commit -m "test(core): add widget tests"
```

## CI/CD

### GitHub Actions Workflows

Located in `.github/workflows/`:

- **`ci.yml`**: Main CI pipeline (tests, lint, build)
- **`publish.yml`**: PyPI publishing on release
- **`codeql.yml`**: Security scanning
- **`dependency-review.yml`**: Dependency security

### Local CI Simulation

Run the same checks that CI runs:

```bash
# Format check
black --check .

# Linting
ruff check .

# Tests with coverage
pytest --cov=fastapps --cov-report=xml

# Type checking (optional)
mypy fastapps --ignore-missing-imports

# Build check
python -m build
twine check dist/*
```

## Troubleshooting

### Import Errors After Install

```bash
# Reinstall in editable mode
pip install -e ".[dev]"
```

### Tests Failing Locally

```bash
# Clean cache and rerun
pytest --cache-clear
rm -rf .pytest_cache __pycache__

# Reinstall dependencies
pip install -e ".[dev]" --force-reinstall
```

### Black/Ruff Conflicts

```bash
# Black takes precedence
black .

# Then run ruff
ruff check --fix .
```

### Pre-commit Hook Fails

```bash
# Update pre-commit
pre-commit autoupdate

# Run manually
pre-commit run --all-files

# Skip if needed (not recommended)
git commit --no-verify
```

## Performance Testing

```bash
# Time a specific test
pytest tests/test_widget.py --durations=10

# Profile with pytest-profiling
pip install pytest-profiling
pytest --profile

# Memory profiling
pip install memory_profiler
python -m memory_profiler my_script.py
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int = 0) -> bool:
    """Short one-line description.

    Longer description if needed, explaining the function's purpose
    and behavior in more detail.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2 (default: 0)

    Returns:
        Description of return value

    Raises:
        ValueError: When arg1 is empty
        TypeError: When arg2 is negative

    Example:
        >>> function("test", 5)
        True
    """
    pass
```

## Resources

- **Black**: https://black.readthedocs.io/
- **Ruff**: https://docs.astral.sh/ruff/
- **pytest**: https://docs.pytest.org/
- **FastApps Docs**: https://www.fastapps.org/

## Quick Command Reference

```bash
# Format all code
black .

# Lint and fix
ruff check --fix .

# Run tests
pytest

# Run tests with coverage
pytest --cov=fastapps

# Build package
python -m build

# Install locally
pip install -e ".[dev]"

# Run pre-commit on all files
pre-commit run --all-files
```

---

Happy coding! 🚀
