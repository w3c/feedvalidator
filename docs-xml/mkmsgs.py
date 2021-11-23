import sys
import os.path as path
basename = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(path.join(basename,'src'))

from feedvalidator.i18n.en import messages
from feedvalidator.logging import Warning, Error

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

def missing():
  result = []

  for key, value in list(messages.items()):
    if issubclass(key,Error):
      dir = 'error'
    elif issubclass(key,Warning):
      dir = 'warning'
    else:
      continue

    xml = path.join(basename, 'docs-xml', dir, key.__name__+'.xml')

    if not path.exists(xml):
      result.append((dir, key.__name__, value, xml))

  return result

import unittest
class MissingMessagesTest(unittest.TestCase):
  def test_messages(self):
    self.assertEqual([],
      ["%s/%s" % (dir,id) for dir, id, msg, xml, html in missing()])

def buildTestSuite():
  suite = unittest.TestSuite()
  loader = unittest.TestLoader()
  suite.addTest(loader.loadTestsFromTestCase(MissingMessagesTest))
  return suite

if __name__ == '__main__':
  import re
  for dir, id, msg, xml in missing():
    msg = re.sub("%\(\w+\)\w?", "<code>foo</code>", msg)
    if not path.exists(xml):
      open(xml,'w').write(template.lstrip() % msg)
      print(xml)
