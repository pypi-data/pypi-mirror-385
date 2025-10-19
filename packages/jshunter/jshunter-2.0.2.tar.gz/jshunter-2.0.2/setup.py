#!/usr/bin/env python3
"""
Setup script for JSHunter - High-Performance JavaScript Security Scanner
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "High-Performance JavaScript Security Scanner with TruffleHog integration"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "jshunter", "cli", "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return [
        "aiohttp>=3.8.0",
        "aiofiles>=23.0.0", 
        "requests>=2.28.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "jinja2>=3.0.0",
        "python-multipart>=0.0.5"
    ]

setup(
    name="jshunter",
    version="2.0.2",
    author="iamunixtz",
    author_email="iamunixtz@example.com",
    description="High-Performance JavaScript Security Scanner - Process 1M URLs in ~5 hours with Telegram & Discord bot integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/iamunixtz/JsHunter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "jshunter=jshunter.cli.jshunter:main",
            "jshunter-web=jshunter.web.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "jshunter": [
            "cli/requirements.txt",
            "web/templates/*",
            "web/static/*",
        ],
    },
    keywords="security, javascript, scanner, trufflehog, secrets, api-keys, tokens, high-performance, parallel-processing",
    project_urls={
        "Bug Reports": "https://github.com/iamunixtz/JsHunter/issues",
        "Source": "https://github.com/iamunixtz/JsHunter",
        "Documentation": "https://github.com/iamunixtz/JsHunter#readme",
    },
)
