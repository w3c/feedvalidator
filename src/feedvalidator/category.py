__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from .base import validatorBase
from .validators import *

#
# author element.
#
class category(validatorBase):
  def getExpectedAttrNames(self):
    return [(None,'term'),(None,'scheme'),(None,'label')]

  def prevalidate(self):
    self.children.append(True) # force warnings about "mixed" content

    self.validate_required_attribute((None,'term'), nonblank)
    self.validate_optional_attribute((None,'scheme'), rfc3987_full)
    self.validate_optional_attribute((None,'label'), nonhtml)
