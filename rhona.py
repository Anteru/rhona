import tornado.ioloop
import tornado.web
import docutils
import docutils.core
import docutils.writers.html4css1
import pygments_rst
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

class LinkFixupVisitor(docutils.nodes.SparseNodeVisitor):
    def visit_reference (self, n):
        if n ['refuri'] [0] == '/':
            n ['refuri'] = '/wiki' + n ['refuri']

class LinkFixupTransform(docutils.transforms.Transform):
    def apply(self):
        visitor = LinkFixupVisitor(self.document)
        self.document.walk(visitor)

class ImageFixupVisitor(docutils.nodes.SparseNodeVisitor):
    def __init__ (self, doc, basepath):
        super (ImageFixupVisitor, self).__init__ (doc)
        self.__basepath = basepath

    def visit_image (self, n):
        if n ['uri'].startswith ('./'):
            n ['uri'] = '/wiki-static/' + self.__basepath + '/' + n ['uri'][2:]

class ImageFixupTransform(docutils.transforms.Transform):
    def apply(self, basepath):
        visitor = ImageFixupVisitor(self.document, basepath)
        self.document.walk (visitor)

class WikiHandler(tornado.web.RequestHandler):
    def get(self, path):
        startTime = time.clock ()
        filename = os.path.join ('content', path) + '.rst'
        if os.path.exists (filename):
            dt = docutils.core.publish_doctree (
                open (filename, 'r', encoding='utf-8').read (),
                settings_overrides = {
                    'smart_quotes' : True
                })

            linkFixup = LinkFixupTransform (dt)
            linkFixup.apply ()
            imageFixup = ImageFixupTransform (dt)
            parentPath = str (pathlib.Path (path).parent)
            imageFixup.apply (parentPath)

            page = PublishPartsFromDoctree (dt,
                writer = docutils.writers.html4css1.Writer (),
                settings_overrides = {
                    'compact_lists' : False
                })

            meta = {
                'generation-time' : round ((time.clock () - startTime) * 1000, 2)
            }

            self.render ('page.html', page = page, meta = meta)
        else:
            self.send_error (404)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/wiki/(.+)", WikiHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static/"}),
    (r"/wiki-static/(.*)", tornado.web.StaticFileHandler, {"path": "./content/"})
], template_path = 'templates', autoescape=None, debug=True)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
