"""
This module deals with valid internet media types for feeds.
"""

__author__ = "Joseph Walton <http://www.kafsemo.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2004 Joseph Walton"

from cgi import parse_header
from .logging import *

FEED_TYPES = [
  'text/xml', 'application/xml', 'application/rss+xml', 'application/rdf+xml',
  'application/atom+xml', 'text/x-opml', 'application/xrds+xml',
  'application/opensearchdescription+xml', 'application/vnd.google-earth.kml+xml', 'application/vnd.google-earth.kmz',
  'application/atomsvc+xml', 'application/atomcat+xml',
]

# Is the Content-Type correct?
def checkValid(contentType, loggedEvents):
  (mediaType, params) = parse_header(contentType)
  if mediaType.lower() not in FEED_TYPES:
    loggedEvents.append(UnexpectedContentType({"type": "Feeds", "contentType": mediaType}))
  if 'charset' in params:
    charset = params['charset']
  else:
    charset = None

  return (mediaType, charset)

# Warn about mismatches between media type and feed version
def checkAgainstFeedType(mediaType, feedType, loggedEvents):
  mtl = mediaType.lower()

  if mtl in ['application/x.atom+xml', 'application/atom+xml']:
    if feedType not in [TYPE_ATOM, TYPE_ATOM_ENTRY]:
      loggedEvents.append(UnexpectedContentType({"type": 'Non-Atom 1.0 feeds', "contentType": mediaType}))
  elif mtl == 'application/atomcat+xml':
    if feedType != TYPE_APP_CATEGORIES:
      loggedEvents.append(UnexpectedContentType({"type": 'Non-AtomPub Category document', "contentType": mediaType}))
  elif mtl == 'application/atomsvc+xml':
    if feedType != TYPE_APP_SERVICE:
      loggedEvents.append(UnexpectedContentType({"type": 'Non-AtomPub Service document', "contentType": mediaType}))
  elif mtl == 'application/rdf+xml':
    if feedType != TYPE_RSS1:
      loggedEvents.append(UnexpectedContentType({"type": 'Non-RSS 1.0 feeds', "contentType": mediaType}))
  elif mtl == 'application/rss+xml':
    if feedType not in [TYPE_RSS1, TYPE_RSS2]:
      loggedEvents.append(UnexpectedContentType({"type": 'Non-RSS feeds', "contentType": mediaType}))
  elif mtl == 'text/x-opml':
    if feedType not in [TYPE_OPML]:
      loggedEvents.append(UnexpectedContentType({"type": 'Non-OPML feeds', "contentType": mediaType}))
  elif mtl == 'application/opensearchdescription+xml':
    if feedType not in [TYPE_OPENSEARCH]:
      loggedEvents.append(UnexpectedContentType({"type": 'Non-OpenSearchDescription documents', "contentType": mediaType}))
  elif mtl == 'application/xrds+xml':
    if feedType not in [TYPE_XRD]:
      loggedEvents.append(UnexpectedContentType({"type": 'Non-Extensible Resource Descriptor documents', "contentType": mediaType}))
  elif mtl == 'application/vnd.google-earth.kml+xml':
    if feedType not in [TYPE_KML20, TYPE_KML21, TYPE_KML22]:
      loggedEvents.append(UnexpectedContentType({"type": 'Non-KML documents', "contentType": mediaType}))
  elif mtl == 'application/earthviewer':
    loggedEvents.append(InvalidKmlMediaType({"type": 'Non-KML documents', "contentType": mediaType}))

# warn if a non-specific media type is used without a 'marker'
def contentSniffing(mediaType, rawdata, loggedEvents):
  if mediaType not in FEED_TYPES: return
  if mediaType == 'application/atom+xml': return
  if mediaType == 'application/atomcat+xml': return
  if mediaType == 'application/atomsvc+xml': return
  if mediaType == 'application/rss+xml': return
  if mediaType == 'text/x-opml': return
  if mediaType == 'application/opensearchdescription+xml': return
  if mediaType == 'application/xrds+xml': return
  if mediaType == 'application/vnd.google-earth.kml+xml': return

  block = rawdata[:512]

  if block.find(b'<rss') >= 0: return
  if block.find(b'<feed') >= 0: return
  if block.find(b'<opml') >= 0: return
  if block.find(b'<kml') >= 0: return
  if block.find(b'<OpenSearchDescription') >= 0: return
  if (block.find(b'<rdf:RDF') >=0 and
      block.find(b'http://www.w3.org/1999/02/22-rdf-syntax-ns#') >= 0 and
      block.find( b'http://purl.org/rss/1.0/')): return

  from .logging import NonSpecificMediaType
  loggedEvents.append(NonSpecificMediaType({"contentType": mediaType}))
