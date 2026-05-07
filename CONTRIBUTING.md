# Contributing Guide

Thank you for interest in contributing to the Professional Algorithmic Trading System!

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps which reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots and animated GIFs if possible**

### Suggesting Enhancements

When creating enhancement suggestions, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and the expected behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

- Fill in the required template
- Follow the Python and documentation styleguides
- End all files with a newline
- Avoid platform-specific code

## Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Python Styleguide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep lines under 100 characters

#### Example:

```python
def calculate_position_size(
    account_size: float,
    risk_percent: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """
    Calculate position size based on risk parameters.
    
    Args:
        account_size: Total account balance
        risk_percent: Risk percentage (e.g., 0.02 for 2%)
        entry_price: Entry price of the trade
        stop_loss: Stop loss price
    
    Returns:
        Position size in lots
    """
    risk_amount = account_size * risk_percent
    pip_distance = abs(entry_price - stop_loss)
    return risk_amount / (pip_distance * 100000)
```

### Documentation Styleguide

- Use Markdown for all documentation
- Include code examples where helpful
- Keep documentation up to date with code changes
- Use clear and concise language

## Development Setup

### 1. Fork the Repository

```bash
git clone https://github.com/yourusername/trading-system.git
cd trading-system
```

### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 4. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # dev tools
```

### 5. Make Your Changes

- Keep commits atomic and focused
- Write tests for new features
- Update documentation as needed

### 6. Run Tests

```bash
pytest tests/
black .
flake8 .
```

### 7. Submit Pull Request

- Push to your fork
- Create a pull request to the main repository
- Fill out the PR template
- Respond to any feedback

## Testing Guidelines

### Unit Tests

```bash
pytest tests/unit/
```

### Integration Tests

```bash
pytest tests/integration/
```

### All Tests

```bash
pytest tests/
```

### Code Coverage

```bash
pytest --cov=hft tests/
```

## Code Review Process

1. At least one approving review required
2. All CI checks must pass
3. Documentation must be updated
4. Code follows style guidelines

## Additional Notes

### Issue and Pull Request Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed

### Release Process

1. Update version in `__init__.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v2.0`
4. Push tag: `git push origin v2.0`

## Community

- Be respectful and constructive
- Welcome new contributors
- Help others learn
- Share knowledge and experience

## Questions?

Feel free to open a discussion or issue if you have any questions!

---

**Thank you for contributing!** 🎉
