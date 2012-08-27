#!/usr/bin/env python
#coding: utf-8

from distutils.core import setup

setup(
	name = "valet",
	author = "Adam Compton",
	author_email = "comptona@gmail.com",
	version = "0.1",
	license = "BSD-2-Clause",
	url = "https://github.com/handyman5/valet",
	download_url = "https://github.com/handyman5/valet/tarball/master",
	description = "valet is a script that turns any directory into a simple wiki, complete with wikitext rendering and automatically committing changes to version control.",
        install_requires = ['bottle'],
	scripts = ['valet']
)