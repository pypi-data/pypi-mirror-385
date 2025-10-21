#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

PACKAGE = "ctyunsdk_elb20220909"
NAME = "ctyunsdk_elb20220909" or "ctyun-python-sdk-elb"
DESCRIPTION = "CTYun ELB (2022-09-09) SDK Library for Python"
AUTHOR = "Ctyun Cloud SDK"
AUTHOR_EMAIL = "ctyunsdk@chinatelecom.cn"
URL = "https://github.com/ctyunsdk/ctyun-python-sdk.git"
LONG_DESCRIPTION = "CTYun ELB (2022-09-09) SDK Library for Python"
if os.path.exists("README.rst"):
    with open("README.rst", encoding="utf-8") as fh:
        LONG_DESCRIPTION = fh.read()

setup(
    name=NAME,
    version="1.0.0",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    keywords=["ctyunsdk", "elb20220909"],
    packages=find_packages(include=['ctyunsdk_elb20220909', 'ctyunsdk_elb20220909.*'], exclude=["ctyunsdk_elb20220909.tests","ctyunsdk_elb20220909.tests.*"]),
    include_package_data=True,
    platforms="any",
    python_requires='>=3.9',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[
        'setuptools',
        "requests>=2.25.0",
    ]
)
