#!/usr/bin/env python3
"""Setup script for CovetPy web framework"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="covet",
    version="0.1.0a1",  # Alpha release
    author="vipin08",
    author_email="vipin@buffercode.in",
    description="A lightweight Python web framework with Flask-like simplicity and Django-like ORM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/covetpy/covet",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    install_requires=[
        "uvicorn>=0.20.0",
        "bcrypt>=4.0.0",
        "PyJWT>=2.8.0",
        "python-multipart>=0.0.5",
        "aiofiles>=23.0.0",
        "jinja2>=3.1.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "postgres": [
            "asyncpg>=0.27.0",
            "psycopg2-binary>=2.9.0",
        ],
        "mysql": [
            "aiomysql>=0.1.0",
            "PyMySQL>=1.0.0",
        ],
        "redis": [
            "redis>=4.5.0",
            "aioredis>=2.0.0",
        ],
        "all": [
            "asyncpg>=0.27.0",
            "psycopg2-binary>=2.9.0",
            "aiomysql>=0.1.0",
            "PyMySQL>=1.0.0",
            "redis>=4.5.0",
            "aioredis>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "covet=covet.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/covetpy/covet/issues",
        "Source": "https://github.com/covetpy/covet",
        "Documentation": "https://covetpy.readthedocs.io",
    },
)
