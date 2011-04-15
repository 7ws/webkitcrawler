# encoding: utf-8
'''
A QtWebKit-based browser class that simulates the behavior of Mechanize.
This code is free, but please consider buying me a soda if you'll use it
for commercial purposes. Contact me if so.

This may not be used as a replacement for Mechanize or any other simpler
way to request content from web pages. This tool can be used
specifically for complex pages whose content depends on JavaScript code.

[BTW, please don't let your web pages depend on JS. Thanks.]

© Evandro Myller - emyller.net
'''

from multiprocessing import Pipe, Process
from StringIO import StringIO

from PyQt4.QtCore import QUrl, SIGNAL
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebSettings, QWebView


__all__ = ('Browser',)


class BrowserCore(QWebView):
    '''
    The main browser class, that contains the Qt loop.
    '''
    def __init__(self, conn, validate_page=None):
        super(BrowserCore, self).__init__()
        self.connect(self, SIGNAL('loadFinished(bool)'),
            self._load_finished)

        settings = self.settings()
        settings.setAttribute(QWebSettings.AutoLoadImages, False)
        settings.setAttribute(
            QWebSettings.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebSettings.PluginsEnabled, False)
        settings.setAttribute(QWebSettings.DnsPrefetchEnabled, True)
        settings.setAttribute(QWebSettings.PrivateBrowsingEnabled, True)

        self.validate_page = validate_page
        self.conn = conn
        self.show()
        self._wait()

    @staticmethod
    def _loader(conn, validate_page):
        app = QApplication([])
        browser = BrowserCore(conn, validate_page)
        app.exec_()

    def _wait(self):
        self.open(self.conn.recv())

    class frames:
        @staticmethod
        def from_QWebFrame(qwf):
            f = {
                'children': [],
                'content': StringIO(unicode(qwf.toHtml())),
                'title': unicode(qwf.title()),
            }
            BrowserCore.frames.find(qwf, f['children'])
            return f

        @staticmethod
        def find(parent, children):
            for frame in parent.childFrames():
                child = BrowserCore.frames.from_QWebFrame(frame)
                children.append(child)

    def _load_finished(self):
        self.settings().clearMemoryCaches()
        if not self.validate_page or self.validate_page(self):
            url = str(self.url().toString())
            main_frame = BrowserCore.frames.from_QWebFrame(
                self.page().mainFrame())
            self.conn.send((url, main_frame,))
            self._wait()

    def open(self, url):
        self.load(QUrl(url))


class Browser(object):
    '''
    The public Browser class.

    >>> b = Browser()
    >>> b.open('http://google.com')
    >>> 'Google' in b.main_frame['content'].read()
    True

    For frame-based pages, the frames are contained into
    b.main_frame['children']; each frame has its 'content' and another
    'children' collection.

    The browser object is known to accumulate cache in memory after
    some page loads. You may handle browser invalidation by using the
    'close' method.

    >>> b.close()
    >>> del b
    '''
    def __init__(self, validate=None):
        # count of requests
        self.requests = 0

        self._conn, bc_conn = Pipe()
        self.process = Process(
            target=BrowserCore._loader, args=(bc_conn, validate,))
        self.process.start()

        self.url = None
        self.content = None

    def open(self, url):
        self._conn.send(url)
        self.url, self.main_frame = self._conn.recv()
        self.requests += 1

    def close(self):
        self._conn = None
        self.process.terminate()
