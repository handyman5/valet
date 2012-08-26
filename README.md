Introduction
============
`valet` is a script that turns any directory into a simple wiki, complete with wikitext rendering and automatically committing changes to version control.

It's a single file with no strict requirements aside from [`bottle`](http://bottlepy.org/).

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

Requirements
============
- Python 2.6+
- [`bottle`](http://bottlepy.org/)

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