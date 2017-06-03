from jinja2 import Environment, FileSystemLoader

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, StaticFileHandler

from bokeh.application import Application as bkApplication
from bokeh.application.handlers import FunctionHandler as bkFunctionHandler
from bokeh.embed import autoload_server as bk_autoload_server
from bokeh.server.server import Server as bkServer

from app import modify_doc

import logging
import tornado.web

try:
    from urllib.parse import unquote
except ImportError:
    # Python 2.
    from urllib import unquote

env = Environment(loader=FileSystemLoader('templates'))


class IndexHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        template = env.get_template('embed.html')
        script = bk_autoload_server(model=None, url='http://localhost:5006/bkapp')
        self.write(template.render(script=script, template="Tornado"))


class POSTHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self):
        logging.info(str(self.request.files.items()))
        for field_name, files in self.request.files.items():
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                body = info['body']
                logging.info('POST "%s" "%s" %d bytes',
                             filename, content_type, len(body))


bokeh_app = bkApplication(bkFunctionHandler(modify_doc))

io_loop = IOLoop.current()
fineUploaderPath = "fine-uploader"
server = bkServer({'/bkapp': bokeh_app}, io_loop=io_loop, extra_patterns=[('/', IndexHandler),
                                                                          (r"/server/upload", POSTHandler),
                                                                          (r'/fine-uploader/(.*)', StaticFileHandler,
                                                                           {'path': fineUploaderPath})
                                                                          ])
server.start()

if __name__ == '__main__':
    from bokeh.util.browser import view

    print('Opening Tornado app with embedded Bokeh application on http://localhost:5006/')

    io_loop.add_callback(view, "http://localhost:5006/")
    io_loop.start()
