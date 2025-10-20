#setup.py

from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for PyPI long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="bengali_bpe",
    version="0.1.2",  # ⬅️ bump version number (PyPI doesn't allow re-upload of same version)
    description="A Byte Pair Encoding (BPE) library for the Bengali language.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # ⬅️ important for Markdown rendering
    author="Firoj Ahmmed Patwary",
    author_email="your.email@example.com",  # optional
    url="https://github.com/yourusername/bengali_bpe",  # or your site
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Bengali",
    ],
    python_requires='>=3.6',
)
