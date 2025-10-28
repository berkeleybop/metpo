# Python Code Style Guidelines for notebooks/

## General Principles

Follow PEP 8 conventions and common Python best practices.

## Script Structure

### 1. File Header
```python
#!/usr/bin/env python3
"""Brief description of what the script does."""
```

### 2. Imports
Group imports at the top in this order:
```python
# Standard library imports
import csv
import time
from pathlib import Path

# Third-party imports
import click
import pandas as pd
import requests

# Local imports (if any)
from metpo import utils
```

### 3. Functions and Classes
```python
def my_function(param1, param2):
    """
    Brief description of what function does.
    
    Use single docstring for the function.
    NO duplicate docstrings.
    """
    # Implementation
    pass
```

### 4. Click CLI
```python
@click.command()
@click.option('--input-file', required=True, help='Input file path')
@click.option('--output-file', default='output.csv', help='Output file path')
def main(input_file, output_file):
    """Main entry point with clear docstring."""
    pass


if __name__ == '__main__':
    main()
```

## Common Issues to Avoid

### ❌ Duplicate Docstrings
```python
# WRONG
def main(sizes_csv):
    """Fetch ontology names."""
    
    """Fetch ontology names."""  # Duplicate!
    pass
```

```python
# CORRECT
def main(sizes_csv):
    """Fetch ontology names."""
    pass
```

### ❌ Imports Inside Functions
```python
# WRONG
def main():
    import pandas as pd  # Should be at top of file
    pass
```

```python
# CORRECT
import pandas as pd

def main():
    pass
```

### ❌ Missing Shebang or Wrong Permissions
```python
# File: my_script.py
# Missing #!/usr/bin/env python3
def main():
    pass
```

```bash
# WRONG - not executable
-rw-rw-r-- my_script.py

# CORRECT - executable
-rwxrwxr-x my_script.py
chmod +x my_script.py
```

## Shell Scripts

### File Header
```bash
#!/bin/bash
# Brief description
```

### Make Executable
```bash
chmod +x script.sh
```

### Best Practices
- Use `set -e` to exit on errors
- Quote variables: `"$variable"`
- Use meaningful variable names

## Checklist for New Scripts

- [ ] Shebang line present (`#!/usr/bin/env python3` or `#!/bin/bash`)
- [ ] Module docstring at top of file
- [ ] Imports at top (not inside functions)
- [ ] Single docstring per function (no duplicates)
- [ ] Click CLI with `--help` for all options
- [ ] `if __name__ == '__main__':` guard for entry point
- [ ] File is executable (`chmod +x script.py`)
- [ ] Tested with `--help` flag

## Automated Checks (Future)

See issue #231 for planned automation:
- ruff for linting
- mypy for type checking  
- pytest for testing
- pre-commit hooks

Until then, manually verify these guidelines before committing.

## Resources

- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
