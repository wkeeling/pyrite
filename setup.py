#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    author="Will Keeling",
    author_email='will@zifferent.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A lightweight text editor written in Python using Tkinter",
    install_requires=['ttkthemes>=3.1.1'],
    license="MIT",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pyrite',
    name='pyrite',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    setup_requires=[],
    test_suite='pytest',
    tests_require=['pytest>=6.1.2'],
    url='https://github.com/wkeeling/pyrite',
    version='0.0.1',
    zip_safe=False,
    entry_points={
        'console_scripts': ['pyrite=pyrite.__main__:main']
    },
)
