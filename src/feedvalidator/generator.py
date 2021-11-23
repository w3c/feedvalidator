__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from .base import validatorBase
from .validators import *

#
# Atom generator element
#
class generator(nonhtml,rfc2396):
  def getExpectedAttrNames(self):
    return [(None, 'uri'), (None, 'version')]

  def prevalidate(self):
    if (None, "url") in self.attrs:
      self.value = self.attrs.getValue((None, "url"))
      rfc2396.validate(self, extraParams={"attr": "url"})
    if (None, "uri") in self.attrs:
      self.value = self.attrs.getValue((None, "uri"))
      rfc2396.validate(self, errorClass=InvalidURIAttribute, extraParams={"attr": "uri"})
    self.value=''
