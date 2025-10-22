"""
Setup script for testtoolkit library.
"""

from setuptools import setup, find_packages
import os

# Read version from component.json
def get_version():
    import json
    import os
    
    # Try current directory first, then parent directory
    for path in ["component.json", "../component.json", "./component.json"]:
        try:
            if os.path.exists(path):
                with open(path) as f:
                    component = json.load(f)
                return component['version']
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    
    # Fallback version if component.json not found
    return "1.0.0"

# Read long description from README.md
def get_long_description():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    return ""

setup(
    name="lib-testtoolkit-python",
    version=get_version(),
    author="QA Team",
    author_email="qa@backend.com",
    description="Reusable utilities for Python test automation projects",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/entinco/bt-templates-harnesses/lib-testtoolkit-python/",
    project_urls={
        "Bug Tracker": "https://bitbucket.org/entinco/bt-templates-harnesses/issues",
        "Repository": "https://bitbucket.org/entinco/bt-templates-harnesses/src/master/lib-testtoolkit-python/",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "pystache>=0.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # Add command line tools if needed
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 