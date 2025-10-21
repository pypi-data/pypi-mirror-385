#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="matp",
    version="0.5.1",
    author="Sangeet Sharma",
    author_email="sangeet.music01@gmail.com",
    description="Matryoshka Protocol - Invisible quantum-resistant messaging with enhanced security",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sangeet01/matp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.9",
    install_requires=[
        "cryptography>=41.0.0",
        "liboqs-python==0.10.0",
    ],
    keywords="cryptography steganography encryption messaging security invisible matp",
    project_urls={
        "Bug Reports": "https://github.com/sangeet01/matp/issues",
        "Source": "https://github.com/sangeet01/matp",
    },
)
