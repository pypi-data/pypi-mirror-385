"""Setup configuration for DinoX API Python client."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dinox-api",
    version="0.1.0",
    author="JimEverest",
    author_email="",  # Add your email if desired
    description="Python client for DinoX API - A note-taking and knowledge management system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JimEverest/DinoSync",
    py_modules=["dinox_client"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: News/Diary",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "httpx>=0.24.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "tenacity>=8.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/JimEverest/DinoSync/issues",
        "Source": "https://github.com/JimEverest/DinoSync",
        "Documentation": "https://github.com/JimEverest/DinoSync/blob/main/README.md",
    },
)
