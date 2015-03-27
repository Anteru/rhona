import tornado.ioloop
import tornado.web
import docutils
import docutils.core
import docutils.writers.html4css1
import docutils.transforms.parts
import docutils.nodes
from . import pygments_rst
import tornado.template
import os
import pathlib
import time

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # We write a simple index here
        items = []
        for root, _, files in os.walk ('content'):
            for name in filter (lambda x: x.endswith ('.rst'), sorted (files)):
                name = name [:-4]
                p = os.path.join (root[8:], name)
                p = p.replace ('\\', '/')
                items.append (p)

        self.render ('main.html', items=items)

def PublishPartsFromDoctree (document, destination_path=None,
    writer=None, writer_name='pseudoxml',
    settings=None, settings_spec=None,
    settings_overrides=None, config_section=None,
    enable_exit_status=False):
    reader = docutils.readers.doctree.Reader(parser_name='null')
    pub = docutils.core.Publisher(reader, None, writer,
        source=docutils.io.DocTreeInput(document),
        destination_class=docutils.io.StringOutput, settings=settings)
    if not writer and writer_name:
        pub.set_writer(writer_name)
    pub.process_programmatic_settings(
        settings_spec, settings_overrides, config_section)
    pub.set_destination(None, destination_path)
    pub.publish(enable_exit_status=enable_exit_status)
    return pub.writer.parts

class WikiFixupVisitor(docutils.nodes.SparseNodeVisitor):
    def __init__ (self, doc, basepath):
        super (WikiFixupVisitor, self).__init__ (doc)
        self.__basepath = basepath

    def visit_reference (self, n):
        if n ['refuri'].startswith ('/'):
            n ['refuri'] = '/wiki' + n ['refuri']
        elif n ['refuri'].startswith ('./'):
            # Redirect file links to wiki-static
            p = (os.path.join ('./content', self.__basepath, n ['refuri'][2:]))
            if os.path.exists (p):
                n ['refuri'] = '/wiki-static/' + self.__basepath + n ['refuri'][1:]
            else:
                n ['refuri'] = '/wiki/' + self.__basepath + n ['refuri'][1:]

    def visit_image (self, n):
        if n ['uri'].startswith ('./'):
            n ['uri'] = '/wiki-static/' + self.__basepath + n ['uri'][1:]

class WikiFixupTransform(docutils.transforms.Transform):
    def apply(self, basepath):
        visitor = WikiFixupVisitor(self.document, basepath)
        self.document.walk (visitor)

class BuildTocTransform(docutils.transforms.Transform):
    def apply(self):
        return self.build_contents (self.document)

    def build_contents(self, node, level=0):
        level += 1
        sections = [sect for sect in node if isinstance(sect, docutils.nodes.section)]
        entries = []
        for section in sections:
            item = {}
            title = section[0]
            item ['label'] = title.astext()
            item ['id'] = section.attributes ['ids'][0]
            item ['children'] = self.build_contents(section, level)
            entries.append(item)
        return entries

def TocToHtmlList (toc):
    def _TocItem (entry):
        r = '<li><a href="#{0}">{1}</a>'.format (entry ['id'], entry ['label'])
        if entry ['children']:
            r += '<ul>'
            for child in entry ['children']:
                r += _TocItem (child)
            r += '</ul>'
        r += '</li>'
        return r

    # Top level is the document itself
    if len (toc) == 1 and toc [0] ['children']:
        r = '<ul>'
        for entry in toc [0]['children']:
            r += _TocItem (entry)
        r += '</ul>'
        return r
    else:
        return None

class WikiHandler(tornado.web.RequestHandler):
    def get(self, path):
        startTime = time.clock ()
        filename = os.path.join ('content', path) + '.rst'
        if os.path.exists (filename):
            dt = docutils.core.publish_doctree (
                open (filename, 'r', encoding='utf-8').read (),
                settings_overrides = {
                    'smart_quotes' : True,
                    'doctitle_xform' : False
                })

            wikiFixup = WikiFixupTransform (dt)
            parentPath = str (pathlib.Path (path).parent)
            wikiFixup.apply (parentPath)

            page = PublishPartsFromDoctree (dt,
                writer = docutils.writers.html4css1.Writer (),
                settings_overrides = {
                    'compact_lists' : False
                })

            tocTransform = BuildTocTransform (dt)
            toc = tocTransform.apply ()
            page ['toc'] = TocToHtmlList (toc)
            page ['title']= dt.children [0][0].astext()

            meta = {
                'generation-time' : round ((time.clock () - startTime) * 1000, 2),
                'style' : self.get_query_argument ('style', 'default'),
                'url' : '/wiki/' + path
            }

            self.render ('page.html', page = page, meta = meta)
        else:
            self.send_error (404)

class Server:
    def __init__ (self, port=8888):
        self.__application = tornado.web.Application([
            (r"/", MainHandler),
            (r"/wiki/(.+)", WikiHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static/"}),
            (r"/wiki-static/(.*)", tornado.web.StaticFileHandler, {"path": "./content/"})
        ], template_path = 'templates', autoescape=None, debug=True)
        self.__port = port

    def Run (self):
        self.__application.listen (self.__port)
        tornado.ioloop.IOLoop.instance().start()
