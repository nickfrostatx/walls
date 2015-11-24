# -*- coding: utf-8 -*-

from setuptools import setup
import re

version = ''
with open('walls/__init__.py', 'r') as f:
    version = re.search(r'__version__\s*=\s*\'([\d.]+)\'', f.read()).group(1)

with open('README.rst') as f:
    readme = f.read()

with open('HISTORY.rst') as f:
    history = f.read()

setup(
    name='walls',
    version=version,
    author='Nick Frost',
    author_email='nickfrostatx@gmail.com',
    url='https://github.com/nickfrostatx/walls',
    description='Random flickr wallpapers.',
    long_description=readme + '\n\n' + history,
    packages=['walls'],
    install_requires=[],
    extras_require={
        'testing': [
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'pytest-pep257',
        ],
    },
    license='MIT',
    keywords='walls',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
