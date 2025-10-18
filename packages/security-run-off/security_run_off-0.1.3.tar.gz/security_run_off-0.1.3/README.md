# README Copier

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

# Display embedded README documentation
readme-copy --show-readme
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

# Access the embedded README
from readme_copier import __readme__
print(__readme__)  # Print the full embedded README

# Save embedded README to a directory
copier.save_embedded_readme("PACKAGE_README.md")
```

### Accessing Embedded README

The package includes an embedded README that can be accessed programmatically:

```python
# Method 1: Direct import
from readme_copier import __readme__
print(__readme__)

# Method 2: Using helper function
from readme_copier.copier import get_embedded_readme
readme_content = get_embedded_readme()

# Method 3: Via CLI
# readme-copy --show-readme

# Save embedded README to a file
from readme_copier import ReadmeCopier
copier = ReadmeCopier("source.md", "./output")
copier.save_embedded_readme("EMBEDDED_README.md")
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
- ✅ **Embedded README** - Access documentation directly from Python code

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
- `save_embedded_readme(filename="README.md")`: Save the embedded README to target directory

### Module-level Variables

- `__readme__`: Contains the full embedded README documentation
- `__version__`: Package version string
- `__author__`: Package author

### `get_embedded_readme()`

Helper function to retrieve the embedded README content.

**Returns:**
- `str`: The embedded README documentation

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/kvsh443/security-run-off.git
cd security-run-off

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dependencies
pip install -e .
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=readme_copier tests/
```

### Building the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the distribution
twine check dist/*
```

### Uploading to TestPyPI

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# You'll need to enter your TestPyPI credentials
# Username: __token__
# Password: your-testpypi-api-token
```

## Requirements

- Python >= 3.12
- click >= 8.0.0

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

kvsh443

## Links

- GitHub: https://github.com/kvsh443/security-run-off
- TestPyPI: https://test.pypi.org/project/security-run-off/
