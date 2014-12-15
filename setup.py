#!/usr/bin/python3

from setuptools import setup

setup(
    name='org_wayround_wsgi',
    version='0.1',
    description='wsgi server realisation',
    author='Alexey Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/org_wayround_wsgi',
    packages=[
        'org.wayround.wsgi'
        ],
    install_requires=[
        'org_wayround_http'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
        ]
    )
