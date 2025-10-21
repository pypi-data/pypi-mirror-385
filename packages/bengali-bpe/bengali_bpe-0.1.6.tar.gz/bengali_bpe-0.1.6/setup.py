#setup.py

from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for PyPI long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="bengali_bpe",
    version="0.1.6",  # ⬅️ bump version number
    description="A Byte Pair Encoding (BPE) library for the Bengali language.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # ⬅️ for Markdown rendering
    author="Firoj Ahmmed Patwary",
    author_email="firoj.stat@gmail.com", 
    url="https://github.com/firojap/bengali_bpe",  
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
