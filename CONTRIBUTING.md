# Contributing to NetBeacon

Thank you for your interest in contributing to NetBeacon!

## How to Contribute

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/amirradmansh73-lgtm/pro.git
   cd pro
   ```
3. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Run test suite**:
   ```bash
   pytest
   ```
6. **Commit and push** your changes, then submit a Pull Request.

## Code Standards
- Follow PEP 8 style guidelines.
- Add unit tests for any new features or bug fixes.
- Ensure all CI tests pass.
