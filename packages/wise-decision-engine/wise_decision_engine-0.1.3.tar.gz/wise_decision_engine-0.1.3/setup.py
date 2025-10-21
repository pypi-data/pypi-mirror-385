"""Setup configuration for wise-decision-engine package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wise-decision-engine",
    version="0.1.3",
    author="Five Acts",
    author_email="dev@five-acts.com",
    description="Uma abstração moderna e inteligente para zen-engine com otimizações avançadas para Spark/Databricks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/five-acts/wise-decision-engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "zen-engine>=0.1.0",
        "pandas>=1.3.0",
        "pyspark>=3.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-mock>=3.0",
            "testcontainers>=3.4.0",
        ],
    },
)