"""Setup script for readme-copier package."""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="security-run-off",
    version="0.1.3",
    author="kvsh443",
    author_email="your.email@example.com",
    description="A utility package to copy README files to project folders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kvsh443/security-run-off",
    project_urls={
        "Bug Tracker": "https://github.com/kvsh443/security-run-off/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "readme_copier": ["*.7z"],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "readme-copy=readme_copier.cli:main",
        ],
    },
)
