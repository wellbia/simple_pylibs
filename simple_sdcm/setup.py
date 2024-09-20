from setuptools import setup, find_packages

import simple_sdcm

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="simple-sdcm",
    version=simple_sdcm.__version__,
    author="wellbia",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="Simple way to use Microsoft SDCM(Surface Dev Center Manager)",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
