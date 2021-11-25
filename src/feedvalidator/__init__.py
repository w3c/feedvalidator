__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

import socket
if hasattr(socket, 'setdefaulttimeout'):
  socket.setdefaulttimeout(10)
  Timeout = socket.timeout
else:
  from . import timeoutsocket
  timeoutsocket.setDefaultSocketTimeout(10)
  Timeout = timeoutsocket.Timeout

import urllib
import ssl
from . import logging
from .logging import *
from xml.sax import SAXException
from xml.sax._exceptions import SAXParseException
from xml.sax.xmlreader import InputSource
# needed in python 3.7.1+
from xml.sax.handler import feature_external_ges
import re
from . import xmlEncoding
from . import mediaTypes
from http.client import BadStatusLine

MAXDATALENGTH = 5000000

def sniffPossibleFeed(rawdata):
  """ Use wild heuristics to detect something that might be intended as a feed."""
  if rawdata.lower().startswith('<!DOCTYPE html'):
    return False

  rawdata=re.sub('<!--.*?-->','',rawdata)
  firstPart = rawdata[:512]
  for tag in ['<rss', '<feed', '<rdf:RDF', '<kml']:
    if tag in firstPart:
      return True

  lastline = rawdata.strip().split('\n')[-1].strip()
  return lastline in ['</rss>','</feed>','</rdf:RDF>', '</kml>']

def _validate(aString, firstOccurrenceOnly, loggedEvents, base, encoding, selfURIs=None, mediaType=None, groupEvents=0):
  """validate RSS from string, returns validator object"""
  from xml.sax import make_parser, handler
  from .base import SAXDispatcher
  from io import StringIO

  if re.match("^\s+<\?xml",aString) and re.search("<generator.*wordpress.*</generator>",aString):
    lt = aString.find('<'); gt = aString.find('>')
    if lt > 0 and gt > 0 and lt < gt:
      loggedEvents.append(logging.WPBlankLine({'line':1,'column':1}))
      # rearrange so that other errors can be found
      aString = aString[lt:gt+1]+aString[0:lt]+aString[gt+1:]

  # By now, aString should be Unicode
  source = InputSource()
  source.setByteStream(StringIO(aString))

  validator = SAXDispatcher(base, selfURIs or [base], encoding)
  validator.setFirstOccurrenceOnly(firstOccurrenceOnly)
  validator.setGroupEvents(groupEvents)

  if mediaType == 'application/atomsvc+xml':
    validator.setFeedType(TYPE_APP_SERVICE)
  elif mediaType ==  'application/atomcat+xml':
    validator.setFeedType(TYPE_APP_CATEGORIES)

  validator.loggedEvents += loggedEvents

  # experimental RSS-Profile support
  validator.rssCharData = [s.find('&#x')>=0 for s in aString.split('\n')]

  xmlver = re.match("^<\?\s*xml\s+version\s*=\s*['\"]([-a-zA-Z0-9_.:]*)['\"]",aString)
  if xmlver and xmlver.group(1) != '1.0':
    validator.log(logging.BadXmlVersion({"version":xmlver.group(1)}))

  try:
    from xml.sax.expatreader import ExpatParser
    class fake_dtd_parser(ExpatParser):
      def reset(self):
        ExpatParser.reset(self)
        self._parser.UseForeignDTD(1)
    parser = fake_dtd_parser()
  except:
    parser = make_parser()

  parser.setFeature(handler.feature_namespaces, 1)
  parser.setFeature(feature_external_ges, True)
  parser.setContentHandler(validator)
  parser.setErrorHandler(validator)
  parser.setEntityResolver(validator)
  if hasattr(parser, '_ns_stack'):
    # work around bug in built-in SAX parser (doesn't recognize xml: namespace)
    # PyXML doesn't have this problem, and it doesn't have _ns_stack either
    parser._ns_stack.append({'http://www.w3.org/XML/1998/namespace':'xml'})

  def xmlvalidate(log):
    import libxml2
    from io import StringIO
    from random import random

    prefix="...%s..." % str(random()).replace('0.','')
    msg=[]
    libxml2.registerErrorHandler(lambda msg,str: msg.append(str), msg)

    input = libxml2.inputBuffer(StringIO(aString))
    reader = input.newTextReader(prefix)
    reader.SetParserProp(libxml2.PARSER_VALIDATE, 1)
    ret = reader.Read()
    while ret == 1: ret = reader.Read()

    msg=''.join(msg)
    for line in msg.splitlines():
      if line.startswith(prefix): log(line.split(':',4)[-1].strip())
  validator.xmlvalidator=xmlvalidate

  try:
    parser.parse(source)
  except SAXException:
    pass
  except UnicodeDecodeError:
    import sys
    exctype, value = sys.exc_info()[:2]
    validator.log(logging.UnicodeError({"exception":value}))

  if validator.getFeedType() == TYPE_RSS1:
    try:
      from rdflib.plugins.parsers.rdfxml import RDFXMLHandler

      class Handler(RDFXMLHandler):
        ns_prefix_map = {}
        prefix_ns_map = {}
        def bind(self, prefix, namespace, override=False):
          self.ns_prefix_map[prefix] = namespace
          self.prefix_ns_map[namespace] = prefix
        def add(self, triple): pass
        def __init__(self, dispatcher):
          RDFXMLHandler.__init__(self, self)
          self.dispatcher=dispatcher
        def error(self, message):
          self.dispatcher.log(InvalidRDF({"message": message}))

      source = InputSource()
      source.setByteStream(StringIO(aString))

      parser.reset()
      parser.setContentHandler(Handler(parser.getContentHandler()))
      parser.setErrorHandler(handler.ErrorHandler())
      try:
        parser.parse(source)
      except SAXParseException as e:
        self.dispatcher.log(SAXError({"message": e.message}))
    except Exception as e:
      pass

  return validator

def validateStream(aFile, firstOccurrenceOnly=0, contentType=None, base=""):
  loggedEvents = []

  if contentType:
    (mediaType, charset) = mediaTypes.checkValid(contentType, loggedEvents)
  else:
    (mediaType, charset) = (None, None)

  rawdata = aFile.read(MAXDATALENGTH)
  if aFile.read(1):
    raise ValidationFailure(logging.ValidatorLimit({'limit': 'feed length > ' + str(MAXDATALENGTH) + ' bytes'}))

  encoding, rawdata = xmlEncoding.decode(mediaType, charset, rawdata, loggedEvents, fallback='utf-8')


  validator = _validate(rawdata, firstOccurrenceOnly, loggedEvents, base, encoding, mediaType=mediaType)

  if mediaType and validator.feedType:
    mediaTypes.checkAgainstFeedType(mediaType, validator.feedType, validator.loggedEvents)

  return {"feedType":validator.feedType, "loggedEvents":validator.loggedEvents}

def validateString(aString, firstOccurrenceOnly=0, fallback=None, base=""):
  loggedEvents = []
  if type(aString) != str:
    encoding, aString = xmlEncoding.decode("", None, aString, loggedEvents, fallback)
  else:
    encoding = "utf-8" # setting a sane (?) default

  if aString is not None:
    validator = _validate(aString, firstOccurrenceOnly, loggedEvents, base, encoding)
    return {"feedType":validator.feedType, "loggedEvents":validator.loggedEvents}
  else:
    return {"loggedEvents": loggedEvents}

def validateURL(url, firstOccurrenceOnly=1, wantRawData=0, groupEvents=0):
  """validate RSS from URL, returns events list, or (events, rawdata) tuple"""
  loggedEvents = []
  request = urllib.request.Request(url)
  request.add_header("Accept-encoding", "gzip, deflate")
  request.add_header("User-Agent", "FeedValidator/1.3")
  usock = None
  ctx2 = ssl.create_default_context()
  ctx1 = ssl.create_default_context()
  ctx2.set_ciphers('ALL:@SECLEVEL=2')
  ctx1.set_ciphers('ALL:@SECLEVEL=1')
  try:
    try:
      try:
        usock = urllib.request.urlopen(request, context=ctx2)
      except urllib.error.URLError as x:
        if isinstance(x.reason, socket.timeout):
          raise ValidationFailure(logging.IOError({"message": 'Server timed out', "exception":x}))
        if "WRONG_SIGNATURE_TYPE" in x.reason[1]:
          loggedEvents.append(HttpsProtocolWarning({'message': "Weak signature used by HTTPS server"}))
          usock = urllib.request.urlopen(request, context=ctx1)
        elif "CERTIFICATE_VERIFY_FAILED" in x.reason[1]:
          raise logging.HttpsProtocolError({'message': "HTTPs server has incorrect certificate configuration"})
        else:
          raise x
      rawdata = usock.read(MAXDATALENGTH)
      if usock.read(1):
        raise ValidationFailure(logging.ValidatorLimit({'limit': 'feed length > ' + str(MAXDATALENGTH) + ' bytes'}))

      # check for temporary redirects
      if usock.geturl() != request.get_full_url():
        from urllib.parse import urlsplit
        (scheme, netloc, path, query, fragment) = urlsplit(url)
        if scheme == 'http':
          from http.client import HTTPConnection
          requestUri = (path or '/') + (query and '?' + query)

          conn=HTTPConnection(netloc)
          conn.request("GET", requestUri)
          resp=conn.getresponse()
          if resp.status != 301:
            loggedEvents.append(TempRedirect({}))

    except BadStatusLine as status:
      raise ValidationFailure(logging.HttpError({'status': status.__class__}))
    except logging.HttpsProtocolError as x:
      raise ValidationFailure(x)

    except urllib.error.HTTPError as status:
      rawdata = status.read()
      if len(rawdata) < 512 or 'content-encoding' in status.headers:
        loggedEvents.append(logging.HttpError({'status': status}))
        usock = status
      else:
        rawdata=re.sub('<!--.*?-->','',rawdata)
        lastline = rawdata.strip().split('\n')[-1].strip()
        if sniffPossibleFeed(rawdata):
          loggedEvents.append(logging.HttpError({'status': status}))
          loggedEvents.append(logging.HttpErrorWithPossibleFeed({}))
          usock = status
        else:
          raise ValidationFailure(logging.HttpError({'status': status}))
    except urllib.error.URLError as x:
      raise ValidationFailure(logging.HttpError({'status': x.reason}))
    except Timeout as x:
      raise ValidationFailure(logging.IOError({"message": 'Server timed out', "exception":x}))
    except Exception as x:
      raise ValidationFailure(logging.IOError({"message": x.__class__.__name__,
        "exception":x}))

    if usock.headers.get('content-encoding', None) == None:
      loggedEvents.append(Uncompressed({}))

    if usock.headers.get('content-encoding', None) == 'gzip':
      import gzip, io
      try:
        rawdata = gzip.GzipFile(fileobj=io.BytesIO(rawdata)).read()
      except:
        import sys
        exctype, value = sys.exc_info()[:2]
        event=logging.IOError({"message": 'Server response declares Content-Encoding: gzip', "exception":value})
        raise ValidationFailure(event)

    if usock.headers.get('content-encoding', None) == 'deflate':
      import zlib
      try:
        rawdata = zlib.decompress(rawdata, -zlib.MAX_WBITS)
      except:
        import sys
        exctype, value = sys.exc_info()[:2]
        event=logging.IOError({"message": 'Server response declares Content-Encoding: deflate', "exception":value})
        raise ValidationFailure(event)

    if usock.headers.get('content-type', None) == 'application/vnd.google-earth.kmz':
      import tempfile, zipfile, os
      try:
        (fd, tempname) = tempfile.mkstemp()
        os.write(fd, rawdata)
        os.close(fd)
        zfd = zipfile.ZipFile(tempname)
        namelist = zfd.namelist()
        for name in namelist:
          if name.endswith('.kml'):
            rawdata = zfd.read(name)
        zfd.close()
        os.unlink(tempname)
      except:
        import sys
        value = sys.exc_info()[:1]
        event=logging.IOError({"message": 'Problem decoding KMZ', "exception":value})
        raise ValidationFailure(event)

    mediaType = None
    charset = None

    # Is the Content-Type correct?
    contentType = usock.headers.get('content-type', None)
    if contentType:
      (mediaType, charset) = mediaTypes.checkValid(contentType, loggedEvents)

    # Check for malformed HTTP headers
    for (h, v) in list(usock.headers.items()):
      if (h.find(' ') >= 0):
        loggedEvents.append(HttpProtocolError({'header': h}))

    selfURIs = [request.get_full_url()]
    baseURI = usock.geturl()
    if not baseURI in selfURIs: selfURIs.append(baseURI)

    # Get baseURI from content-location and/or redirect information
    if usock.headers.get('content-location', None):
      from urllib.parse import urljoin
      baseURI=urljoin(baseURI,usock.headers.get('content-location', ""))
    elif usock.headers.get('location', None):
      from urllib.parse import urljoin
      baseURI=urljoin(baseURI,usock.headers.get('location', ""))

    if not baseURI in selfURIs: selfURIs.append(baseURI)
    usock.close()
    usock = None

    mediaTypes.contentSniffing(mediaType, rawdata, loggedEvents)

    encoding, rawdata = xmlEncoding.decode(mediaType, charset, rawdata, loggedEvents, fallback='utf-8')

    if rawdata is None:
      return {'loggedEvents': loggedEvents}

    rawdata = rawdata.replace('\r\n', '\n').replace('\r', '\n') # normalize EOL
    validator = _validate(rawdata, firstOccurrenceOnly, loggedEvents, baseURI, encoding, selfURIs, mediaType=mediaType, groupEvents=groupEvents)
  
    # Warn about mismatches between media type and feed version
    if mediaType and validator.feedType:
      mediaTypes.checkAgainstFeedType(mediaType, validator.feedType, validator.loggedEvents)

    params = {"feedType":validator.feedType, "loggedEvents":validator.loggedEvents}
    if wantRawData:
      params['rawdata'] = rawdata
    return params

  finally:
    try:
      if usock: usock.close()
    except:
      pass

__all__ = ['base',
           'channel',
           'compatibility',
           'image',
           'item',
           'logging',
           'rdf',
           'root',
           'rss',
           'skipHours',
           'sniffPossibleFeed',
           'textInput',
           'util',
           'validators',
           'validateURL',
           'validateString']
