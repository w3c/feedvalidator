__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from .base import validatorBase
from .validators import *
from .logging import *
from .extension import extension_everywhere
import re

#
# Outline Processor Markup Language element.
#
class opml(validatorBase, extension_everywhere):
  versionList = ['1.0', '1.1', '2.0']

  def validate(self):
    self.setFeedType(TYPE_OPML)

    if (None,'version') in self.attrs.getNames():
      if self.attrs[(None,'version')] not in opml.versionList:
        self.log(InvalidOPMLVersion({"parent":self.parent.name, "element":self.name, "value":self.attrs[(None,'version')]}))
    elif self.name != 'outlineDocument':
      self.log(MissingAttribute({"parent":self.parent.name, "element":self.name, "attr":"version"}))

    if 'head' not in self.children:
      self.log(MissingElement({"parent":self.name, "element":"head"}))

    if 'body' not in self.children:
      self.log(MissingElement({"parent":self.name, "element":"body"}))

  def getExpectedAttrNames(self):
    return [(None, 'version')]

  def do_head(self):
    return opmlHead()

  def do_body(self):
    return opmlBody()

class opmlHead(validatorBase, extension_everywhere):
  def do_title(self):
    return safeHtml(), noduplicates()

  def do_dateCreated(self):
    return rfc822(), noduplicates()

  def do_dateModified(self):
    return rfc822(), noduplicates()

  def do_ownerName(self):
    return safeHtml(), noduplicates()

  def do_ownerEmail(self):
    return email(), noduplicates()

  def do_ownerId(self):
    return httpURL(), noduplicates()

  def do_expansionState(self):
    return commaSeparatedLines(), noduplicates()

  def do_vertScrollState(self):
    return positiveInteger(), nonblank(), noduplicates()

  def do_windowTop(self):
    return positiveInteger(), nonblank(), noduplicates()

  def do_windowLeft(self):
    return positiveInteger(), nonblank(), noduplicates()

  def do_windowBottom(self):
    return positiveInteger(), nonblank(), noduplicates()

  def do_windowRight(self):
    return positiveInteger(), nonblank(), noduplicates()

class commaSeparatedLines(text):
  linenumbers_re=re.compile('^(\d+(,\s*\d+)*)?$')
  def validate(self):
    if not self.linenumbers_re.match(self.value):
      self.log(InvalidExpansionState({"parent":self.parent.name, "element":self.name, "value":self.value}))

class opmlBody(validatorBase, extension_everywhere):

  def validate(self):
    if 'outline' not in self.children:
      self.log(MissingElement({"parent":self.name, "element":"outline"}))

  def do_outline(self):
    return opmlOutline()

class opmlOutline(validatorBase, extension_everywhere):
  versionList = ['RSS', 'RSS1', 'RSS2', 'scriptingNews']

  def getExpectedAttrNames(self):
    return [
      (None, 'category'),
      (None, 'created'),
      (None, 'description'),
      (None, 'htmlUrl'),
      (None, 'isBreakpoint'),
      (None, 'isComment'),
      (None, 'language'),
      (None, 'text'),
      (None, 'title'),
      (None, 'type'),
      (None, 'url'),
      (None, 'version'),
      (None, 'xmlUrl'),
    ]

  def validate(self):

    if not (None,'text') in self.attrs.getNames():
      self.log(MissingAttribute({"parent":self.parent.name, "element":self.name, "attr":"text"}))

    if (None,'type') in self.attrs.getNames():
      if self.attrs[(None,'type')].lower() == 'rss':

        if not (None,'xmlUrl') in self.attrs.getNames():
          self.log(MissingXmlURL({"parent":self.parent.name, "element":self.name}))
        if not (None,'title') in self.attrs.getNames():
          self.log(MissingTitleAttr({"parent":self.parent.name, "element":self.name}))

      elif self.attrs[(None,'type')].lower() == 'link':

        if not (None,'url') in self.attrs.getNames():
          self.log(MissingUrlAttr({"parent":self.parent.name, "element":self.name}))

      else:

        opml = self.parent
        while opml and opml.name != 'opml':
            opml = opml.parent

        if opml and opml.attrs.get((None,'version')).startswith('1.'):
            self.log(InvalidOutlineType({"parent":self.parent.name, "element":self.name, "value":self.attrs[(None,'type')]}))

    if (None,'version') in self.attrs.getNames():
      if self.attrs[(None,'version')] not in opmlOutline.versionList:
        self.log(InvalidOutlineVersion({"parent":self.parent.name, "element":self.name, "value":self.attrs[(None,'version')]}))

    if len(self.attrs)>1 and not (None,'type') in self.attrs.getNames():
      for name in 'description htmlUrl language title version xmlUrl'.split():
        if (None, name) in self.attrs.getNames():
          self.log(MissingOutlineType({"parent":self.parent.name, "element":self.name}))
          break

    self.validate_optional_attribute((None,'created'), rfc822)
    self.validate_optional_attribute((None,'description'), safeHtml)
    self.validate_optional_attribute((None,'htmlUrl'), rfc2396_full)
    self.validate_optional_attribute((None,'isBreakpoint'), truefalse)
    self.validate_optional_attribute((None,'isComment'), truefalse)
    self.validate_optional_attribute((None,'language'), iso639)
    self.validate_optional_attribute((None,'title'), safeHtml)
    self.validate_optional_attribute((None,'text'), safeHtml)
    self.validate_optional_attribute((None,'url'), rfc2396_full)

  def characters(self, string):
    if not self.value:
      if string.strip():
        self.log(UnexpectedText({"element":self.name,"parent":self.parent.name}))
        self.value = string

  def do_outline(self):
    return opmlOutline()
