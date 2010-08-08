# WebKit Crawler

A Python Qt based tool for extracting content from complex websites.

    from webkitcralwer import Page

    dom = Page('http://google.com/search?q=python').main_frame.document()
    result_elements = dom.xpath('//*[@id="ires"]/ol/li')

    for result in result_elements:
        print result.find('h3').text_content()

## Dependencies

Assuming that you're on a Linux box, you need ``python-qt`` and ``lxml``
installed in your system to make it work. If you plan to run it on a server, you
may want to use ``xvfb``, since Qt needs a display backend.

If you get it working on another environment, please contribute to this README.
:)

## Target

Use this software if you are dealing with a web page that completely depends on
JavaScript and you already digged on its code but still can't extract the info
you want with simple HTTP requests.

Note that this software **is not** intended to replace tools like [Mechanize][1]
nor others simple tools for doing web scraping. I would not use it if the page
I want would be downloadable with a simple ``curl`` call.

## Usage

There's a ``Page`` class that you will use to load any web page. It is as simple
as the above example.

After the page is downloaded, you'll have an object (``page``) that contains the
set (tree-like) of frames (``Frame`` objects) that compose the page, starting
from ``page.main_frame``. Any child frames are found in ``frame.child_frames``.

The information and content of each frame is found on its API:

- ``Frame.url``
- ``Frame.name`` (if any, in cases of ``<iframe>``s)
- ``Frame.title``
- ``Frame.child_frames`` (a collection of other frames, as described above)
- ``Frame.document()`` (The frame content, parsed by [lxml][2])
- ``Frame.content`` (The frame content, plain markup).

If you need to handle authentication and/or your page goes through many
redirects until you finally get what you want, consider providing a ``validate``
function for it. Example:

    def proceed_after_redirect(qwebpage):
        """
        After all the redirects, a page with title 'Home' will be displayed.
        Note that you'll be handing the QWebPage in this function, not a Page
        object.
        """
        if 'Home' in qwebpage.mainFrame().title:
            return True

Or even

    def proceed_after_login(qwebpage):
        """
        Fill then submit the authentication form
        """
        if 'Login' in qwebpage.mainFrame().title:
            qwebpage.mainFrame().evaluateJavaScript('''
                var form = document.querySelector('form');
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

This project is licensed under the DWTFYW (Do What The F*ck You Want) license.
No, I'm kidding. It's *MIT* licensed; anyway you are free to do anything you
want with it.

If this program saved your day, please consider sending me some soda or donate
to my PayPal account (evandromyller@gmail.com) so I can buy it here. :)

[1]: http://wwwsearch.sourceforge.net/mechanize/
[2]: http://codespeak.net/lxml/
