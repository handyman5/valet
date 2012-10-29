#!/usr/bin/env python
#coding: utf-8

from distutils.core import setup

setup(
        name = "valet",
        author = "Adam Compton",
        author_email = "comptona@gmail.com",
        version = "0.3",
        license = "BSD-2-Clause",
        url = "https://github.com/handyman5/valet",
        download_url = "https://github.com/handyman5/valet/tarball/master",
        description = "valet is a script that turns any directory into a simple wiki, complete with wikitext rendering, editing, and automatically committing changes to version control.",
        install_requires = ['bottle'],
        scripts = ['valet'],
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'License :: OSI Approved :: BSD License',
            'Operating System :: Unix',
            'Development Status :: 5 - Production/Stable',
            'Environment :: No Input/Output (Daemon)'
        ]
)
