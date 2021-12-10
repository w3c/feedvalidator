#!/usr/bin/env python3
"""feedfinder: Find the Web feed for a Web page
http://www.aaronsw.com/2002/feedfinder/

Usage:
  feed(uri) - returns feed found for a URI
  feeds(uri) - returns all feeds found for a URI

    >>> import feedfinder
    >>> feedfinder.feed('scripting.com')
    'http://scripting.com/rss.xml'
    >>>
    >>> feedfinder.feeds('scripting.com')
    ['http://delong.typepad.com/sdj/atom.xml',
     'http://delong.typepad.com/sdj/index.rdf',
     'http://delong.typepad.com/sdj/rss.xml']
    >>>

Can also use from the command line.  Feeds are returned one per line:

    $ python feedfinder.py diveintomark.org
    http://diveintomark.org/xml/atom.xml

How it works:
  0. At every step, feeds are minimally verified to make sure they are really feeds.
  1. If the URI points to a feed, it is simply returned; otherwise
     the page is downloaded and the real fun begins.
  2. Feeds pointed to by LINK tags in the header of the page (autodiscovery)
  3. <A> links to feeds on the same server ending in ".rss", ".rdf", ".xml", or
     ".atom"
  4. <A> links to feeds on the same server containing "rss", "rdf", "xml", or "atom"
  5. <A> links to feeds on external servers ending in ".rss", ".rdf", ".xml", or
     ".atom"
  6. <A> links to feeds on external servers containing "rss", "rdf", "xml", or "atom"
  7. Try some guesses about common places for feeds (index.xml, atom.xml, etc.).
"""

__version__ = "2.0"
__date__ = "2021-12-01"
__maintainer__ = "Dominique Hazael-Massieux (dom@w3.org)"
__author__ = "Mark Pilgrim (http://diveintomark.org)"
__copyright__ = "Copyright 2002-4, Mark Pilgrim; 2006 Aaron Swartz, 2021 Dominique Hazael-Massieux"
__license__ = "Python"
__credits__ = """Abe Fettig for a patch to sort Syndic8 feeds by popularity
Also Jason Diamond, Brian Lalor for bug reporting and patches"""

_debug = 0

from html5lib import HTMLParser
from lxml import etree
import html5lib, urllib.request, urllib.error, urllib.parse, re, sys, urllib.robotparser

import threading
class TimeoutError(Exception): pass

def timelimit(timeout):
    def internal(function):
        def internal2(*args, **kw):
            """
            from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/473878
            """
            class Calculator(threading.Thread):
                def __init__(self):
                    threading.Thread.__init__(self)
                    self.result = None
                    self.error = None

                def run(self):
                    try:
                        self.result = function(*args, **kw)
                    except:
                        self.error = sys.exc_info()

            c = Calculator()
            c.setDaemon(True) # don't hold up exiting
            c.start()
            c.join(timeout)
            if c.is_alive():
                raise TimeoutError
            if c.error:
                raise c.error[0](c.error[1])
            return c.result
        return internal2
    return internal

if not dict:
    def dict(aList):
        rc = {}
        for k, v in aList:
            rc[k] = v
        return rc

def _debuglog(message):
    if _debug: print(message)

class URLGatekeeper:
    """a class to track robots.txt rules across multiple servers"""
    def __init__(self):
        self.rpcache = {} # a dictionary of RobotFileParser objects, by domain
        self.urlopener = urllib.request.build_opener()
        self.version = "feedfinder/" + __version__ + " https://github.com/w3c/feedvalidator/blob/main/feedfinder.py"
        _debuglog(self.version)
        self.urlopener.addheaders = [('User-agent', self.version)]

    def _getrp(self, url):
        protocol, domain = urllib.parse.urlparse(url)[:2]
        if domain in self.rpcache:
            return self.rpcache[domain]
        baseurl = '%s://%s' % (protocol, domain)
        robotsurl = urllib.parse.urljoin(baseurl, 'robots.txt')
        _debuglog('fetching %s' % robotsurl)
        rp = urllib.robotparser.RobotFileParser()
        with self.urlopener.open(robotsurl) as response:
            rp.parse(response.read().decode("utf-8").splitlines())
        try:
            rp.read()
        except:
            pass
        self.rpcache[domain] = rp
        return rp

    def can_fetch(self, url):
        rp = self._getrp(url)
        allow = rp.can_fetch(self.version, url)
        _debuglog("gatekeeper of %s says %s" % (url, allow))
        return allow

    @timelimit(10)
    def get(self, url):
        if not self.can_fetch(url): return ''
        try:
            return self.urlopener.open(url).read()
        except:
            return ''

_gatekeeper = URLGatekeeper()

class BaseParser(HTMLParser):
    def __init__(self, baseuri):
        HTMLParser.__init__(self, namespaceHTMLElements=False)
        self.links = []
        self.baseuri = baseuri

    def feed(self, data):
        root = self.parse(data)
        for child in root.iter('*'):
            if isinstance(child.tag, str):
                try:
                    handler = getattr(self, "do_" + child.tag)
                    handler(child)
                except AttributeError:
                    pass

    def do_base(self, el):
        if el.get('href'):
            self.baseuri = el.get('href').strip()

    def error(self, *a, **kw): pass # we're not picky

class LinkParser(BaseParser):
    FEED_TYPES = ('application/rss+xml',
                  'text/xml',
                  'application/atom+xml',
                  'application/x.atom+xml',
                  'application/x-atom+xml')
    def do_link(self, el):
        if not el.get('rel'): return
        rels = el.get('rel').lower().split()
        if 'alternate' not in rels: return
        if el.get('type').lower().strip() not in self.FEED_TYPES: return
        if not el.get('href'): return
        self.links.append(urllib.parse.urljoin(self.baseuri, el.get('href').strip()))

class ALinkParser(BaseParser):
    def do_a(self, el):
        if not el.get('href'): return
        self.links.append(urllib.parse.urljoin(self.baseuri, el.get('href').strip()))

def makeFullURI(uri):
    if uri.startswith('feed://'):
        uri = 'http://' + uri.split('feed://', 1).pop()
    for x in ['http', 'https']:
        if uri.startswith('%s://' % x):
            return uri
    return 'http://%s' % uri

def getLinks(data, baseuri):
    p = LinkParser(baseuri)
    p.feed(data)
    return p.links

def getALinks(data, baseuri):
    p = ALinkParser(baseuri)
    p.feed(data)
    return p.links

def getLocalLinks(links, baseuri):
    baseuri = baseuri.lower()
    urilen = len(baseuri)
    return [l for l in links if l.lower().startswith(baseuri)]

def isFeedLink(link):
    if link.startswith('http://feeds.feedburner.com/'): return True
    if link.endswith('/feeds/posts/default'): return True
    return link[-4:].lower() in ('.rss', '.rdf', '.xml') or link[-5:].lower() in ('.atom', 'atom/', '/atom', '/feed')

def isXMLRelatedLink(link):
    link = link.lower()
    return link.count('rss') + link.count('rdf') + link.count('xml') + link.count('atom') + link.count('feed')

def couldBeFeedData(data):
    data = data.lower()
    if isinstance(data, str):
        data = data.encode("utf-8")
    if data.count(b'<html'): return 0
    return data.count(b'<rss') + data.count(b'<rdf') + data.count(b'<feed')

def isFeed(uri):
    _debuglog('seeing if %s is a feed' % uri)
    protocol = urllib.parse.urlparse(uri)
    if protocol[0] not in ('http', 'https'): return 0
    try:
        data = _gatekeeper.get(uri)
    except TimeoutError: # server down, give up
        return false
    return couldBeFeedData(data)

def sortFeeds(feed1Info, feed2Info):
    return cmp(feed2Info['headlines_rank'], feed1Info['headlines_rank'])

def feeds(uri, all=False):
    fulluri = makeFullURI(uri)
    try:
        data = _gatekeeper.get(fulluri)
    except:
        return []
    # is this already a feed?
    if couldBeFeedData(data):
        return [fulluri]
    # nope, it's a page, try LINK tags first
    _debuglog('looking for LINK tags')
    try:
        feeds = getLinks(data, fulluri)
    except:
        feeds = []
    _debuglog('found %s feeds through LINK tags' % len(feeds))
    feeds = list(filter(isFeed, feeds))
    if all or not feeds:
        # no LINK tags, look for regular <A> links that point to feeds
        _debuglog('no LINK tags, looking at A tags')
        try:
            links = getALinks(data, fulluri)
        except:
            links = []
        locallinks = getLocalLinks(links, fulluri)
        # look for obvious feed links on the same server
        feeds.extend(list(filter(isFeed, list(filter(isFeedLink, locallinks)))))
        if all or not feeds:
            # look harder for feed links on the same server
            feeds.extend(list(filter(isFeed, list(filter(isXMLRelatedLink, locallinks)))))
        if all or not feeds:
            # look for obvious feed links on another server
            feeds.extend(list(filter(isFeed, list(filter(isFeedLink, links)))))
        if all or not feeds:
            # look harder for feed links on another server
            feeds.extend(list(filter(isFeed, list(filter(isXMLRelatedLink, links)))))
    if all and not feeds:
        _debuglog('no A tags, guessing')
        suffixes = [ # filenames used by popular software:
          'atom.xml', # blogger, TypePad
          'index.atom', # MT, apparently
          'index.rdf', # MT
          'rss.xml', # Dave Winer/Manila
          'index.xml', # MT
          'index.rss' # Slash
        ]
        feeds.extend(list(filter(isFeed, [urllib.parse.urljoin(fulluri, x) for x in suffixes])))
    if hasattr(__builtins__, 'set') or 'set' in __builtins__:
        feeds = list(set(feeds))
    return feeds

getFeeds = feeds # backwards-compatibility

def feed(uri):
    #todo: give preference to certain feed formats
    feedlist = feeds(uri)
    if feedlist:
        return feedlist[0]
    else:
        return None

##### test harness ######

def test():
    failed = []
    count = 0
    filename = 'html4-001.html'
    while 1:
        uri = 'http://diveintomark.org/tests/client/autodiscovery/' + filename
        with open("feedfinder-tests/%s" % filename, 'rb') as f:
            data = f.read()
            if data.find(b'Atom autodiscovery test') == -1: break
            sys.stdout.write('.')
            sys.stdout.flush()
            count += 1
            links = getLinks(data, uri)
            if not links:
                print('\n*** FAILED ***', uri, 'could not find link')
                failed.append(uri)
            elif len(links) > 1:
                print('\n*** FAILED ***', uri, 'found too many links')
                failed.append(uri)
            else:
                feedfilename = links[0].split('/')[-1]
                if links[0].startswith('http://www.ragingplatypus.com/'):
                    feedfilename = "ragingplatypus/" + feedfilename
                with open("feedfinder-tests/%s" % feedfilename, 'rb') as atomf:
                    atomdata = atomf.read()
                    if atomdata.find(b'<link rel="alternate"') == -1:
                        print('\n*** FAILED ***', uri, 'retrieved something that is not a feed')
                        failed.append(uri)
                    else:
                        backlink = atomdata.split(b'href="').pop().split(b'"')[0].decode('utf-8')
                        if backlink != uri:
                            print('\n*** FAILED ***', uri, 'retrieved wrong feed, backlink set to ', backlink)
                            failed.append(uri)
            if data.find(b'<link rel="next" href="') == -1: break
            filename = data.split(b'<link rel="next" href="').pop().split(b'"')[0].split(b'/')[-1].decode('us-ascii')
    print()
    print(count, 'tests executed,', len(failed), 'failed')

if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--debug':
        _debug = 1
        args.pop(0)
    if args:
        uri = args[0]
    else:
        uri = 'http://diveintomark.org/'
    if uri == 'test':
        test()
    else:
        print("\n".join(getFeeds(uri)))
