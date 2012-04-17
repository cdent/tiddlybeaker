"""
A framework kind of thing, using TiddlyWeb as
the base. To explore if it is possible.
"""
import logging
from itertools import chain
from tiddlyweb.web.serve import start_cherrypy, load_app

from tiddlywebplugins.templates import get_template

app = None

class Request(object):
    """
    A request object that encapsulates the WSGI environment.
    """

    def __init__(self, environ):
        self.env = environ

    @property
    def store(self):
        return self.env['tiddlyweb.store']


class App(object):
    """
    A carrier for various bits of information.
    """

    def __init__(self, server, config=None):
        if config is None:
            config = {}
        self.server = server
        self.config = config

    def start(self):
        from cherrypy.wsgiserver import CherryPyWSGIServer
        hostname = self.config['server_host']['host']
        port = int(self.config['server_host']['port'])
        scheme = self.config['server_host']['scheme']
        server = CherryPyWSGIServer((hostname, port), self.server)
        try:
            logging.debug('starting CherryPy at %s://%s:%s',
                    scheme, hostname, port)
            print "Starting CherryPy at %s://%s:%s" % (scheme, hostname, port)
            server.start()
        except KeyboardInterrupt:
            server.stop()

def establish():
    """
    Set up the global app.
    """
    from tiddlyweb.config import config

    global app
    app = App(load_app(), config)
    return app


def render(b, content=None, template=None, **kwargs):
    """
    Return iterated content or template, or both.
    """
    if content is None:
        content = []
    if template is not None:
        template_object = get_template(b.env, template)
        template_generator = template_object.generate(kwargs)
    else:
        template_generator = []
    return chain(content, template_generator)


def route(path, methods=['GET']):
    """
    Decorate a method to be a route handler.

    This means getting it on the selector, and providing
    some satisfactory local variables.
    """

    def entangle(func):

        def _handle_route(environ, start_response, *args, **kwds):
            output = func(Request(environ))
            start_response('200 OK', [
                ('Content-Type', 'text/html; charset=UTF-8')])
            return output

        method_dict = dict((method, _handle_route) for method in methods)
        app.config['selector'].add(path, **method_dict)

        return _handle_route

    return entangle
