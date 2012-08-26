#!/usr/bin/env python

from magic import Magic
import os
import os.path
from bottle import route, response, run, redirect
import mimetypes
import StringIO
from optparse import OptionParser

# optional type support
### markdown
try:
    import markdown
    mimetypes.types_map['.md'] = 'text/x-markdown'
    mimetypes.types_map['.markdown'] = 'text/x-markdown'
except ImportError:
    markdown = None
# creole
try:
    import creole
    mimetypes.types_map['.creole'] = 'text/x-creole'
except ImportError:
    creole = None
# textile
try:
    import textile
    mimetypes.types_map['.textile'] = 'text/x-textile'
except ImportError:
    textile = None
# rst
try:
    import docutils.core as docutils
    mimetypes.types_map['.rst'] = 'text/x-restructured-text'
except ImportError:
    docutils = None
### pygments
try:
    import pygments
    from pygments import highlight
    from pygments.lexers import get_lexer_for_mimetype
    from pygments.formatters import HtmlFormatter
    from pygments.util import ClassNotFound
    from pygments.styles import get_style_by_name
except ImportError:
    pygments = None

# support other common file extensions
mimetypes.types_map['.org'] = 'text/org'
mimetypes.types_map['.pl'] = 'application/x-perl'
mimetypes.types_map['.c'] = 'text/x-csrc'
mimetypes.types_map['.h'] = 'text/x-chdr'

# build page template
template = """<HTML><HEAD><TITLE>%(title)s</TITLE>
<STYLE>%(style)s
.navbar { display: inline-block; border-bottom: solid 3px gray; border-right: solid 3px gray; padding-right: 2px; }
</STYLE></HEAD>
<BODY>
<DIV CLASS='navbar'>%(nav)s</DIV>
<DIV CLASS='main'>%(body)s</DIV>
<!-- template --></BODY></HTML>
"""

root = os.getcwd()

class ContentReadyException(Exception):
    def __init__(self, content, ctype='text/html', style=""):
        self.content = content
        self.ctype = ctype
        self.style = style
    def __str__(self):
        return self.content


def discern_type(path):
    t = mimetypes.guess_type(path)[0]
    if not t:
        m = Magic(mime=True)
        t = m.from_file(path)
    return t

def dispatch(ctype, path):
    if ctype == "text/x-c":
        ctype = "text/x-csrc"


    if ctype == "text/x-markdown":
        output = StringIO.StringIO()
        md = markdown.markdownFromFile(path, output=output)
        output.seek(0)
        raise ContentReadyException(output.read())
    elif creole and ctype == "text/x-creole":
        with open(path) as f:
            data = f.read().decode('utf8')
            raise ContentReadyException(creole.creole2html(data))
    elif textile and ctype == "text/x-textile":
        with open(path) as f:
            data = f.read().decode('utf8')
            raise ContentReadyException(textile.textile(data))
    elif docutils and ctype == "text/x-restructured-text":
        with open(path) as f:
            data = f.read().decode('utf8')
            raise ContentReadyException(docutils.publish_string(data, writer_name='html'))
    elif ctype == "inode/directory":
        raise ContentReadyException(render_dir(path))
    elif ctype == "text/html":
        pass
    elif pygments and \
         (ctype.startswith("text/") or ctype in ["x/sh", "text/x-c", 'application/x-perl']):
        print "trying pygments"
        try:
            lexer = get_lexer_for_mimetype(ctype)
#            formatter = HtmlFormatter(full=True, style='default')
            formatter = HtmlFormatter(style='default')
            with open(path) as f:
                data = f.read()
                result = highlight(data, lexer, formatter)
                raise ContentReadyException(result, "text/html", style=formatter.get_style_defs())
        except ClassNotFound as e:
            pass

def render_navbar(path):
    print "**render_navbar:", path
    rpath = [(x, x) for x in os.path.relpath(path, root).split("/") if x != "."]
    print rpath
    rpath.insert(0, ('', '<I>Home</I>'))

    crumbs = ["<A HREF='/view/%s'>%s</A>" % (p, l) for (p, l) in rpath]
    output = " > ".join(crumbs)
    return output

def render_dir(path):
    output = "<UL>"
    for f in os.listdir(path):
        rpath = os.path.relpath(path, root)
        pjoin = os.path.join(rpath, f)
#        print "index:", rpath, f, root, path, pjoin
        output += "<LI><A HREF='/view/%s'>%s</A></LI>\n" % \
                  (pjoin, f)
    output += "</UL>"
    return output


@route('/')
def redirect_root():
    redirect("/view/")

#def index(path=os.getcwd()):
#    template_vars = {"title": path, "style": ""}
#    template_vars["nav"] = render_dir(path)
#    template_vars['body'] = "Click on a file to proceed"
#    return template % template_vars

@route('/view')
@route('/view/<short_path:path>')
def view(short_path=root):
    template_vars = {"title": short_path, "style": ""}


    print "**view: short_path", short_path
    print type(short_path)
    full_path = os.path.join(root, short_path)
    # handle directory case
    if os.path.isdir(full_path):
        template_vars["nav"] = render_navbar(full_path)
        template_vars["body"] = render_dir(full_path)
        return template % template_vars

    template_vars["nav"] = render_navbar(full_path)
    if not os.path.exists(full_path):
        template_vars["body"] = "<H1>Please specify a <u>VALID</u> filename</H1>"
        return template % template_vars
    ctype = discern_type(full_path)
    try:
        dispatch(ctype, full_path)
        response.content_type=ctype
        if ctype in ["text/x-c"]:
            response.content_type="text/plain"
        print full_path, ctype
        with open(full_path) as data:
            template_vars.update({"body": data.read()})
            if ctype.startswith("image/"):
                return template_vars["body"]
            return template % template_vars
    except ContentReadyException as c:
        print "content ready exception", c.ctype
        response.content_type=c.ctype
        # response.charset="utf8"
        print c.ctype
        template_vars.update({"style": c.style, "body": c.content})
        return template % template_vars

@route('/edit')
@route('/edit/<name:path>')
def edit(name=None):
    with open(name) as data:
        output = "<FORM METHOD='POST' ACTION='/post/>"
        output += "<TEXTAREA NAME='data' STYLE='width:100%,height=100%'>"
        output += data.read()
        output += "</TEXTAREA>"
    return template % {"title": name, "style": "", "nav": render_navbar(os.path.dirname(name)), "body": output}


@route('/post')
@route('/post/<name:path>')
def post(name=None):
    pass


if __name__ == '__main__':
    run(host='0.0.0.0', port=9876, reloader=True)
