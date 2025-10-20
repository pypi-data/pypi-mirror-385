"""
WATBOT - WhatsApp & Instagram Automation Bot with AI-powered responses
"""
from setuptools import setup, find_packages
import os
from typing import List

def read_requirements(filename: str) -> List[str]:
    """Read requirements from file, filtering comments and empty lines"""
    with open(filename, 'r', encoding='utf-8') as f:
        return [
            line.strip() 
            for line in f
            if line.strip() and not line.startswith('#')
        ]

def read_file(filename: str) -> str:
    """Read file contents, try both cases if not found"""
    try:
        # Try exact filename first
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Try lowercase
        try:
            with open(filename.lower(), 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Try uppercase
            try:
                with open(filename.upper(), 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                print(f"Warning: Could not find {filename} in any case variation, using empty string")
                return ""

# Core setup configuration
setup(
    name="watbot",
    version="0.1.1",
    author="Nithin Jambula",
    author_email="nithin@example.com",
    description="WhatsApp & Instagram Automation Bot with AI-powered responses",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    
    # Project URLs
    url="https://github.com/nithin434/woat",
    project_urls={
        "Bug Tracker": "https://github.com/nithin434/woat/issues",
        "Documentation": "https://github.com/nithin434/woat/wiki",
        "Source Code": "https://github.com/nithin434/woat",
    },
    
    # Package configuration
    packages=find_packages(include=['watbot', 'watbot.*']),
    include_package_data=True,
    
    # Dependencies
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-asyncio>=0.21.1',
            'pytest-cov>=3.0',
            'black>=22.0',
            'flake8>=4.0',
            'mypy>=0.950',
        ],
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    
    # Entry points
    entry_points={
        "console_scripts": [
            "watbot=watbot.cli:main",
        ],
    },
    
    # Package Keywords
    keywords=[
        "whatsapp", "instagram", "bot", "automation", 
        "ai", "chat", "messaging", "api"
    ],
)
