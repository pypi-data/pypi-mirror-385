from setuptools import setup, find_packages

setup(
    name="bitmicro",  # your PyPI package name
    version="1.0.1",  # increment this for new releases
    author="Neoncorp",
    author_email="snurlaelah163@gmail.com",
    description="MicroBitcoin Python library (Bitcash-style)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/COXKPER/bitmicro",  # or your project site
    license="GPLv3",
    packages=find_packages(),
    install_requires=[
        "ecdsa",
        "base58",
        "requests",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
