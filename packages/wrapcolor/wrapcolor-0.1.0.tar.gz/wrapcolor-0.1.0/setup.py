from setuptools import setup, find_packages
import pathlib

README = (pathlib.Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="wrapcolor",
    version="0.1.0",
    description="Universal ANSI colorizer for Python (8/16 colors, 256-color, RGB, styles)",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Bohdan",
    author_email="datcukbogdan@gmail.com",
    url="https://github.com/datsiuk7/wrapcolor",
    project_urls={
        "Homepage": "https://github.com/datsiuk7/wrapcolor",
        "Source": "https://github.com/datsiuk7/wrapcolor",
        "Issues": "https://github.com/datsiuk7/wrapcolor/issues",
    },
    license="MIT",
    license_files=["LICENSE"],
    packages=find_packages(include=["wrapcolor", "wrapcolor.*"]),
    include_package_data=False,
    keywords=["ansi", "color", "terminal", "console", "rgb", "xterm-256", "styles"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Terminals",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "colorama": ["colorama>=0.4.6"],
        "dev": ["build>=1.2.1", "twine>=5.0.0", "pytest>=8.0.0"],
    },
)