from setuptools import setup, find_packages
import os

# Read README if it exists
long_description = ""
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "EzDB B-Class - Free & open source vector database for semantic search and AI applications"

setup(
    name="jokerr",
    version="1.0.0",
    description="EzDB B-Class - Free & open source vector database with multimodal support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="EzDB Team",
    author_email="hello@ezdb.io",
    url="https://github.com/utpalraina/ezdb",
    project_urls={
        "Documentation": "https://github.com/utpalraina/ezdb#readme",
        "Source": "https://github.com/utpalraina/ezdb",
        "Bug Tracker": "https://github.com/utpalraina/ezdb/issues",
    },
    packages=find_packages(),
    package_data={
        "ezdb.server": ["static/*"],
    },
    include_package_data=True,
    install_requires=[
        "numpy>=1.24.0",
        "hnswlib>=0.8.0",
    ],
    extras_require={
        "server": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.0.0",
            "python-multipart>=0.0.6",
        ],
        "embeddings": [
            "sentence-transformers>=2.2.0",
        ],
        "clip": [
            "sentence-transformers>=2.2.0",
            "pillow>=10.0.0",
            "requests>=2.31.0",
        ],
        "openai": [
            "openai>=1.0.0",
        ],
        "cohere": [
            "cohere>=4.0.0",
        ],
        "huggingface": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
        ],
        "all": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.0.0",
            "python-multipart>=0.0.6",
            "sentence-transformers>=2.2.0",
            "pillow>=10.0.0",
            "requests>=2.31.0",
        ],
        "full": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.0.0",
            "python-multipart>=0.0.6",
            "sentence-transformers>=2.2.0",
            "openai>=1.0.0",
            "cohere>=4.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ezdb=ezdb.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="vector database, semantic search, embeddings, AI, machine learning, similarity search",
)
