"""$Id: $"""

__author__ = "Thomas Gambet <tgambet@w3.org>, Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 1994-2009 W3C (MIT, ERCIM, KEIO)"

"""Output class for unicorn output"""

from .base import BaseFormatter
from feedvalidator.logging import *
import feedvalidator

from config import DOCSURL

def xmlEncode(value):
  value = value.replace('&', '&amp;')
  value = value.replace('<', '&lt;')
  value = value.replace('>', '&gt;')
  value = value.replace('"', '&quot;')
  value = value.replace("'", '&apos;')
  return value

class Formatter(BaseFormatter):
  FRAGMENTLEN = 80

  def __init__(self, events, rawdata):
    BaseFormatter.__init__(self, events)
    self.rawdata = rawdata

  def getRootClass(self, aClass):
    base = aClass.__bases__[0]
    if base == Message: return aClass
    if base.__name__.split('.')[-1] == 'LoggedEvent':
      return aClass
    else:
      return self.getRootClass(base)

  def getHelpURL(self, event):
    rootClass = self.getRootClass(event.__class__).__name__
    rootClass = rootClass.split('.')[-1]
    rootClass = rootClass.lower()
#    messageClass = self.getMessageClass(event).__name__.split('.')[-1]
    messageClass = event.__class__.__name__.split('.')[-1]
    return 'http://beta.feedvalidator.org/' + DOCSURL + '/' + rootClass + '/' + messageClass

  def getContext(self, event):
    params = event.params
    if 'line' in event.params:
      line = event.params['line']
      if line >= len(self.rawdata.split('\n')):
        # For some odd reason, UnicodeErrors tend to trigger a bug
        # in the SAX parser that misrepresents the current line number.
        # We try to capture the last known good line number/column as
        # we go along, and now it's time to fall back to that.
        line = event.params['line'] = event.params.get('backupline',0)
        column = event.params['column'] = event.params.get('backupcolumn',0)
      column = event.params['column']
      codeFragment = self.rawdata.split('\n')[line-1]
      markerColumn = column
      if column > self.FRAGMENTLEN:
        codeFragment = '... ' + codeFragment[column-(self.FRAGMENTLEN/2):]
        markerColumn = 5 + (self.FRAGMENTLEN/2)
      if len(codeFragment) > self.FRAGMENTLEN:
        codeFragment = codeFragment[:(self.FRAGMENTLEN-4)] + ' ...'
    else:
      codeFragment = ''
      line = None
      markerColumn = None
  
    return xmlEncode(codeFragment)
  
  def getLineColumn(self, event):
    params = event.params
    if 'line' in params:
      line = str(params['line'])
    else:
      line = ""
    if 'column' in params:
      column = str(params['column'])
      if params['column'] < 1:
        column = '1'
    else:
      column = ""
    return {'line':line,'column':column}

  def mostSeriousClass(self):
    ms=0
    for event in self.data:
      level = -1
      if isinstance(event,Info): level = 1
      if isinstance(event,Warning): level = 2
      if isinstance(event,Error): level = 3
      ms = max(ms, level)
    return [None, Info, Warning, Error][ms]

  def format(self, event):

    params = event.params
    params['text'] = self.getMessage(event)

    # determine the level of severity
    level = 'error'
    if isinstance(event,Info): level = 'info'
    if isinstance(event,Warning): level = 'warning'
    if isinstance(event,Error): level = 'error'
    params['level'] = level

    result = '<message type="' + level + '">\n\t'
    if 'duplicates' in event.params:
      for event in event.params['duplicates']:
        position = self.getLineColumn(event)
        result = result + '<context'
        if position['line']:
          result = result + ' line="' + position['line'] + '"'
        if position['column']:
          result = result + ' column="' + position['column'] + '"'
        result = result + '>' + self.getContext(event) + '</context>\n\t'
    else:
      position = self.getLineColumn(event)
      result = result + '<context'
      if position['line']:
        result = result + ' line="' + position['line'] + '"'
      if position['column']:
        result = result + ' column="' + position['column'] + '"'
      result = result + '>' + self.getContext(event) + '</context>\n\t'
      #result = result + '<context line="' + position['line'] + '" column="' + position['column'] + '">' + self.getContext(event) + '</context>\n\t'
    rc = '''[<a title="more information about this error" href="%s.html">help</a>]''' % self.getHelpURL(event)
    result = result + '<title></title>\n<description>' + xmlEncode(params['text']) + ' ' + rc + '</description>\n'
    result = result + '</message>\n'

    return result

  def header(self):
    return ''

  def footer(self):
    return ''