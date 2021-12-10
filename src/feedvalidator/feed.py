__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from .base import validatorBase
from .validators import *
from .logging import *
from .itunes import itunes_channel
from .extension import extension_feed

#
# Atom root element
#
class feed(validatorBase, extension_feed, itunes_channel):
  def getExpectedAttrNames(self):
    return [('urn:atom-extension:indexing', 'index')]

  def prevalidate(self):
    self.links = []
    self.validate_optional_attribute(('urn:atom-extension:indexing', 'index'), yesno)

  def missingElement(self, params):
    offset = [self.line - self.dispatcher.locator.getLineNumber(),
              self.col  - self.dispatcher.locator.getColumnNumber()]
    self.log(MissingElement(params), offset)

  def validate_metadata(self):
    if not 'title' in self.children:
      self.missingElement({"parent":self.name, "element":"title"})
    if not 'id' in self.children:
      self.missingElement({"parent":self.name, "element":"id"})
    if not 'updated' in self.children:
      self.missingElement({"parent":self.name, "element":"updated"})

    # complete feeds can only have current=self and no other links
    if 'fh_complete' in self.children:
      for link in self.links:
        if link.rel in link.rfc5005:
          if link.rel == "current":
            if link.href not in self.dispatcher.selfURIs:
              self.log(CurrentNotSelfInCompleteFeed({"rel":link.rel}))
          else:
            self.log(FeedRelInCompleteFeed({"rel":link.rel}))

    # ensure that there is a link rel="self"
    if self.name != 'source':
      for link in self.links:
        if link.rel=='self': break
      else:
        offset = [self.line - self.dispatcher.locator.getLineNumber(),
                  self.col  - self.dispatcher.locator.getColumnNumber()]
        self.log(MissingSelf({"parent":self.parent.name, "element":self.name}), offset)

    types={}
    archive=False
    current=False
    for link in self.links:
      if link.rel == 'current': current = True
      if link.rel in ['prev-archive', 'next-archive']: archive = True

      # attempts to link past the end of the list
      if link.rel == 'first' and link.href in self.dispatcher.selfURIs:
        for link2 in self.links:
          if link2.rel == 'previous':
              self.log(LinkPastEnd({"self":link.rel, "rel":link2.rel}))
      if link.rel == 'last' and link.href in self.dispatcher.selfURIs:
        for link2 in self.links:
          if link2.rel == 'next':
              self.log(LinkPastEnd({"self":link.rel, "rel":link2.rel}))

      # can only have one alternate per type
      if not link.rel=='alternate': continue
      if not link.type in types: types[link.type]={}
      if link.rel in types[link.type]:
        if link.hreflang in types[link.type][link.rel]:
          self.log(DuplicateAtomLink({"parent":self.name, "element":"link", "type":link.type, "hreflang":link.hreflang}))
        else:
          types[link.type][link.rel] += [link.hreflang]
      else:
        types[link.type][link.rel] = [link.hreflang]

    if 'fh_archive' in self.children:
      # archives should either have links or be marked complete
      if not archive and 'fh_complete' not in self.children:
        self.log(ArchiveIncomplete({}))

      # archives should have current links
      if not current and ('fh_complete' not in self.children):
        self.log(MissingCurrentInArchive({}))

    if self.itunes: itunes_channel.validate(self)

  def metadata(self):
    if 'entry' in self.children:
      self.log(MisplacedMetadata({"parent":self.name, "element":self.child}))

  def validate(self):
    entries = self.children.count('entry')
    dups = 0
    for event in self.dispatcher.loggedEvents:
      if isinstance(event,DuplicateEntries):
        dups += event.params.get('msgcount',1)
    if entries > 9 and entries == dups + 1:
      self.log(DuplicateIds({}))
      self.dispatcher.loggedEvents = [event
        for event in self.dispatcher.loggedEvents
        if not isinstance(event,DuplicateEntries)]

    if not 'entry' in self.children:
      self.validate_metadata()

  def do_author(self):
    self.metadata()
    from .author import author
    return author()

  def do_category(self):
    self.metadata()
    from .category import category
    return category()

  def do_contributor(self):
    self.metadata()
    from .author import author
    return author()

  def do_generator(self):
    self.metadata()
    from .generator import generator
    return generator(), nonblank(), noduplicates()

  def do_id(self):
    self.metadata()
    return canonicaluri(), nows(), noduplicates()

  def do_icon(self):
    self.metadata()
    return nonblank(), nows(), rfc2396(), noduplicates()

  def do_link(self):
    self.metadata()
    from .link import link
    self.links.append(link())
    return self.links[-1]

  def do_logo(self):
    self.metadata()
    return nonblank(), nows(), rfc2396(), noduplicates()

  def do_title(self):
    self.metadata()
    from .content import textConstruct
    return textConstruct(), noduplicates()

  def do_subtitle(self):
    self.metadata()
    from .content import textConstruct
    return textConstruct(), noduplicates()

  def do_rights(self):
    self.metadata()
    from .content import textConstruct
    return textConstruct(), noduplicates()

  def do_updated(self):
    self.metadata()
    return rfc3339(), nows(), noduplicates()

  def do_entry(self):
    if not 'entry' in self.children:
      self.validate_metadata()
    from .entry import entry
    return entry()

  def do_app_collection(self):
    from .service import collection
    return collection(), noduplicates()
