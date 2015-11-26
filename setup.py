# -*- coding: utf-8 -*-

from setuptools import setup
import re

version = ''
with open('walls.py', 'r') as f:
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
    description='Random Flickr wallpapers.',
    long_description=readme + '\n\n' + history,
    py_modules=['walls'],
    install_requires=[
        'flickrapi',
    ],
    extras_require={
        'testing': [
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'pytest-pep257',
        ],
    },
    entry_points={
        'console_scripts': 'walls=walls:main'
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
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
