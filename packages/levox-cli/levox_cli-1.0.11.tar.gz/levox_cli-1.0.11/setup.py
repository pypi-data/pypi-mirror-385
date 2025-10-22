#!/usr/bin/env python3
"""
Setup configuration for Levox PII/GDPR Detection CLI
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README_PYPI.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements - using pyproject.toml instead
def read_requirements():
    # Dependencies are now defined in pyproject.toml
    return []

setup(
    name="levox-cli",
    version="1.0.11",
    author="Levox Team",
    author_email="team@levox.ai",
    description="AI-powered PII/GDPR detection CLI tool. Free for now, paid plans coming soon. Visit levoxserver.vercel.app for details.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/levox/levox",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Text Processing :: Filters",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "ml": [
            "scikit-learn>=1.2.0",
            "tensorflow>=2.12.0",
            "torch>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "levox=levox.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "levox": ["configs/*.json", "configs/*.yaml", "configs/ml_models/*"],
    },
    zip_safe=False,
)
