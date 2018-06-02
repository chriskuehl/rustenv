# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import setup


with open('README.md') as f:
    long_description = f.read()


setup(
    name='rustenv',
    description='Virtual, activate-able environments for Rust',
    url='https://github.com/chriskuehl/rustenv',
    version='0.0.2',

    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Chris Kuehl',
    author_email='ckuehl@ckuehl.me',

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    py_modules=['rustenv'],
    entry_points={'console_scripts': ['rustenv=rustenv:main']},
)
