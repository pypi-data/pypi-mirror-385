from setuptools import setup, find_packages
import os

# Read README if it exists
long_description = "Official Python SDK for Dudwalls NoSQL Database"
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="dudwalls-python",
    version="1.0.0",
    author="Dudwalls Team",
    author_email="support@dudwalls.com",
    description="Official Python SDK for Dudwalls NoSQL Database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dudwalls/dudwalls-python",
    py_modules=["dudwalls"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="database nosql dudwalls sdk",
)
