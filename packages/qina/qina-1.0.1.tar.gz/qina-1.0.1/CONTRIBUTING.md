# Contributing to QINA Security Editor

Thank you for your interest in contributing to QINA Security Editor! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CloudDefenseAI/qina-security-editor.git
   cd qina-security-editor
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Set up your credentials:**
   ```bash
   export CLOUDDEFENSE_API_KEY=your_api_key
   export CLOUDDEFENSE_CLIENT_ID=your_client_id
   export CLOUDDEFENSE_TEAM_ID=your_team_id
   ```

## Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test them:
   ```bash
   python -m qina_security_editor.main
   ```

3. **Run tests** (if available):
   ```bash
   python -m pytest tests/
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small

## Testing

Before submitting a PR, ensure:
- [ ] Code runs without errors
- [ ] No hardcoded credentials
- [ ] Proper error handling
- [ ] Documentation updated if needed

## Release Process

Releases are managed through GitHub releases. When a new release is created, it automatically triggers the PyPI upload workflow.

## Security

- Never commit API keys or credentials
- Use environment variables for sensitive data
- Report security issues privately to security@clouddefenseai.com

## Questions?

Feel free to open an issue for questions or discussions!
