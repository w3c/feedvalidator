from .base import validatorBase
from .validators import *
from .logging import InvalidSseType, InvalidNSS, MissingElement, MissingByAndWhenAttrs
import re

class Sharing(validatorBase):
  def getExpectedAttrNames(self):
    return [ (None, 'expires'), (None, 'since'), (None, 'until') ]

  def prevalidate(self):
    if (None,'until') in self.attrs:
      self.validate_required_attribute((None,'since'), rfc3339)
    else:
      self.validate_optional_attribute((None,'since'), rfc3339)

    if (None,'since') in self.attrs:
      self.validate_required_attribute((None,'until'), rfc3339)
    else:
      self.validate_optional_attribute((None,'until'), rfc3339)

    self.validate_optional_attribute((None,'expires'), rfc3339)

    if (None,'since') in self.attrs:
      if (None,'until') in self.attrs:
        if self.attrs[(None,'since')]>self.attrs[(None,'until')]:
          self.log(SinceAfterUntil({}))

  def do_sx_related(self):
    return Related()

class Sync(validatorBase):
  def getExpectedAttrNames(self):
    return [ (None, 'deleted'), (None, 'noconflicts'),
             (None, 'id'), (None, 'updates') ]

  def prevalidate(self):
    self.validate_optional_attribute((None,'deleted'), truefalsestrict)
    self.validate_optional_attribute((None,'noconflicts'), truefalsestrict)
    self.validate_required_attribute((None,'id'), unique('id',self.parent.parent))
    self.validate_optional_attribute((None,'id'), rfc2141_nss)
    self.validate_required_attribute((None,'updates'), UINT31)

  def validate(self):
    if not 'sx_history' in self.children:
      self.log(MissingElement({'parent':self.name, 'element':'sx:history'}))

  def do_sx_history(self):
    return History()

  def do_sx_conflicts(self):
    return Conflicts()

class Related(validatorBase):
  def getExpectedAttrNames(self):
    return [ (None, 'link'), (None, 'title'), (None, 'type') ]

  def prevalidate(self):
    self.validate_required_attribute((None,'link'), rfc2396_full)
    self.validate_optional_attribute((None,'title'), nonhtml)
    self.validate_optional_attribute((None,'title'), nonblank)
    self.validate_required_attribute((None,'type'), FeedType)

class History(validatorBase):
  def getExpectedAttrNames(self):
    return [ (None, 'by'), (None, 'sequence'), (None, 'when') ]

  def prevalidate(self):
    self.validate_optional_attribute((None,'by'), nonhtml)
    self.validate_optional_attribute((None,'by'), nonblank)
    self.validate_optional_attribute((None,'by'), rfc2141_nss)
    self.validate_required_attribute((None,'sequence'), UINT31)
    self.validate_optional_attribute((None,'when'), rfc3339)

    if (None,'when') in self.attrs:
      if (None,'by') not in self.attrs:
        self.log(MissingRecommendedAttribute({"attr":"by"}))
    elif (None,'by') in self.attrs:
      self.log(MissingRecommendedAttribute({"attr":"when"}))
    else:
      self.log(MissingByAndWhenAttrs({}))

class FeedType(enumeration):
  error = InvalidSseType
  valuelist = ['complete', 'aggregated']

class rfc2141_nss(text):
  def validate(self):
    if not re.match("^([0-9a-zA-Z()+,\\-\\.:=@;$_!*'/?#]|%[0-9a-fA-F][0-9a-fA-F])+$", self.value):
     self.log(InvalidNSS({"element":self.name,"parent":self.parent.name}))

class Conflicts(validatorBase):
  def do_entry(self):
    from .entry import entry
    return entry()
  def do_item(self):
    from .item import item
    return item()
