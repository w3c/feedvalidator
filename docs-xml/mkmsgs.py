import sys
from os.path import isfile
import os.path as path
basename = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(path.join(basename,'src'))

from feedvalidator.i18n.en import messages
from feedvalidator.logging import Warning, Error
import feedvalidator

ignoreMissing = ["warning/RSS20Profile", "error/ValidationFailure"]

template = '''
<fvdoc>
<div xmlns='http://www.w3.org/1999/xhtml'>
<div id='message'>
<p>%s</p>
</div>
<div id='explanation'>
<p>XXX</p>
</div>
<div id='solution'>
<p>XXX</p>
</div>
</div>
</fvdoc>
'''

import inspect
# Logic from text_html.py
def getRootClass(aClass):
  bl = aClass.__bases__
  if not(bl):
    return None

  aClass = bl[0]
  bl = bl[0].__bases__

  while bl:
    base = bl[0]
    if base == feedvalidator.logging.Message:
      return aClass
    aClass = base
    bl = aClass.__bases__
  return None

def isclass(x):
  import types
  return inspect.isclass(x) or type(x) == type

def missing():
  result = []

  for n, o in inspect.getmembers(feedvalidator.logging, isclass):
    rc = getRootClass(o)
    if not(rc):
      continue

    rcname = rc.__name__.split('.')[-1].lower()
    if rcname in ['warning', 'error']:
      fn = path.join(basename, 'docs', rcname, n + '.html')
      if not(isfile(path.join(basename, fn))) and not rcname + "/" + n in ignoreMissing:
        result.append((rcname, n, "", fn, fn))


  for key, value in list(messages.items()):
    if issubclass(key,Error):
      dir = 'error'
    elif issubclass(key,Warning):
      dir = 'warning'
    else:
      continue

    html = path.join(basename, 'docs', dir, key.__name__+'.html')
    xml = path.join(basename, 'docs-xml', dir, key.__name__+'.xml')

    if not path.exists(xml) or not path.exists(html):
      result.append((dir, key.__name__, value, html, xml))

  return result

import unittest
class MissingMessagesTest(unittest.TestCase):
  def test_messages(self):
    self.assertEqual([],
                     ["%s/%s" % (dir,id) for dir, id, msg, xml, html in missing()], "Errors/warnings without corresponding documentation")

def buildTestSuite():
  suite = unittest.TestSuite()
  loader = unittest.TestLoader()
  suite.addTest(loader.loadTestsFromTestCase(MissingMessagesTest))
  return suite

if __name__ == '__main__':
  import re
  for dir, id, msg, html, xml in missing():
    msg = re.sub("%\(\w+\)\w?", "<code>foo</code>", msg)
    if not path.exists(html):
      pass
    if not path.exists(xml):
      open(xml,'w').write(template.lstrip() % msg)
      print(xml)
