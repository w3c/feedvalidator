__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

"""Output class for xml output"""

from .base import BaseFormatter
from feedvalidator.logging import *
import feedvalidator

def xmlEncode(value):
  value = value.replace('&', '&amp;')
  value = value.replace('<', '&lt;')
  value = value.replace('>', '&gt;')
  value = value.replace('"', '&quot;')
  value = value.replace("'", '&apos;')
  return value

class Formatter(BaseFormatter):
  def format(self, event):
    params = event.params

    params['type'] = event.__class__.__name__
    params['text'] = self.getMessage(event)

    # determine the level of severity
    level = 'unknown'
    if isinstance(event,Info): level = 'info'
    if isinstance(event,Warning): level = 'warning'
    if isinstance(event,Error): level = 'error'
    params['level'] = level

    # organize fixed elements into a known order
    order = list(params.keys())
    order.sort()
    for key in ['msgcount', 'text', 'column', 'line', 'type', 'level']:
      if key in order:
        order.remove(key)
        order.insert(0,key)

    # output the elements
    result = "<%s>\n" % level
    for key in order:
      value = xmlEncode(str(params[key]))
      pub_key = key
      if key == "backupcolumn":
        pubkey = "column"
      elif key == "backupline":
        pubkey = "line"
      result = result + ("  <%s>%s</%s>\n" % (key, value, key))
    result = result + "</%s>\n" % level

    return result
