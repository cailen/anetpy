#!/usr/bin/env python
import anetpy

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(filename):
    return open(filename).read()

setup(
    name="anetpy",
    version=anetpy.__version__,
    description="Python client for the Atlantic.Net Cloud API",
    long_description=read("README.rst"),
    author="Derek Wiedenhoeft",
    author_email="derek@derekdesignsorlando.com",
    maintainer="Derek Wiedenhoeft",
    maintainer_email="derek@derekdesignsorlando.com",
    url="https://github.com/devo-ps/dopy",
    download_url="https://github.com/devo-ps/dopy/archive/master.zip",
    classifiers=("Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2.6",
                 "Programming Language :: Python :: 2.7"),
    license=read("LICENSE"),
    packages=['anetpy'],
    install_requires=["requests >= 1.0.4", "six >= 1.9.0"],
)
