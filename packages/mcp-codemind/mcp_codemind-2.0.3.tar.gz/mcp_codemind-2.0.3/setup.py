#!/usr/bin/env python3
"""Setup script for CodeMind MCP Server.

For backward compatibility with older pip versions.
Modern installations should use pyproject.toml.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="mcp-codemind",
    version="2.0.3",
    author="MrUnreal",
    author_email="mrunreal@users.noreply.github.com",
    description="Multi-Workspace MCP Memory Server for GitHub Copilot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MrUnreal/codemind",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "configs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "codemind=codemind:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="mcp model-context-protocol github-copilot code-analysis semantic-search",
    project_urls={
        "Bug Tracker": "https://github.com/MrUnreal/codemind/issues",
        "Documentation": "https://github.com/MrUnreal/codemind/blob/master/README.md",
        "Source Code": "https://github.com/MrUnreal/codemind",
        "Changelog": "https://github.com/MrUnreal/codemind/blob/master/CHANGELOG.md",
    },
)
