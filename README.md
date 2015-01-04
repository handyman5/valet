Introduction
============
`valet` is a script that turns any directory into a simple wiki, complete with wikitext rendering, editing, and automatically committing changes to version control.

It's a single file with no strict requirements aside from [`bottle`](http://bottlepy.org/).

News
====
2015-01-03
----------
I got a bee in my bonnet recently on making some improvements to `valet`, so Merry Christmas to you all.

New features:

- The `/view/X`, `/edit/X`, etc. paths have been removed in favor of using URL query arguments, e.g. `X?edit` and `X?delete`. CGI/WSGI path prefixes still work fine.
- New file-management-related functionality, like creating new files and deleting files
- Search! A fancy search field will grep through documents and filenames for your query
- Lots of git-related functionality has been added, including:
    - Displaying a dropdown that lets you view an old version of a file
    - Displaying a table with detailed status about the last few changes to a file
- Lots of code cleanup, refactoring, and simplification
- Fixed a ton of bugs
- Lots of code changes to better comply with pylint (score 9.24)
- Added some basic unit/regression tests in `tests.py`

2012-10-28
----------
I spent some time hacking on `valet` this weekend, fixing a few bugs and adding one big new feature: CGI/WSGI support. Now if you link or rename `valet` to `something.cgi` or `something.fcgi`, it will "Do The Right Thing" and operate as a proper webapp. (WSGI support requires [`flup`](http://trac.saddi.com/flup).)

This feature was required for me to run `valet` as a lightweight wiki on my DreamHost server without interfering in that environment by opening a new port or leaving a long-running service around. I didn't add a configuration interface; if you're going to be linking or renaming the script, open it up and change the options hard-coded near the top.

Other changes and new features:

- Added a `mime` query argument to override the automatic filetype detection.
    - You can use this if, for instance, you have a Python script without the ".py" extension; add `?mime=text/x-python` to get it properly syntax-colored anyway.
- Added support for arbitrary URL prefixes.
    - This just works automatically; `valet` will figure out where you put it and prepend that to all of the links instead of hardcoding "/view" etc.
	- This doesn't work super-well with Apache's `mod_rewrite`; it basically ignores the rewrite headers. This is a limitation of `bottle` but I'm not sure how to do it better anyway.

Fixes:

- Added proper support for empty "edit" and "post" routes with a slash at the end (now it will complain about no file being provided instead of saying the route doesn't exist)
- Fixed an error output that caused problems when running as a CGI (now writes to stderr)

Usage
=====

    $ valet

Or, use some command line options:

    $ valet [-d <path>] [-p <port>] [-r] [-s] [-v]

By default, `valet` serves `$CWD`; change this with `-d <path>`.
Other options:

- `-r`: set readonly mode and disable editing
- `-s`: set simple mode and disable all special-case processing (pygments, wikitext rendering, etc.)
- `-v`: automatically commit edits into version control if possible
    - Currently only git is supported.

Installation
============

    $ pip install valet

Requirements
============
- Python 2.6+
- [`bottle`](http://bottlepy.org/)

Tested on:

- Centos 5.4 (python 2.6)
- Debian 6.0.4 (python 2.6)
- Gentoo (python 2.7)
- Mac OS X 10.7 (python 2.7)
- Ubuntu 12.04.1 (python 2.7)
- Windows 7 (python 2.7)

Optional Components
===================
`valet` supports lots of useful modules, which will be automatically enabled if present:

- [`python-magic`](http://pypi.python.org/pypi/python-magic/): Better automatic file type detection
- [`Markdown`](http://pypi.python.org/pypi/Markdown/): Render "markdown" wikitext in files
- [`python-creole`](http://pypi.python.org/pypi/python-creole/): Render "creole" wikitext in files
- [`textile`](http://pypi.python.org/pypi/textile): Render "textile" wikitext in files
- [`docutils`](http://pypi.python.org/pypi/docutils/): Render "reStructuredText" wikitext in files
- [`pygments`](http://pypi.python.org/pypi/Pygments): Adds syntax highlighting for source code files

Use the `-s`/`--simple` command-line option to disable these optional components.

Known Issues
============
- There's no security anywhere here; please, whatever you do, DON'T make this available over the Internet. `valet` has a readonly mode and attempts to jail reads and edits into its root directory, but be careful!
- `bottle`'s `static_file` function doesn't appear to handle UTF-8 data properly, or at least it doesn't show up right when I load a file that way.
- The version of `python-magic` that ships with Ubuntu [is broken](https://bugs.launchpad.net/bugs/603128); I worked around it as best I could.
