# WebKit Crawler

A Python Qt based tool for extracting content from complex websites.

    from webkit_browser import Browser
    from lxml import html

    b = Browser()
    b.open('http://google.com/search?q=python')
    content = b.main_frame['content'].read()
    dom = html.fromstring(content)
    results = dom.xpath('//*[@id="ires"]/ol/li')

    for result in results:
        print result.find('h3').text_content()


## Dependencies

Assuming that you're on a Linux box, you need ``python-qt`` installed
in your system to make it work. If you plan to run it on a server, you
may want to use ``xvfb``, since Qt needs a display backend.

If you get it working on another environment, please contribute to this
README. :)


## Target

Use this software if you are dealing with a web page that completely
depends on JavaScript and you already digged on its code but still can't
extract the info you want with simple HTTP requests.

Note that this software **is not** intended to replace tools like
[Mechanize][1] nor others simple tools for doing web scraping. I would
not use it if the page I want would be downloadable with a simple
``curl`` call.


## Usage

There's a ``Browser`` class that works similarly to the Mechanize's
``Browser``, but without all that extra functionality. You can follow
the above example and interact with the ``main_frame`` dict.

When the page is loaded, the code looks for all the page frames,
recursively, and puts them up in a dictionary. Each "frame" has three
keys, ``'title'`` (unicode) ``'content'`` (a file-like object) and
``'children'`` (a list containing child frames, if they exist). As you
can see in the example, ``main_frame`` serves as the root frame.

Additionally, if you're running the code in a graphical environment,
a mini-browser window will open, showing what's happen under the hoods.

If you need to handle authentication and/or your page goes through many
redirects until you finally get what you want, consider providing a
``validate`` function for it. Example:

    def proceed_after_redirect(qwebview):
        """
        After all the redirects, a page with title 'Home' will be
        displayed. Note that you'll be handing the ``QWebView`` instance
        in this function, not a ``Browser`` object.
        """

        if 'Home' in qwebview.page().mainFrame().title:
            return True

Or even

    def proceed_after_login(qwebview):
        """
        Fill then submit the authentication form
        """
        main_frame = qwebview.page().mainFrame()
        if 'Login' in main_frame.title:
            main_frame.evaluateJavaScript('''
                var form = document.querySelector('form#login');
                form['username'].value = '{0}';
                form['password'].value = '{1}';
                form.submit();
            '''.format(
                username, password,
            ))
        else:
            return True

You can always mix these to get what fits your problem. ;)


## License

This project is licensed under the DWTFYW (Do What The F*ck You Want)
license. No, I'm kidding. It's *MIT* licensed; anyway you are free to do
anything you want with it.

If this program saved your day, please consider sending me some soda or
donate to my PayPal account (evandromyller@gmail.com) so I can buy it
here. :)

**Note**: this code needs packaging. Why don't you fork it and make it
a Python package?


[1]: http://wwwsearch.sourceforge.net/mechanize/
