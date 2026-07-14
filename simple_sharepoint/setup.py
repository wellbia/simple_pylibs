from setuptools import setup, find_packages

import simple_sharepoint

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="simple-sharepoint",
    version=simple_sharepoint.__version__,
    author="Wellbia.com Co.,Ltd.",
    author_email="opensource@wellbia.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="Simple way to handle sharepoint with python",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "simple-sharepoint-cli=simple_sharepoint.__main__:main",
        ],
    },
    install_requires=[
        "cryptography==49.0.0",
        "msal==1.37.0",
        "requests==2.34.2",
    ],
    python_requires=">=3.10",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)
