from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="chronomap",
    version="2.0.2",
    author="Devansh Singh",
    description="Thread-safe, time-versioned key-value store with snapshots and diffs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Devansh-567/chronomap",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
