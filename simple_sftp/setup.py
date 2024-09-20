from setuptools import setup, find_packages

import simple_sftp

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="simple-sftp",
    version=simple_sftp.__version__,
    author="sprumin",
    author_email="sprumin@wellbia.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="Simple way to handle sftp with python",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "simple-sftp-cli=simple_sftp.__main__:main",
        ],
    },
    install_requires=["paramiko"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
