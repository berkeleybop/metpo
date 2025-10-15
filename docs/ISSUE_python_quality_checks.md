# CI: Implement Python code quality checks (ruff, mypy, pytest)

### The Issue

The repository currently has CI configured for ontology quality checks in `.github/workflows/qc.yml`, but there are no automated standards for the Python code itself.

### Proposal

To improve code quality, maintainability, and catch errors early, we should implement the following standard tools into the CI pipeline:

- **`ruff`**: For fast linting and code formatting.
- **`mypy`**: For static type checking.
- **`pytest`**: For running a test suite.

This would likely involve adding a new job to the `qc.yml` workflow that runs on pushes and pull requests, ensuring all Python code adheres to a consistent standard.
