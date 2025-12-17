#!/usr/bin/env python3
"""Setup script for Call Blocker."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="callblocker",
    version="1.0.0",
    author="maryfield",
    description="Sistema di blocco chiamate telefoniche indesiderate su linee PSTN analogiche",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maryfield/callblocker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Telephony",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyserial>=3.5",
    ],
    entry_points={
        "console_scripts": [
            "callblockerd=callblocker.daemon:main",
            "callblocker-cli=callblocker.cli:main",
        ],
    },
)
