"""
Setup script for ABTK (A/B Testing Toolkit).
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="abtk",
    version="0.2.0",
    author="Alexei Veselov",
    author_email="alexeiveselov92@gmail.com",
    description="A/B Testing Toolkit - Statistical analysis library for A/B tests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexeiveselov92/abtk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "viz": [
            "matplotlib>=3.5.0",
        ],
    },
    keywords="ab-testing statistics hypothesis-testing experimentation analytics",
    project_urls={
        "Bug Reports": "https://github.com/alexeiveselov92/abtk/issues",
        "Source": "https://github.com/alexeiveselov92/abtk",
        "Documentation": "https://github.com/alexeiveselov92/abtk/blob/main/docs/README.md",
    },
)
