#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="kkutils",
    version="1.8.2",
    description="python utils",
    author="digua",
    author_email="digua@gmail.com",
    url="https://www.github.com",
    license="MIT",
    python_requires='>=3.6',
    data_files=[('', ['requirements.txt'])],
    install_requires=[line.strip() for line in open('requirements.txt') if not line.strip().startswith('#')],
    include_package_data=True,
    extras_require={'curl': ['pycurl']},
    py_modules=['processor'],
    packages=['tornado_utils', 'utils'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
)
