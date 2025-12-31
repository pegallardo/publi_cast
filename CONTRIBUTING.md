# Contributing to PubliCast

Thank you for your interest in contributing to PubliCast! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Audacity installed on your system
- Git for version control
- Windows OS (current implementation is Windows-only)

### Setting Up Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/pegallardo/publi_cast.git
   cd publi_cast
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # PowerShell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Enable Audacity mod-script-pipe**
   - Open Audacity
   - Go to Edit → Preferences → Modules
   - Set mod-script-pipe to "Enabled"
   - Restart Audacity

## Development Workflow

### Project Structure
```
publi_cast/
├── main.py              # Application entry point
├── config.py            # Configuration settings
├── controllers/         # User interaction layer
├── services/            # Business logic
├── repositories/        # Data access layer
├── dialogs/             # UI dialogs
├── utils/               # Utility functions
└── tests/               # Test files
```

### Making Changes

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow PEP 8 style guidelines
   - Add docstrings to functions and classes
   - Keep functions focused and single-purpose

3. **Test your changes**
   ```bash
   pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the GitHub repository
   - Click "New Pull Request"
   - Describe your changes clearly

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep lines under 100 characters when possible

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Test both automated and manual fallback modes

## Reporting Issues

When reporting issues, please include:
- Python version
- Audacity version
- Windows version
- Steps to reproduce
- Expected vs actual behavior
- Relevant log files from `logs/` directory

## Feature Requests

We welcome feature requests! Please:
- Check if the feature already exists
- Describe the use case clearly
- Explain how it benefits users

## Questions?

Feel free to open an issue for questions or discussions.

## License

By contributing, you agree that your contributions will be licensed under the GPL-3.0 License.

