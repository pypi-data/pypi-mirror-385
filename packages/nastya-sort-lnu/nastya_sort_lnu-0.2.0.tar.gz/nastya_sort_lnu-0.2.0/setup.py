from setuptools import setup, find_packages
import pathlib

# Read version from __init__.py
HERE = pathlib.Path(__file__).parent
version_file = HERE / "nastya_sort" / "__init__.py"
version = {}
with open(version_file, "r", encoding="utf-8") as f:
    exec(f.read(), version)

long_description = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="nastya-sort-lnu",  # Унікальне ім'я для PyPI
    version=version["__version__"],
    description="Simple sort utility implemented in Python with Click",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nastya",
    author_email="nastavasilik1@gmail.com",
    url="https://github.com/Nastia2004/nastya-sort-lnu",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "sort=nastya_sort.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    keywords="sort cli utility unix",
)