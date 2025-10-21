from setuptools import setup, find_packages
import io
import os

# Safely read the long description from README.md
def read_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    try:
        with io.open(readme_path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

setup(
    name="semverish",
    version="1.0.0",
    author="Al Arafat Tanin",
    author_email="arafat.rng70@gmail.com",
    description=(
        "Python wrapper around Go module `github.com/rng70/versions` "
        "for parsing and sorting semver and non-semver-ish versions and constraints."
    ),
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/rng70/versions",
    project_urls={
        "Bug Tracker": "https://github.com/rng70/versions/issues",
        "Source": "https://github.com/rng70/versions",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Go",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(exclude=("tests*", "docs*")),
    include_package_data=True,
    package_data={
        "semverish": ["libpyversions.so"],
    },
    install_requires=[
        "cffi>=1.15.0",
    ],
    python_requires=">=3.8",
    zip_safe=False,
)
