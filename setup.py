#!/usr/bin/python3

from setuptools import setup

setup(
    name='wayround_i2p_wsgi',
    version='0.7',
    description='wsgi server realisation',
    author='Alexey Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_i2p_awsgi',
    packages=[
        'wayround_i2p.wsgi'
        ],
    install_requires=[
        'wayround_i2p_http'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
        ]
    )
