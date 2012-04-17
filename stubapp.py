from tiddlybeaker import establish, route, render

from pprint import pformat

app = establish()

@route('/carp', ['GET', 'POST'])
def root(b):
    return render(b, template='hello.html', name='chris', store=b.store.__class__)

if __name__ == '__main__':
    app.start()
