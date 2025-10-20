# setup.py

from setuptools import setup, find_packages

setup(
    name="bengali_bpe",
    version="0.1.0",
    description="A Byte Pair Encoding library for the Bengali language.",
    author="Firoj Ahmmed Patwary",
    author_email="firoj.stat@gmail.com",
    url="https://github.com/yourusername/bengali_bpe",  # Update with your repository URL
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here, e.g., "numpy", "regex", etc.
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
        "Natural Language :: Bengali",
    ],
    python_requires='>=3.6',
)
