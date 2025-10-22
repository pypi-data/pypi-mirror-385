"""Setup file for the medisearch_client package."""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="medisearch_client",
    version="0.3.17",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
        "rich>=10.0.0",  # Required for test client
        "urllib3>=1.26.0",
        "typing-extensions>=4.0.0",  # For Python <3.8 compatibility
    ],
    extras_require={
        "test": [
            "rich>=10.0.0",
            "pytest>=6.0.0",
            "pytest-asyncio>=0.14.0",
            "pytest-timeout>=2.0.0",
        ],
        "dev": [
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
            "pylint>=2.8.0",
        ],
    },
    python_requires=">=3.7",
    author="Michal Pandy",
    author_email="founders@medisearch.io",
    description="A Python client for the MediSearch medical information API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MediSearch/medisearch_client_python",
    project_urls={
        "Documentation": "https://docs.medisearch.io",
        "Source": "https://github.com/MediSearch/medisearch_client_python",
        "Issues": "https://github.com/MediSearch/medisearch_client_python/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="medical, healthcare, api, search, research, medisearch",
)
