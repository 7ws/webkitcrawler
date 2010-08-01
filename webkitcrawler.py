# -*- coding: utf-8 -*-

"""
(c) Evandro Myller - emyller.net
Released under MIT license.

This library is intended for situations where certain -- aka "crappy" -- pages
*really* require JavaScript to be displayed properly. Note that it doesn't load
any media from the page. If you don't need to run JavaScript, use Mechanize
instead or consider looking at Scrapy for web crawling.

If this program saved your day, please consider sending me some soda or donate
to my PayPal account (evandromyller@gmail.com) so I can buy it here. :)
"""

import re
import sys
from PyQt4.QtCore import QUrl, SIGNAL
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebPage, QWebSettings
from lxml import html
from multiprocessing import Process, Queue


class _loader(QWebPage):
    """
    Uses QtWebKit to load a page. Note that this class should never be used
    alone, since one process can't have more than one QApplication instance.
    Use 'Page' instead.
    """
    def __init__(self, url, validate=None):
        self._app = QApplication(sys.argv)
        self._validate = validate
        QWebPage.__init__(self)
        settings = self.settings()
        settings.setAttribute(QWebSettings.AutoLoadImages, False)
        settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebSettings.PluginsEnabled, False)
        self.connect(self, SIGNAL('loadFinished(bool)'), self._finished)
        self.mainFrame().load(QUrl(url))
        self._app.exec_()

    def _finished(self, result):
        main_frame = self.mainFrame()

        self.title = unicode(main_frame.title())

        self.main_frame = Frame.fromQWebFrame(main_frame)
        Frame.find_frames(main_frame, self.main_frame)

        if not self._validate or self._validate(self):
            self._app.quit()

class Frame(object):
    def __init__(self, content, **info):
        self.content = content
        self.url = info.get('src')
        self.name = info.get('name')
        self.title = info.get('title')
        self.child_frames = []

    def document(self):
        return html.fromstring(self.content)

    @staticmethod
    def find_frames(parent, frame_object=None):
        """
        Looks recursively for QWebFrame objects in 'parent'.

        Maybe this function would make more sense if it was placed at 'Page',
        but since QWebFrame objects would be no longer available in there,
        they are "parsed" here.
        """
        for frame in parent.childFrames():
            child = Frame.fromQWebFrame(frame)
            frame_object.child_frames.append(child)
            Frame.find_frames(frame, child)

    @staticmethod
    def fromQWebFrame(frame):
        return Frame(unicode(frame.toHtml()),
            url=str(frame.baseUrl()),
            name=str(frame.frameName()),
            title=unicode(frame.title()),
        )

class Page(object):
    """
    Grabs the contents of a web page.

    Use the 'validate' parameter if you wish to verify if the page is ready to
    be returned. This is useful when handling authentication, redirects, etc.
    Note that 'validate' is called with a QWebPage instance (derived from
    '_loader') as its only parameter.
    """
    def __init__(self, url, validate=None):
        queue = Queue()
        proc = Process(target=lambda: queue.put(_loader(url, validate)))
        proc.start()
        self.main_frame = queue.get().main_frame
        proc.join()
