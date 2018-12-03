# -*- coding: utf-8 -*-
"""setup.py"""
from setuptools import setup, find_packages

with open("README.md") as f:
    README = f.read()

with open("LICENSE") as f:
    LICENSE = f.read()

setup(
    name="dataland",
    version="1.1.1",
    description="A jutsu of data style",
    long_description=README,
    author="Sourcepirate",
    author_email="plasmashadowx@gmail.com",
    url="https://github.com/sourcepirate/datastyle.git",
    license=LICENSE,
    packages=find_packages(exclude=("tests", "docs")),
    install_requires=[
        "aiohttp==3.4.4",
        "untangle==1.1.1",
        "beautifulsoup4==4.6.3",
        "selenium==3.141.0",
    ],
    test_suite="tests",
)
