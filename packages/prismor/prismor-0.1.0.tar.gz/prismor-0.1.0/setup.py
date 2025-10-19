"""Setup script for Prismor CLI."""

from setuptools import setup, find_packages
import os


def read_file(filename):
    """Read file contents."""
    with open(filename, encoding="utf-8") as f:
        return f.read()


# Read README for long description
long_description = ""
if os.path.exists("README.md"):
    long_description = read_file("README.md")

setup(
    name="prismor",
    version="0.1.0",
    author="Prismor",
    author_email="support@prismor.dev",
    description="A CLI tool for scanning GitHub repositories for vulnerabilities, secrets, and generating SBOMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PrismorSec/prismor-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "prismor=prismor.cli:main",
        ],
    },
    keywords="security scanning vulnerability sbom secrets github",
    project_urls={
        "Bug Reports": "https://github.com/PrismorSec/prismor-cli/issues",
        "Source": "https://github.com/PrismorSec/prismor-cli",
        "Documentation": "https://docs.prismor.dev",
        "Homepage": "https://prismor.dev",
    },
)

