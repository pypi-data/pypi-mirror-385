"""
Setup file for SentinelDF Python SDK
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sentineldf",
    version="1.0.0",
    author="Varun Sripad Kota",
    author_email="varunsripadkota@gmail.com",
    description="Official Python SDK for SentinelDF - Data Firewall for LLM Training",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/varunsripad123/sentineldf",
    project_urls={
        "Documentation": "https://docs.sentineldf.com",
        "Source": "https://github.com/varunsripad123/sentineldf",
        "Bug Reports": "https://github.com/varunsripad123/sentineldf/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="llm security prompt-injection data-poisoning ai-safety machine-learning",
)
