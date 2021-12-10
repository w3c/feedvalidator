__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from .base import validatorBase
from .validators import *

#
# Atom link element
#
class link(nonblank,xmlbase,iso639,nonhtml,nonNegativeInteger,rfc3339):
  validRelations = [
    # http://www.iana.org/assignments/link-relations.html
    'alternate',    # RFC4287
    'current',      # RFC5005
    'describedby',  # http://www.w3.org/TR/powder-dr/#assoc-linking
    'edit',         # RFC-ietf-atompub-protocol-17.txt
    'edit-media',   # RFC-ietf-atompub-protocol-17.txt
    'enclosure',    # RFC4287
    'first',        # RFC5005
    'hub',          # http://pubsubhubbub.googlecode.com/
    'last',         # RFC5005
    'license',      # RFC4946
    'next',         # RFC5005
    'next-archive', # RFC5005
    'payment',      # Kinberg
    'prev-archive', # RFC5005
    'previous',     # RFC5005
    'related',      # RFC4287
    'replies',      # RFC4685
    'search',       # http://www.opensearch.org/Specifications/OpenSearch/1.1
    'self',         # RFC4287
    'service',      # Snell
    'up',           # Slater
    'via'           # RFC4287
    ]

  rfc5005 = [
    'current',      # RFC5005
    'first',        # RFC5005
    'last',         # RFC5005
    'next',         # RFC5005
    'next-archive', # RFC5005
    'prev-archive', # RFC5005
    'previous',     # RFC5005
    ]

  def getExpectedAttrNames(self):
    return [(None, 'type'), (None, 'title'), (None, 'rel'),
      (None, 'href'), (None, 'length'), (None, 'hreflang'),
      ('http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'type'),
      ('http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'resource'),
      ('http://purl.org/syndication/thread/1.0', 'count'),
      ('http://purl.org/syndication/thread/1.0', 'when'),
      ('http://purl.org/syndication/thread/1.0', 'updated')]

  def validate(self):
    self.type = ""
    self.rel = "alternate"
    self.href = ""
    self.hreflang = ""
    self.title = ""

    if (None, "rel") in self.attrs:
      self.value = self.rel = self.attrs.getValue((None, "rel"))

      if self.rel.startswith('http://www.iana.org/assignments/relation/'):
        self.rel=self.rel[len('http://www.iana.org/assignments/relation/'):]

      if self.rel in self.validRelations:
        self.log(ValidAtomLinkRel({"parent":self.parent.name, "element":self.name, "attr":"rel", "value":self.rel}))
      elif rfc2396_full.rfc2396_re.match(self.rel.encode('idna').decode('utf-8')):
        self.log(ValidAtomLinkRel({"parent":self.parent.name, "element":self.name, "attr":"rel", "value":self.rel}))
      else:
        self.log(UnregisteredAtomLinkRel({"parent":self.parent.name, "element":self.name, "attr":"rel", "value":self.rel}))
      nonblank.validate(self, errorClass=AttrNotBlank, extraParams={"attr": "rel"})

      if self.rel in self.rfc5005 and self.parent.name == 'entry':
        self.log(FeedHistoryRelInEntry({"rel":self.rel}))

    if (None, "type") in self.attrs:
      self.value = self.type = self.attrs.getValue((None, "type"))
      if not mime_re.match(self.type):
        self.log(InvalidMIMEType({"parent":self.parent.name, "element":self.name, "attr":"type", "value":self.type}))
      elif self.rel == "self" and self.type not in ["application/atom+xml", "application/rss+xml", "application/rdf+xml"]:
        self.log(SelfNotAtom({"parent":self.parent.name, "element":self.name, "attr":"type", "value":self.type}))
      else:
        self.log(ValidMIMEAttribute({"parent":self.parent.name, "element":self.name, "attr":"type", "value":self.type}))

    if (None, "title") in self.attrs:
      self.log(ValidTitle({"parent":self.parent.name, "element":self.name, "attr":"title"}))
      self.value = self.title = self.attrs.getValue((None, "title"))
      nonblank.validate(self, errorClass=AttrNotBlank, extraParams={"attr": "title"})
      nonhtml.validate(self)

    if (None, "length") in self.attrs:
      self.name = 'length'
      self.value = self.attrs.getValue((None, "length"))
      nonNegativeInteger.validate(self)
      nonblank.validate(self)

    if (None, "hreflang") in self.attrs:
      self.name = 'hreflang'
      self.value = self.hreflang = self.attrs.getValue((None, "hreflang"))
      iso639.validate(self)

    if (None, "href") in self.attrs:
      self.name = 'href'
      self.value = self.href = self.attrs.getValue((None, "href"))
      xmlbase.validate(self, extraParams={"attr": "href"})

      if self.rel == "self" and self.parent.name in ["feed","channel"]:

        # detect relative self values
        from urllib.parse import urlparse
        from xml.dom import XML_NAMESPACE
        absolute = urlparse(self.href)[1]
        element = self
        while not absolute and element and hasattr(element,'attrs'):
          pattrs = element.attrs
          if pattrs and (XML_NAMESPACE, 'base') in pattrs:
            absolute=urlparse(pattrs.getValue((XML_NAMESPACE, 'base')))[1]
          element = element.parent
        if not absolute:
          self.log(RelativeSelf({"value":self.href}))

        from urllib.parse import urljoin
        if urljoin(self.xmlBase,self.value) not in self.dispatcher.selfURIs:
          if urljoin(self.xmlBase,self.value).split('#')[0] != self.xmlBase.split('#')[0]:
            from .uri import Uri
            if self.value.startswith('http://feeds.feedburner.com/'):
              if self.value.endswith('?format=xml'):
                self.value = self.value.split('?')[0]
            value = Uri(self.value)
            for docbase in self.dispatcher.selfURIs:
              if value == Uri(docbase): break

              # don't complain when validating feedburner's xml view
              if docbase.startswith('http://feeds.feedburner.com/'):
                if docbase.endswith('?format=xml'):
                  if value == Uri(docbase.split('?')[0]): break
            else:
              self.log(SelfDoesntMatchLocation({"parent":self.parent.name, "element":self.name}))
              self.dispatcher.selfURIs.append(urljoin(self.xmlBase,self.value))

    else:
      self.log(MissingHref({"parent":self.parent.name, "element":self.name, "attr":"href"}))

    if ('http://purl.org/syndication/thread/1.0', 'count') in self.attrs:
      if self.rel != "replies":
        self.log(UnexpectedAttribute({"parent":self.parent.name, "element":self.name, "attribute":"thr:count"}))
      self.value = self.attrs.getValue(('http://purl.org/syndication/thread/1.0', 'count'))
      self.name="thr:count"
      nonNegativeInteger.validate(self)

    if ('http://purl.org/syndication/thread/1.0', 'when') in self.attrs:
        self.log(NoThrWhen({"parent":self.parent.name, "element":self.name, "attribute":"thr:when"}))

    if ('http://purl.org/syndication/thread/1.0', 'updated') in self.attrs:
      if self.rel != "replies":
        self.log(UnexpectedAttribute({"parent":self.parent.name, "element":self.name, "attribute":"thr:updated"}))
      self.value = self.attrs.getValue(('http://purl.org/syndication/thread/1.0', 'updated'))
      self.name="thr:updated"
      rfc3339.validate(self)

  def startElementNS(self, name, qname, attrs):
    self.push(eater(), name, attrs)

  def characters(self, text):
    if text.strip():
      self.log(AtomLinkNotEmpty({"parent":self.parent.name, "element":self.name}))
