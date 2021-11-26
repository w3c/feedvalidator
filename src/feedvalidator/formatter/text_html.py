__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

"""Output class for HTML text output"""

from .base import BaseFormatter
import feedvalidator
from xml.sax.saxutils import escape

from feedvalidator.logging import Message, Info, Warning, Error

from config import DOCSURL

def escapeAndMark(x):
  html = escape(x)

  # Double-escape, and highlight, illegal characters.
  for i in range(len(html)-1,-1,-1):
    c = ord(html[i])
    if 0x80 <= c <= 0x9F or c == 0xfffd:
      if c == 0xfffd:
        e = '?'
      else:
        e = '\\x%02x' % (c)
      html = '%s<span class="badOctet">%s</span>%s' % (html[:i], e, html[i+1:])

  return html.replace("  "," &nbsp;")

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
    return DOCSURL + '/' + rootClass + '/' + messageClass

  def mostSeriousClass(self):
    ms=0
    for event in self.data:
      level = -1
      if isinstance(event,Info): level = 1
      if isinstance(event,Warning): level = 2
      if isinstance(event,Error): level = 3
      ms = max(ms, level)
    return [None, Info, Warning, Error][ms]

  def header(self):
    return '<ul>'

  def footer(self):
    return '</ul>'

  def format(self, event):
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
        codeFragment = '... ' + codeFragment[column-int(self.FRAGMENTLEN/2):]
        markerColumn = 5 + int(self.FRAGMENTLEN/2)
      if len(codeFragment) > self.FRAGMENTLEN:
        codeFragment = codeFragment[:(self.FRAGMENTLEN-4)] + ' ...'
    else:
      codeFragment = ''
      line = None
      markerColumn = None

    html = escapeAndMark(codeFragment)

    rc = '<li><p>'
    if line:
      rc += '''<a href="#l%s">''' % line
      rc += '''%s</a>, ''' % self.getLine(event)
      rc += '''%s: ''' % self.getColumn(event)
    if 'value' in event.params:
      rc += '''<span class="message">%s: <code>%s</code></span>''' % (escape(self.getMessage(event)), escape(str(event.params['value'])))
    else:
      rc += '''<span class="message">%s</span>''' % escape(self.getMessage(event))
    rc += '''%s ''' % self.getCount(event)
    rc += '''[<a title="more information about this error" href="%s.html">help</a>]</p>''' % self.getHelpURL(event)
    rc += '''<blockquote><pre>''' + html + '''<br />'''
    if markerColumn:
      rc += '&nbsp;' * markerColumn
      rc += '''<span class="marker">^</span>'''
    rc += '</pre></blockquote></li>'
    return rc
