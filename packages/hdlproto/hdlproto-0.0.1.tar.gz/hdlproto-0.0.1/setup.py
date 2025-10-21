# setup.py
from setuptools import setup, find_packages

setup(
    name="hdlproto",
    version="0.0.1",
    description="A Python-based HDL design prototyping framework for circuit simulation and verification",
    long_description="Placeholder package - under development",
    author="shntn",
    author_email="shntn@users.noreply.github.com",
    url="https://github.com/shntn/hdlproto",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
