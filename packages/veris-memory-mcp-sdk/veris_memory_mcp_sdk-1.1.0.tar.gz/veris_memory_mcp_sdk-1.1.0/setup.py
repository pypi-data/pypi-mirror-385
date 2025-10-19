"""Setup configuration for Veris Memory MCP SDK."""

import os

from setuptools import find_packages, setup


# Read README for long description
def read_readme():
    """Read README.md for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Veris Memory MCP SDK - Production-ready client for the Model Context Protocol"


# Read requirements
def read_requirements():
    """Read requirements from requirements.txt."""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return [
        "httpx>=0.24.0",
        "websockets>=11.0.0",
        "pydantic>=1.10.0,<3.0.0",
        "typing-extensions>=4.0.0",
    ]


setup(
    name="veris-memory-mcp-sdk",
    version="1.1.0",
    description="Production-ready Python SDK for ◎ Veris Memory Model Context Protocol (MCP)",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="◎ Veris Memory Team",
    author_email="credento@credentum.ai",
    url="https://github.com/credentum/veris-memory-mcp-sdk",
    packages=find_packages(exclude=["tests*", "examples*"]),
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "monitoring": [
            "opentelemetry-api>=1.15.0",
            "opentelemetry-sdk>=1.15.0",
            "opentelemetry-exporter-jaeger>=1.15.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
            "opentelemetry-api>=1.15.0",
            "opentelemetry-sdk>=1.15.0",
            "opentelemetry-exporter-jaeger>=1.15.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Networking",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=[
        "mcp",
        "model-context-protocol",
        "veris-memory",
        "context-management",
        "ai",
        "machine-learning",
        "distributed-tracing",
        "async",
        "client-library",
    ],
    project_urls={
        "Documentation": "https://credentum.ai/docs/sdk",
        "Source": "https://github.com/credentum/veris-memory-mcp-sdk",
        "Tracker": "https://github.com/credentum/veris-memory-mcp-sdk/issues",
        "Changelog": "https://github.com/credentum/veris-memory-mcp-sdk/blob/main/CHANGELOG.md",
    },
    include_package_data=True,
    zip_safe=False,
    test_suite="tests",
)
