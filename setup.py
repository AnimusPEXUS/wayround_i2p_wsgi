#!/usr/bin/python3

from setuptools import setup

setup(
    name='wayround_org_wsgi',
    version='0.2',
    description='wsgi server realisation',
    author='Alexey Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_org_wsgi',
    packages=[
        'wayround_org.wsgi'
        ],
    install_requires=[
        'wayround_org_http'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
        ]
    )
