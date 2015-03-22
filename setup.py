# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys

setup(
    name = "Rhona",
    version = '0.1.0',
    packages = find_packages (exclude=['*.test', 'test.*', '*.test.*']),

    cmdclass = {},

    install_requires = ['docutils', 'pygments', 'tornado>=4.1'],
    include_package_data = True,

    author = "Matthäus G. Chajdas",
    author_email = "dev@anteru.net",
    description = "Rhona reStructuredText wiki",
    license = "BSD",
    keywords = [],
    url = "http://shelter13.net/projects/Rhona",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',

    ]
)
