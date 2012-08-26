#!/usr/bin/env python

from bottle import SimpleTemplate, abort, post, redirect, request, response, route, run, static_file
from optparse import OptionParser
import StringIO
import mimetypes
import os
import os.path

###
# Global constants
###
root = os.getcwd()
simple = False

###
# Optional filetype support for wikitext rendering
###
# using the magic byte-marker file to determine types
try:
    from magic import Magic
except ImportError:
    Magic = None
# markdown
try:
    import markdown
    mimetypes.add_type('text/x-markdown', '.md')
    mimetypes.add_type('text/x-markdown', '.markdown')
except ImportError:
    markdown = None
# creole
try:
    import creole
    mimetypes.add_type('text/x-creole', '.creole')
except ImportError:
    creole = None
# textile
try:
    import textile
    mimetypes.add_type('text/x-textile', '.textile')
except ImportError:
    textile = None
# rst
try:
    import docutils.core as docutils
    mimetypes.add_type('text/x-restructured-text', '.rst')
except ImportError:
    docutils = None
# pygments
try:
    import pygments
    from pygments import highlight
    from pygments.lexers import get_lexer_for_filename, get_lexer_for_mimetype
    from pygments.formatters import HtmlFormatter
    from pygments.util import ClassNotFound
    from pygments.styles import get_style_by_name
except ImportError:
    pygments = None

# Add some other common file extensions mimetypes either doesn't support or handles wrong
mimetypes.add_type('application/x-perl', '.pl')
mimetypes.add_type('text/x-csrc', '.c')
mimetypes.add_type('text/x-chdr', '.h')
mimetypes.add_type('text/plain', '.org')

###
# Helpers for handling wikitext renderers
###
class ContentReadyException(Exception):
    def __init__(self, content, ctype='text/html', style=''):
        self.content = content
        self.ctype = ctype
        self.style = style

# Ensure a passed path is valid and inside the jail
def check_path(short_path):
    if not short_path: short_path = root
    full_path = os.path.join(root, short_path)
    if not os.path.abspath(full_path).startswith(root):
        abort(401, "Access denied; path outside of jail.")
    if not os.path.exists(full_path):
        abort(404, "Please specify a valid filename.")
    return full_path

# Figure out the MIME type of a file if at all possible
def discern_type(path):
    t = mimetypes.guess_type(path, strict=False)[0]
    if not t and Magic:
        t = Magic(mime=True).from_file(path)
    return t

# Handle various special-case MIME types (directories, links, pygments, etc.)
def dispatch(ctype, path):
    if ctype == 'inode/symlink':
        realpath = os.path.abspath(os.readlink(path))
        if not os.path.abspath(realpath).startswith(root):
            abort(401, "Access denied; path outside of jail.")
        else:
            dispatch(discern_type(realpath), realpath)
    elif ctype == 'inode/directory':
        raise ContentReadyException(render_dir(path))
    elif ctype == 'inode/x-empty':
        raise ContentReadyException("<I>(empty file)</I>")
    elif ctype == 'text/html':
        pass

    if not simple:
        if markdown and ctype == 'text/x-markdown':
            output = StringIO.StringIO()
            dirname = os.path.dirname(os.path.relpath(path, root))
            md = markdown.markdownFromFile(
                path, output=output,
                extensions=['wikilinks', 'codehilite'],
                extension_configs = {'wikilinks': [
                    ('base_url', '/view/%s/' % dirname),
                    ('end_url',  '.md')]})
            output.seek(0)
            raise ContentReadyException(output.read().decode('utf-8'))
        elif creole and ctype == 'text/x-creole':
            with open(path) as f:
                data = f.read().decode('utf8')
                raise ContentReadyException(creole.creole2html(data))
        elif textile and ctype == 'text/x-textile':
            with open(path) as f:
                data = f.read().decode('utf8')
                raise ContentReadyException(textile.textile(data, auto_link=True))
        elif docutils and ctype == 'text/x-restructured-text':
            with open(path) as f:
                data = f.read().decode('utf8')
                raise ContentReadyException(docutils.publish_string(data, writer_name='html'))
        elif pygments:
            try:
                lexer = get_lexer_for_mimetype(ctype)
                if isinstance(lexer, pygments.lexers.TextLexer):
                    lexer = get_lexer_for_filename(path)
                formatter = HtmlFormatter(style='default')
                with open(path) as f:
                    data = f.read().decode('utf-8')
                    result = highlight(data, lexer, formatter)
                    raise ContentReadyException(result, 'text/html',
                                                style=formatter.get_style_defs())
            except ClassNotFound as e:
                print "no lexer found"
                pass

###
# Rendering helpers
###
def render_navbar(path):
    path_parts = os.path.relpath(path, root).split('/')
    path_stack = []
    crumbs = []

    for p in path_parts:
        if p == '.': continue
        path_stack.append(p)
        crumbs.append(('/'.join(path_stack), p))

    crumbs.insert(0, ('', '<I>Home</I>'))

    output = []
    for (p, l) in crumbs[0:-1]:
        output.append("<A HREF='/view/%s'>%s</A>" % (p, l))
    output.append(crumbs[-1][1])
    return ' > '.join(output)

def render_edit_link(path):
    return "&nbsp;<A CLASS='link' HREF='/edit/%s'>e</A>" % os.path.relpath(path, root)

def render_raw_link(path):
    return "&nbsp;<A CLASS='link' HREF='/view/%s?raw'>r</A>" % os.path.relpath(path, root)

def render_dir(path):
    output = '<UL>'
    for f in os.listdir(path):
        if f in ['.git', '.svn', '.hg', 'CVS']: continue
        rpath = os.path.relpath(path, root)
        pjoin = os.path.join(rpath, f)
        output += "<LI><A HREF='/view/%s'>%s</A></LI>\n" % (pjoin, f)
    output += '</UL>'
    return output

###
# Build standard page template
###
template = SimpleTemplate("""<HTML><HEAD><TITLE>{{path}}</TITLE>
<STYLE>{{style}}
.navbar { display: inline-block; border: solid 3px gray; border-top: 0px; padding-left: 2px; padding-right: 2px; float: left; }
.navlink { float: right; }
</STYLE></HEAD>
<BODY>
<DIV STYLE='display: inline-block;'>
<DIV CLASS='navbar'>{{!render_navbar(path)}}</DIV>
<DIV CLASS='navlink'>{{!render_raw_link(path)}}</DIV>
<DIV CLASS='navlink'>{{!render_edit_link(path)}}</DIV>
</DIV>
<DIV CLASS='main'>
{{!body}}
</DIV></BODY></HTML>
""")
template.defaults.update({'style': '', 'body': ''})
template.defaults.update(locals())

###
# Routes
###
@route('/')
def redirect_root():
    redirect('/view/')

@route('/view')
@route('/view/<short_path:path>')
def view(short_path=None):
    full_path = check_path(short_path)
    ctype = discern_type(full_path)
    try:
        if 'raw' in request.query:
            if not os.path.isdir(full_path):
                return static_file(os.path.basename(full_path), os.path.dirname(full_path))
        dispatch(ctype, full_path)
        if ctype.startswith('text/'):
            with open(full_path, 'rb') as data:
                body = u"<PRE>%s</PRE>" % data.read().decode('utf8')
                return template.render(path=full_path, body=body)
        else:
            return static_file(os.path.basename(full_path), os.path.dirname(full_path))
    except ContentReadyException as c:
        response.content_type="%s; charset=utf-8" % c.ctype
        return template.render(path=full_path, style=c.style, body=c.content)

@route('/edit')
@route('/edit/<short_path:path>')
def edit(short_path=None):
    full_path = check_path(short_path)
    ctype = discern_type(full_path)
    if not (ctype.startswith('text/') or ctype in ['application/xml']):
        abort(403, 'Not an editable file type')
    with open(full_path) as data:
        output = "<FORM METHOD='POST' ACTION='/post/%s' ENCTYPE='multipart/form-data'>" % short_path
        output += "<INPUT TYPE='submit'><INPUT TYPE='button' VALUE='Cancel' onclick='window.location = \"/view/%s\"'><BR>" % short_path
        output += "<TEXTAREA NAME='data' ROWS=50 COLS=100>"
        output += data.read()
        output += "</TEXTAREA></FORM>"
    return template.render(path=full_path, body=output)

@post('/post/<short_path:path>')
def post(short_path=None):
    full_path = check_path(short_path)
    with open(full_path, 'wb') as handle:
        handle.write(request.forms.get('data'))
    redirect('/view/%s' % short_path)


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [<options>]")
    parser.add_option("-d", "--directory", action="store", dest="root",
                      default=os.getcwd(), help="Directory to serve (defaults to $CWD)")
    parser.add_option("-r", "--readonly", action="store_true", dest="readonly",
                      help="Make the website read-only")
    parser.add_option("-p", "--port", action="store", dest="port",
                      default=9876, type=int, help="Port number to use (defaults to 9876)")
    parser.add_option("-s", "--simple", action="store_true", dest="simple",
                      help="Disables all special-case processing (wikitext rendering, pygments syntax coloring, etc.)")
    (options,args) = parser.parse_args()
    root = os.path.abspath(options.root)
    simple = options.simple

    run(host='0.0.0.0', port=options.port, reloader=True)
