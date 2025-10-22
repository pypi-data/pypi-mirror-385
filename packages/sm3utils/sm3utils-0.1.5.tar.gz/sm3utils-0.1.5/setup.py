# -*- coding: utf-8 -*-
import os
from io import open
from setuptools import setup
from distutils.core import Extension
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires = [x.strip() for x in fobj.readlines() if x.strip()]


setup(
    name="sm3utils",
    version="0.1.5",
    description="SM3 Cryptographic Hash Algorithm.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="rRR0VrFP",
    maintainer="rRR0VrFP",
    license="Apache License, Version 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["sm3"],
    install_requires=requires,
    packages=find_packages(".", exclude=["tests"]),
    ext_modules=[Extension("_sm3", ["sm3utils/bind.c", "sm3utils/sm3.c"])],
    zip_safe=False,
    include_package_data=True,
)
