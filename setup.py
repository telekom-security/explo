#!/usr/bin/env python
from setuptools import setup

setup(
    name = 'explo',
    author = 'Robin Verton',
    author_email = 'hello@robinverton.de',
    version = '0.1',
    packages = ['explo', 'explo.modules'],
    install_requires = [
        'click',
        'requests',
        'pyyaml',
        'colorama',
        'pyquery'
    ]
)
