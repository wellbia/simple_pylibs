from setuptools import setup, find_packages

import simple_ip_tools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="simple-ip-tools",
    version=simple_ip_tools.__version__,
    author="hgyoon",
    author_email="hgyoon@wellbia.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="A simple IP address to country mapping tool",
    packages=find_packages(),
    install_requires=["pytricia", "ipaddress"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
