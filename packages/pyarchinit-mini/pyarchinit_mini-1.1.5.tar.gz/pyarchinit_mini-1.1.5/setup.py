"""
Setup script for PyArchInit-Mini
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

# Read requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    requirements = (this_directory / "requirements.txt").read_text().splitlines()

setup(
    name="pyarchinit-mini",
    version="1.1.5",
    author="PyArchInit Team",
    author_email="enzo.ccc@gmail.com",
    description="Lightweight archaeological data management system with multi-user authentication, real-time collaboration, and analytics dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/enzococca/pyarchinit-mini",
    project_urls={
        "Bug Tracker": "https://github.com/enzococca/pyarchinit-mini/issues",
        "Documentation": "https://github.com/enzococca/pyarchinit-mini/blob/main/README.md",
        "Source Code": "https://github.com/enzococca/pyarchinit-mini",
    },
    packages=find_packages(exclude=["docs*", "examples*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Database :: Database Engines/Servers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8,<3.15",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyarchinit-mini=pyarchinit_mini.cli:main",
            "pyarchinit-graphml=pyarchinit_mini.cli.graphml_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pyarchinit_mini": ["*.yaml", "*.yml", "*.json", "graphml_converter/templates/*.graphml"],
    },
    keywords=[
        "archaeology",
        "archaeological data",
        "heritage",
        "cultural heritage",
        "database",
        "api",
        "gis",
        "stratigraphy",
        "archaeological recording",
        "harris matrix",
        "finds",
        "inventory",
        "excavation",
    ],
    zip_safe=False,
)