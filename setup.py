#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='explo',
    author='Robin Verton',
    author_email='hello@robinverton.de',
    version='0.1',
    packages=['explo', 'explo.modules'],

    install_requires=[
        'click',
        'requests',
        'pyyaml',
        'pyquery',
        'pystache'
    ],

    entry_points={
        'console_scripts': [
            'explo = explo.core:main',
        ]
    }
)
