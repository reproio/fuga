#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'Click>=6.0',
    'google-cloud-resource-manager~=0.29.1',
    'google-cloud-storage~=1.18.0',
    'cookiecutter~=1.6.0',
    'GitPython~=2.1.11',
    'pyyaml~=4.2b1',  # pyyaml<=4.2 has a severe vulnerability
    'docker~=4.0.2']

setup_requirements = []

test_requirements = []

setup(
    author="Yuichiro Someya",
    author_email='me@ayemos.me',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Fuga - Helper toolset for Google Cloud Cimposer",
    entry_points={
        'console_scripts': [
            'fuga=fuga.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='fuga',
    name='fuga',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ayemos/fuga',
    version='0.1.2',
    zip_safe=False,
)
