__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from .base import validatorBase, namespaces
from .validators import *
from .logging import *

def _isXhtmlDiv(ns, elem):
  return ns == 'http://www.w3.org/1999/xhtml' and elem == 'div'

#
# item element.
#
class textConstruct(rfc2396,nonhtml):
  from .validators import mime_re
  import re

  def getExpectedAttrNames(self):
      return [(None, 'type'),(None, 'src')]

  def normalizeWhitespace(self):
      pass

  def maptype(self):
    if self.type.find('/') > -1:
      self.log(InvalidTextType({"parent":self.parent.name, "element":self.name, "attr":"type", "value":self.type}))

  def prevalidate(self):
    nonhtml.start(self)
    if (None,"src") in self.attrs:
      self.type=''
    else:
      self.type='text'
      if self.getFeedType() == TYPE_RSS2 and self.name != 'atom_summary':
        self.log(DuplicateDescriptionSemantics({"element":self.name}))

    if (None,"type") in self.attrs:
      self.type=self.attrs.getValue((None,"type"))
      if not self.type:
        self.log(AttrNotBlank({"parent":self.parent.name, "element":self.name, "attr":"type"}))

    self.maptype()

    if (None,"src") in self.attrs:
      self.children.append(True) # force warnings about "mixed" content
      self.value=self.attrs.getValue((None,"src"))
      rfc2396.validate(self, errorClass=InvalidURIAttribute, extraParams={"attr": "src"})
      self.value=""

      if (None,"type") not in self.attrs:
        self.log(MissingTypeAttr({"parent":self.parent.name, "element":self.name, "attr":"type"}))

    if self.type in ['text','html','xhtml'] and (None,"src") not in self.attrs:
      pass
    elif self.type and not self.mime_re.match(self.type):
      self.log(InvalidMIMEType({"parent":self.parent.name, "element":self.name, "attr":"type", "value":self.type}))
    else:
      self.log(ValidMIMEAttribute({"parent":self.parent.name, "element":self.name, "attr":"type", "value":self.type}))

    if not self.xmlLang:
      self.log(MissingDCLanguage({"parent":self.name, "element":"xml:lang"}))

  def validate(self):
    if self.type in ['text','xhtml']:
      if self.type=='xhtml':
        nonhtml.validate(self, NotInline)
      else:
        nonhtml.validate(self, ContainsUndeclaredHTML)
    else:
      if self.type.find('/') > -1 and not (
         self.type.endswith('+xml') or self.type.endswith('/xml') or
         self.type.startswith('text/')):
        import base64
        try:
          self.value=base64.decodebytes(self.value.encode('us-ascii'))
          if self.type.endswith('/html'):
            self.type='html'
            self.value = self.value.decode('utf-8')
        except:
          self.log(NotBase64({"parent":self.parent.name, "element":self.name,"value":self.value}))

      if self.type=='html' or self.type.endswith("/html"):
        self.validateSafe(self.value)

        if self.type.endswith("/html"):
          if self.value.find("<html")<0 and (None,"src") not in self.attrs:
            self.log(HtmlFragment({"parent":self.parent.name, "element":self.name,"value":self.value, "type":self.type}))
      else:
        nonhtml.validate(self, ContainsUndeclaredHTML)

    if not self.value and len(self.children)==0 and (None,"src") not in self.attrs:
       self.log(NotBlank({"parent":self.parent.name, "element":self.name}))

  def textOK(self):
    if self.children: validatorBase.textOK(self)

  def characters(self, string):
    for c in string:
      if 0x80 <= ord(c) <= 0x9F or c == '\ufffd':
        from .validators import BadCharacters
        self.log(BadCharacters({"parent":self.parent.name, "element":self.name}))
    if (self.type=='xhtml') and string.strip() and not self.value.strip():
      self.log(MissingXhtmlDiv({"parent":self.parent.name, "element":self.name}))
    validatorBase.characters(self,string)

  def startElementNS(self, name, qname, attrs):
    if (self.type != 'xhtml') and not (
        self.type.endswith('+xml') or self.type.endswith('/xml')):
      self.log(UndefinedElement({"parent":self.name, "element":name}))

    if self.type=="xhtml":
      if not _isXhtmlDiv(qname, name) and not self.value.strip():
        self.log(MissingXhtmlDiv({"parent":self.parent.name, "element":self.name}))
        if name == 'div':
          self.log(NotHtml({"parent":self.parent.name, "element":self.name, "message":"unexpected namespace", "value": qname}))

      elif qname not in ["http://www.w3.org/1999/xhtml"]:
        self.log(NotHtml({"parent":self.parent.name, "element":self.name, "message":"unexpected namespace", "value": qname}))

    if self.type=="application/xhtml+xml":
      if name != 'html':
        self.log(HtmlFragment({"parent":self.parent.name, "element":self.name,"value":self.value, "type":self.type}))
      elif qname not in ["http://www.w3.org/1999/xhtml"]:
        self.log(NotHtml({"parent":self.parent.name, "element":self.name, "message":"unexpected namespace", "value":qname}))

    if (None,"mode") in self.attrs:
      if self.attrs.getValue((None,"mode")) == 'escaped':
        self.log(NotEscaped({"parent":self.parent.name, "element":self.name}))

    if _isXhtmlDiv(qname, name):
      handler=diveater()
    else:
      handler=eater()
    self.children.append(handler)
    self.push(handler, name, attrs)

# treat xhtml:div as part of the content for purposes of detecting escaped html
class diveater(eater):
  def __init__(self):
    eater.__init__(self)
    self.mixed = False
  def textOK(self):
    pass
  def characters(self, string):
    validatorBase.characters(self, string)
  def startElementNS(self, name, qname, attrs):
    if not qname:
      self.log(MissingNamespace({"parent":"xhtml:div", "element":name}))
    elif qname == 'http://www.w3.org/1999/xhtml':
      if name not in HTMLValidator.htmltags:
        self.log(NotHtml({'message':'Non-XHTML element', 'value':name}))
      elif name not in HTMLValidator.acceptable_elements:
        self.log(SecurityRisk({'tag':name}))
      for ns,attr in attrs.getNames():
        if not ns and attr not in HTMLValidator.acceptable_attributes:
          if attr == 'style':
            for value in checkStyle(attrs.get((ns,attr))):
              self.log(DangerousStyleAttr({"attr":attr, "value":value}))
          else:
            self.log(SecurityRiskAttr({'attr':attr}))
    elif qname == 'http://www.w3.org/2000/svg':
      if name not in HTMLValidator.svg_elements:
        self.log(SecurityRisk({'tag':name}))
      for ns,attr in attrs.getNames():
        if not ns and attr not in HTMLValidator.svg_attributes:
          self.log(SecurityRiskAttr({'attr':attr}))
    elif qname == 'http://www.w3.org/1998/Math/MathML':
      if name not in HTMLValidator.mathml_elements:
        self.log(SecurityRisk({'tag':name}))
      for ns,attr in attrs.getNames():
        if not ns and attr not in HTMLValidator.mathml_attributes:
          self.log(SecurityRiskAttr({'attr':attr}))
    elif qname in namespaces:
      if self.name != 'metadata':
        self.log(UndefinedElement({"parent": self.name, "element":namespaces[qname] + ":" + name}))
      self.push(eater(), name, attrs)
      return

    self.mixed = True
    eater.startElementNS(self, name, qname, attrs)
  def validate(self):
    if not self.mixed: self.parent.value += self.value

class content(textConstruct):
  def maptype(self):
    if self.type == 'multipart/alternative':
      self.log(InvalidMIMEType({"parent":self.parent.name, "element":self.name, "attr":"type", "value":self.type}))
