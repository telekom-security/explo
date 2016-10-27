#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='explo',
    author='Robin Verton',
    author_email='hello@robinverton.de',
    version='0.1',
    description='Test web based vulnerabilities from a .yaml file',
    packages=['explo', 'explo.modules'],
    url='https://github.com/dtag-dev-sec/explo',
    platforms='any',
    install_requires=[
        'requests',
        'pyyaml',
        'pyquery',
        'pystache',
        'eliot',
        'six'
    ],

    entry_points={
        'console_scripts': [
            'explo = explo.core:main',
        ]
    }
)
