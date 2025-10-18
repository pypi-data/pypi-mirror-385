"""
README Copier - A utility package to copy README files to project folders.

This package provides functionality to copy README files from a source location
to a target project folder, with options for customization and formatting.
"""

__version__ = "0.1.3"
__author__ = "kvsh443"

# Embedded README content
__readme__ = """# README Copier

A simple utility package to copy README files to project folders locally.

## Installation

### From TestPyPI

```bash
pip install -i https://test.pypi.org/simple/ security-run-off
```

### From Source

```bash
git clone https://github.com/kvsh443/security-run-off.git
cd security-run-off
pip install -e .
```

## Usage

### As a Command-Line Tool

```bash
# Basic usage
readme-copy README.md ./my-project

# Overwrite existing file
readme-copy README.md ./my-project --overwrite

# Rename the file in target directory
readme-copy README.md ./my-project --rename PROJECT_README.md

# Show information about paths
readme-copy README.md ./my-project --info

# Show version
readme-copy --version
```

### As a Python Library

```python
from readme_copier import copy_readme, ReadmeCopier

# Simple copy using convenience function
copy_readme("README.md", "/path/to/project")

# Copy with overwrite
copy_readme("README.md", "/path/to/project", overwrite=True)

# Copy with rename
copy_readme("README.md", "/path/to/project", rename="PROJECT_README.md")

# Using the ReadmeCopier class for more control
copier = ReadmeCopier("README.md", "/path/to/project")

# Get information about paths
info = copier.get_info()
print(info)

# Perform the copy
success = copier.copy(overwrite=True)
if success:
    print("README copied successfully!")
```

## Features

- ✅ Copy README files to any directory
- ✅ Optional file renaming
- ✅ Overwrite protection with optional override
- ✅ Automatic target directory creation
- ✅ Command-line interface
- ✅ Python API for programmatic use
- ✅ Comprehensive logging
- ✅ Path validation

## API Reference

### `copy_readme(source, target, overwrite=False, rename=None)`

Convenience function to copy a README file.

**Parameters:**

- `source` (str | Path): Path to the source README file
- `target` (str | Path): Path to the target directory
- `overwrite` (bool): If True, overwrite existing file (default: False)
- `rename` (str | None): Optional new name for the copied file

**Returns:**

- `bool`: True if copy was successful, False otherwise

### `ReadmeCopier`

Class to handle README file copying operations.

**Methods:**

- `__init__(source_path, target_path)`: Initialize the copier
- `validate_source()`: Validate that the source file exists
- `validate_target()`: Validate that the target directory exists or can be created
- `copy(overwrite=False, rename=None)`: Copy the README file
- `get_info()`: Get information about source and target paths

## Requirements

- Python >= 3.12
- click >= 8.0.0

## License

MIT License - see LICENSE file for details

## Author

kvsh443

## Links

- GitHub: <https://github.com/kvsh443/security-run-off>
- TestPyPI: <https://test.pypi.org/project/security-run-off/>
"""

from .copier import ReadmeCopier, copy_readme
from .cheatsheet import __readme_full__, get_full_readme

__all__ = [
    "ReadmeCopier", 
    "copy_readme", 
    "__version__", 
    "__readme__",
    "__readme_full__",
    "get_full_readme"
]
