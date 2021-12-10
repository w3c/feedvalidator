__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from xml.sax.handler import ContentHandler
from xml.sax.xmlreader import Locator
from .logging import NonCanonicalURI, NotUTF8
import re

# references:
# http://web.resource.org/rss/1.0/modules/standard.html
# http://web.resource.org/rss/1.0/modules/proposed.html
# http://dmoz.org/Reference/Libraries/Library_and_Information_Science/Technical_Services/Cataloguing/Metadata/RDF/Applications/RSS/Specifications/RSS1.0_Modules/
namespaces = {
  "http://www.bloglines.com/about/specs/fac-1.0":   "access",
  "http://webns.net/mvcb/":                         "admin",
  "http://purl.org/rss/1.0/modules/aggregation/":   "ag",
  "http://purl.org/rss/1.0/modules/annotate/":      "annotate",
  "http://www.w3.org/2007/app":                     "app",
  "http://media.tangent.org/rss/1.0/":              "audio",
  "http://backend.userland.com/blogChannelModule":  "blogChannel",
  "http://web.resource.org/cc/":                    "cc",
  "http://www.microsoft.com/schemas/rss/core/2005": "cf",
  "http://backend.userland.com/creativeCommonsRssModule": "creativeCommons",
  "http://purl.org/rss/1.0/modules/company":        "company",
  "http://purl.org/rss/1.0/modules/content/":       "content",
  "http://conversationsnetwork.org/rssNamespace-1.0/": "conversationsNetwork",
  "http://my.theinfo.org/changed/1.0/rss/":         "cp",
  "http://purl.org/dc/elements/1.1/":               "dc",
  "http://purl.org/dc/terms/":                      "dcterms",
  "http://purl.org/rss/1.0/modules/email/":         "email",
  "http://purl.org/rss/1.0/modules/event/":         "ev",
  "http://purl.org/syndication/history/1.0":        "fh",
  "http://www.w3.org/2003/01/geo/wgs84_pos#":       "geo",
  "http://geourl.org/rss/module/":                  "geourl",
  "http://www.georss.org/georss":                   "georss",
  "http://www.opengis.net/gml":                     "gml",
  "http://postneo.com/icbm":                        "icbm",
  "http://purl.org/rss/1.0/modules/image/":         "image",
  "urn:atom-extension:indexing":                    "indexing",
  "http://www.itunes.com/dtds/podcast-1.0.dtd":     "itunes",
  "http://rssnamespace.org/feedburner/ext/1.0":     "feedburner",
  "http://xmlns.com/foaf/0.1/":                     "foaf",
  "http://purl.org/rss/1.0/modules/link/":          "l",
  "http://search.yahoo.com/mrss/":                  "media",
  "http://www.w3.org/1998/Math/MathML":             "mathml",
  "http://a9.com/-/spec/opensearchrss/1.0/":        "opensearch10",
  "http://a9.com/-/spec/opensearch/1.1/":           "opensearch",
  "http://www.opml.org/spec2":                      "opml",
  "http://www.w3.org/1999/02/22-rdf-syntax-ns#":    "rdf",
  "http://www.w3.org/2000/01/rdf-schema#":          "rdfs",
  "http://purl.org/rss/1.0/modules/reference/":     "ref",
  "http://purl.org/rss/1.0/modules/richequiv/":     "reqv",
  "http://purl.org/rss/1.0/modules/rss091#":        "rss091",
  "http://purl.org/rss/1.0/modules/search/":        "search",
  "http://purl.org/rss/1.0/modules/slash/":         "slash",
  "http://purl.org/rss/1.0/modules/servicestatus/": "ss",
  "http://hacks.benhammersley.com/rss/streaming/":  "str",
  "http://purl.org/rss/1.0/modules/subscription/":  "sub",
  "http://feedsync.org/2007/feedsync":              "sx",
  "http://www.w3.org/2000/svg":                     "svg",
  "http://purl.org/rss/1.0/modules/syndication/":   "sy",
  "http://purl.org/rss/1.0/modules/taxonomy/":      "taxo",
  "http://purl.org/rss/1.0/modules/threading/":     "thr",
  "http://purl.org/syndication/thread/1.0":         "thr",
  "http://madskills.com/public/xml/rss/module/trackback/": "trackback",
  "http://wellformedweb.org/CommentAPI/":           "wfw",
  "http://purl.org/rss/1.0/modules/wiki/":          "wiki",
  "http://www.usemod.com/cgi-bin/mb.pl?ModWiki":    "wiki",
  "http://schemas.xmlsoap.org/soap/envelope/":      "soap",
  "http://www.w3.org/2005/Atom":                    "atom",
  "http://www.w3.org/1999/xhtml":                   "xhtml",
  "http://my.netscape.com/rdf/simple/0.9/":         "rss090",
  "http://purl.org/rss/1.0/":                       "rss1",
  "http://purl.org/net/rss1.1#":                    "rss11",
  "http://base.google.com/ns/1.0":                  "g",
  "http://www.w3.org/XML/1998/namespace":           "xml",
  "http://openid.net/xmlns/1.0":                    "openid",
  "http://earth.google.com/kml/2.0":                "kml20",
  "http://earth.google.com/kml/2.1":                "kml21",
  "http://www.opengis.net/kml/2.2":                 "kml22",
  "http://www.w3.org/1999/xlink":                   "xlink",
  "xri://$xrd*($v*2.0)":                            "xrd",
  "xri://$xrds":                                    "xrds",
}

unsupported_namespaces = {
  "http://schemas.google.com/g/2005": ("Google Data", "https://developers.google.com/gdata/docs/1.0/elements"),
  "http://www.rawvoice.com/rawvoiceRssModule/":	("RawVoice", "http://www.rawvoice.com/services/tools-and-resources/rawvoice-rss-2-0-module-xmlns-namespace-rss2/")
}

def near_miss(ns):
  try:
    return re.match(".*\w", ns).group().lower()
  except:
    return ns

nearly_namespaces = dict([(near_miss(u),p) for u,p in list(namespaces.items())])

stdattrs = [('http://www.w3.org/XML/1998/namespace', 'base'),
            ('http://www.w3.org/XML/1998/namespace', 'id'),
            ('http://www.w3.org/XML/1998/namespace', 'lang'),
            ('http://www.w3.org/XML/1998/namespace', 'space')]

#
# From the SAX parser's point of view, this class is the one responsible for
# handling SAX events.  In actuality, all this class does is maintain a
# pushdown stack of the *real* content handlers, and delegates sax events
# to the current one.
#
class SAXDispatcher(ContentHandler):

  firstOccurrenceOnly = 0
  groupEvents = 0

  def __init__(self, base, selfURIs, encoding):
    from .root import root
    ContentHandler.__init__(self)
    self.lastKnownLine = 1
    self.lastKnownColumn = 0
    self.loggedEvents = []
    self.feedType = 0
    try:
       self.xmlBase = base.encode('idna').decode('utf-8')
    except:
       self.xmlBase = base
    self.selfURIs = selfURIs
    self.encoding = encoding
    self.handler_stack=[[root(self, base)]]
    self.defaultNamespaces = []

    # experimental RSS-Profile support
    self.rssCharData = []

  def setDocumentLocator(self, locator):
    self.locator = locator
    ContentHandler.setDocumentLocator(self, self.locator)

  def setFirstOccurrenceOnly(self, firstOccurrenceOnly=1):
    self.firstOccurrenceOnly = firstOccurrenceOnly

  def setGroupEvents(self, groupEvents=1):
    self.groupEvents = groupEvents

  def startPrefixMapping(self, prefix, uri):
    for handler in iter(self.handler_stack[-1]):
      handler.namespace[prefix] = uri
    if uri and len(uri.split())>1:
      from xml.sax import SAXException
      self.error(SAXException('Invalid Namespace: %s' % uri))
    if prefix in list(namespaces.values()):
      if not namespaces.get(uri,'') == prefix and prefix:
        from .logging import ReservedPrefix, MediaRssNamespace
        preferredURI = [key for key, value in list(namespaces.items()) if value == prefix][0]
        if uri == 'http://search.yahoo.com/mrss':
          self.log(MediaRssNamespace({'prefix':prefix, 'ns':preferredURI}))
        else:
          self.log(ReservedPrefix({'prefix':prefix, 'ns':preferredURI}))
      elif prefix=='wiki' and uri.find('usemod')>=0:
        from .logging import ObsoleteWikiNamespace
        self.log(ObsoleteWikiNamespace({'preferred':namespaces[uri], 'ns':uri}))
      elif prefix in ['atom','xhtml']:
        from .logging import TYPE_ATOM, AvoidNamespacePrefix
        if self.getFeedType() == TYPE_ATOM:
          self.log(AvoidNamespacePrefix({'prefix':prefix}))
    elif uri in namespaces:
      if not namespaces[uri] == prefix and prefix:
        from .logging import NonstdPrefix
        self.log(NonstdPrefix({'preferred':namespaces[uri], 'ns':uri}))
        if namespaces[uri] in ['atom', 'xhtml']:
          from .logging import TYPE_UNKNOWN, TYPE_ATOM, AvoidNamespacePrefix
          if self.getFeedType() in [TYPE_ATOM,TYPE_UNKNOWN]:
            self.log(AvoidNamespacePrefix({'prefix':prefix}))
    elif uri == 'http://search.yahoo.com/mrss':
      from .logging import MediaRssNamespace
      uri = 'http://search.yahoo.com/mrss/'
      self.log(MediaRssNamespace({'prefix':prefix, 'ns':uri}))
    else:
      from .validators import rfc3987
      rule=rfc3987()
      rule.setElement('xmlns:'+str(prefix), {}, self.handler_stack[-1][0])
      rule.value=uri
      if not uri or rule.validate():
        if uri in unsupported_namespaces:
          from .logging import UnsupportedNamespace
          (name, specification) = unsupported_namespaces[uri]
          self.log(UnsupportedNamespace({'namespace': uri, 'name': name, 'specification': specification}))
        else:
          from .logging import UnknownNamespace
          self.log(UnknownNamespace({'namespace':uri}))

  def namespaceFor(self, prefix):
    return None

  def startElementNS(self, name, qname, attrs):
    self.lastKnownLine = self.locator.getLineNumber()
    self.lastKnownColumn = self.locator.getColumnNumber()
    qname, name = name
    for handler in iter(self.handler_stack[-1]):
      handler.startElementNS(name, qname, attrs)

    if len(attrs):
      present = attrs.getNames()
      unexpected = [x for x in present if x not in stdattrs]
      for handler in iter(self.handler_stack[-1]):
        ean = handler.getExpectedAttrNames()
        if ean: unexpected = [x for x in unexpected if x not in ean]
      for u in unexpected:
        if u[0] and near_miss(u[0]) not in nearly_namespaces:
          feedtype=self.getFeedType()
          if (not qname) and feedtype and (feedtype==TYPE_RSS2):
            from .logging import UseOfExtensionAttr
            self.log(UseOfExtensionAttr({"attribute":u, "element":name}))
          continue
        from .logging import UnexpectedAttribute
        if not u[0]: u=u[1]
        self.log(UnexpectedAttribute({"parent":name, "attribute":u, "element":name}))

  def resolveEntity(self, publicId, systemId):
    if not publicId and not systemId:
      import io
      return io.StringIO()

    try:
      def log(exception):
        from .logging import SAXError
        self.log(SAXError({'exception':str(exception)}))
      if self.xmlvalidator:
        self.xmlvalidator(log)
      self.xmlvalidator=0
    except:
      pass

    if (publicId=='-//Netscape Communications//DTD RSS 0.91//EN' and
        systemId=='http://my.netscape.com/publish/formats/rss-0.91.dtd'):
      from .logging import ValidDoctype, DeprecatedDTD
      self.log(ValidDoctype({}))
      self.log(DeprecatedDTD({}))
    elif (publicId=='-//Netscape Communications//DTD RSS 0.91//EN' and
        systemId=='http://www.rssboard.org/rss-0.91.dtd'):
      from .logging import ValidDoctype
      self.log(ValidDoctype({}))
    else:
      from .logging import ContainsSystemEntity
      self.lastKnownLine = self.locator.getLineNumber()
      self.lastKnownColumn = self.locator.getColumnNumber()
      self.log(ContainsSystemEntity({}))
    from io import StringIO
    return StringIO()

  def skippedEntity(self, name):
    from .logging import ValidDoctype
    if [e for e in self.loggedEvents if e.__class__ == ValidDoctype]:
      from html.entities import name2codepoint
      if name in name2codepoint: return
    from .logging import UndefinedNamedEntity
    self.log(UndefinedNamedEntity({'value':name}))

  def characters(self, string):
    self.lastKnownLine = self.locator.getLineNumber()
    self.lastKnownColumn = self.locator.getColumnNumber()
    for handler in iter(self.handler_stack[-1]):
      handler.characters(string)

  def endElementNS(self, name, qname):
    self.lastKnownLine = self.locator.getLineNumber()
    self.lastKnownColumn = self.locator.getColumnNumber()
    qname, name = name
    for handler in iter(self.handler_stack[-1]):
      handler.endElementNS(name, qname)
    del self.handler_stack[-1]

  def push(self, handlers, name, attrs, parent):
    if hasattr(handlers,'__iter__'):
      for handler in iter(handlers):
        handler.setElement(name, attrs, parent)
        handler.value=""
        handler.prevalidate()
    else:
      handlers.setElement(name, attrs, parent)
      handlers.value=""
      handlers.prevalidate()
      handlers = [handlers]
    self.handler_stack.append(handlers)

  def log(self, event, offset=(0,0)):
    def findDuplicate(self, event):
      duplicates = [e for e in self.loggedEvents if e.__class__ == event.__class__]
      if duplicates and (event.__class__ in [NonCanonicalURI]):
        return duplicates[0]

      for dup in duplicates:
        for k, v in list(event.params.items()):
          if k != 'value':
            if not k in dup.params or dup.params[k] != v: break
        else:
          return dup

    if 'element' in event.params and event.params['element']:
      if not isinstance(event.params['element'],tuple):
        event.params['element']=':'.join(event.params['element'].split('_', 1))
      elif event.params['element'][0]=='http://www.w3.org/XML/1998/namespace':
        event.params['element'] = 'xml:' + event.params['element'][-1]
    if self.firstOccurrenceOnly:
      dup = findDuplicate(self, event)
      if dup:
        dup.params['msgcount'] = dup.params['msgcount'] + 1
        return
      event.params['msgcount'] = 1
    if self.groupEvents:
      dup = findDuplicate(self, event)
    try:
      line = self.locator.getLineNumber() + offset[0]
      backupline = self.lastKnownLine
      column = (self.locator.getColumnNumber() or 0) + offset[1]
      backupcolumn = self.lastKnownColumn
    except AttributeError:
      line = backupline = column = backupcolumn = 1
    event.params['line'] = line
    event.params['backupline'] = backupline
    event.params['column'] = column
    event.params['backupcolumn'] = backupcolumn
    if self.groupEvents and dup:
      if 'duplicates' in dup.params:
        dup.params['duplicates'].append(event)
      else:
        dup.params['duplicates'] = []
        dup.params['duplicates'].append(event)
      return
    self.loggedEvents.append(event)

  def error(self, exception):
    from .logging import SAXError
    self.log(SAXError({'exception':str(exception)}))
    raise exception
  fatalError=error
  warning=error

  def getFeedType(self):
    return self.feedType

  def setFeedType(self, feedType):
    self.feedType = feedType

#
# This base class for content handlers keeps track of such administrative
# details as the parent of the current element, and delegating both log
# and push events back up the stack.  It will also concatenate up all of
# the SAX events associated with character data into a value, handing such
# things as CDATA and entities.
#
# Subclasses are expected to declare "do_name" methods for every
# element that they support.  These methods are expected to return the
# appropriate handler for the element.
#
# The name of the element and the names of the children processed so
# far are also maintained.
#
# Hooks are also provided for subclasses to do "prevalidation" and
# "validation".
#
from .logging import TYPE_RSS2

class validatorBase(ContentHandler):

  def __init__(self):
    ContentHandler.__init__(self)
    self.value = ""
    self.attrs = None
    self.children = []
    self.isValid = 1
    self.name = None
    self.itunes = False
    self.namespace = {}

  def setElement(self, name, attrs, parent):
    self.name = name
    self.attrs = attrs
    self.parent = parent
    self.dispatcher = parent.dispatcher
    self.line = self.dispatcher.locator.getLineNumber()
    self.col  = self.dispatcher.locator.getColumnNumber()
    self.xmlLang = parent.xmlLang

    if attrs and ('http://www.w3.org/XML/1998/namespace', 'base') in attrs:
      self.xmlBase=attrs.getValue(('http://www.w3.org/XML/1998/namespace', 'base'))
      from .validators import rfc3987
      self.validate_attribute(('http://www.w3.org/XML/1998/namespace','base'),
          rfc3987)
      from urllib.parse import urljoin
      self.xmlBase = urljoin(parent.xmlBase, self.xmlBase)
    else:
      self.xmlBase = parent.xmlBase

    return self

  def simplename(self, name):
    if not name[0]: return name[1]
    return namespaces.get(name[0], name[0]) + ":" + name[1]

  def namespaceFor(self, prefix):
    if prefix in self.namespace:
      return self.namespace[prefix]
    elif self.parent:
      return self.parent.namespaceFor(prefix)
    else:
      return None

  def validate_attribute(self, name, rule):
    if not isinstance(rule,validatorBase): rule = rule()
    if isinstance(name,str): name = (None,name)
    rule.setElement(self.simplename(name), {}, self)
    rule.value=self.attrs.getValue(name)
    rule.validate()

  def validate_required_attribute(self, name, rule):
    if self.attrs and name in self.attrs:
      self.validate_attribute(name, rule)
    else:
      from .logging import MissingAttribute
      self.log(MissingAttribute({"attr": self.simplename(name)}))

  def validate_optional_attribute(self, name, rule):
    if self.attrs and name in self.attrs:
      self.validate_attribute(name, rule)

  def getExpectedAttrNames(self):
    None

  def unknown_starttag(self, name, qname, attrs):
    from .validators import any
    return any(self, name, qname, attrs)

  def startElementNS(self, name, qname, attrs):
    if ('http://www.w3.org/XML/1998/namespace', 'lang') in attrs:
      self.xmlLang=attrs.getValue(('http://www.w3.org/XML/1998/namespace', 'lang'))
      if self.xmlLang:
        from .validators import iso639_validate
        iso639_validate(self.log, self.xmlLang, "xml:lang", name)

    from .validators import eater
    feedtype=self.getFeedType()
    if (not qname) and feedtype and (feedtype != TYPE_RSS2):
       from .logging import UndeterminableVocabulary
       self.log(UndeterminableVocabulary({"parent":self.name, "element":name, "namespace":'""'}))
       qname="null"
    if qname in self.dispatcher.defaultNamespaces: qname=None

    nm_qname = near_miss(qname)
    if nm_qname in nearly_namespaces:
      prefix = nearly_namespaces[nm_qname]
      qname, name = None, prefix + "_" + name
      if prefix == 'itunes' and not self.itunes and not self.parent.itunes:
        if hasattr(self, 'setItunes'): self.setItunes(True)

    # ensure all attribute namespaces are properly defined
    for (namespace,attr) in list(attrs.keys()):
      if ':' in attr and not namespace:
        from .logging import MissingNamespace
        self.log(MissingNamespace({"parent":self.name, "element":attr}))

    if qname=='http://purl.org/atom/ns#':
      from .logging import ObsoleteNamespace
      self.log(ObsoleteNamespace({"element":"feed"}))

    for key, string in list(attrs.items()):
      for c in string:
        if 0x80 <= ord(c) <= 0x9F or c == '\ufffd':
          from .validators import BadCharacters
          self.log(BadCharacters({"parent":name, "element":key[-1]}))

    if qname:
      handler = self.unknown_starttag(name, qname, attrs)
      name="unknown_"+name
      self.child=name
    else:
      try:
        self.child=name
        if name.startswith('dc_'):
          # handle "Qualified" Dublin Core
          handler = getattr(self, "do_" + name.replace("-","_").split('.')[0])()
        else:
          handler = getattr(self, "do_" + name.replace("-","_"))()
      except AttributeError:
        if name.find(':') != -1:
          from .logging import MissingNamespace
          self.log(MissingNamespace({"parent":self.name, "element":name}))
          handler = eater()
        elif name.startswith('xhtml_'):
          from .logging import MisplacedXHTMLContent
          self.log(MisplacedXHTMLContent({"parent": ':'.join(self.name.split("_",1)), "element":name}))
          handler = eater()
        else:
          try:
            from .extension import Questionable

            # requalify the name with the default namespace
            qname = name
            from .logging import TYPE_APP_CATEGORIES, TYPE_APP_SERVICE
            if self.getFeedType() in [TYPE_APP_CATEGORIES, TYPE_APP_SERVICE]:
              if qname.startswith('app_'): qname=qname[4:]

            if name.find('_')<0 and self.name.find('_')>=0:
              if 'http://www.w3.org/2005/Atom' in self.dispatcher.defaultNamespaces:
                qname='atom_'+qname

            # is this element questionable?
            handler = getattr(Questionable(), "do_" + qname.replace("-","_"))()
            from .logging import QuestionableUsage
            self.log(QuestionableUsage({"parent": ':'.join(self.name.split("_",1)), "element":qname}))

          except AttributeError:
            from .logging import UndefinedElement
            self.log(UndefinedElement({"parent": ':'.join(self.name.split("_",1)), "element":name}))
            handler = eater()

    self.push(handler, name, attrs)

     # MAP - always append name, even if already exists (we need this to
     # check for too many hour elements in skipHours, and it doesn't
     # hurt anything else)
    self.children.append(self.child)

  def normalizeWhitespace(self):
    self.value = self.value.strip()

  def endElementNS(self, name, qname):
    self.normalizeWhitespace()
    self.validate()
    if self.isValid and self.name:
      from .validators import ValidElement
      self.log(ValidElement({"parent":self.parent.name, "element":name}))

  def textOK(self):
    from .validators import UnexpectedText
    self.log(UnexpectedText({"element":self.name,"parent":self.parent.name}))

  def characters(self, string):
    if string.strip(): self.textOK()

    line=column=0
    pc=' '
    for c in string:

      # latin characters double encoded as utf-8
      if 0x80 <= ord(c) <= 0xBF:
        if 0xC2 <= ord(pc) <= 0xC3:
          try:
            string.encode('iso-8859-1').decode('utf-8')
            from .validators import BadCharacters
            self.log(BadCharacters({"parent":self.parent.name, "element":self.name}), offset=(line,max(1,column-1)))
          except:
            pass
      pc = c

      # win1252
      if 0x80 <= ord(c) <= 0x9F or c == '\ufffd':
        from .validators import BadCharacters
        self.log(BadCharacters({"parent":self.parent.name, "element":self.name}), offset=(line,column))
      column=column+1
      if ord(c) in (10,13):
        column=0
        line=line+1

    self.value = self.value + string

  def log(self, event, offset=(0,0)):
    if 'element' not in event.params:
      event.params['element'] = self.name
    self.dispatcher.log(event, offset)
    self.isValid = 0

  def setFeedType(self, feedType):
    self.dispatcher.setFeedType(feedType)

  def getFeedType(self):
    return self.dispatcher.getFeedType()

  def push(self, handler, name, value):
    self.dispatcher.push(handler, name, value, self)

  def leaf(self):
    from .validators import text
    return text()

  def prevalidate(self):
    pass

  def validate(self):
    pass
