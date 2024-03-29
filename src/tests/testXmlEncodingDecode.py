#!/usr/bin/python

__author__ = "Joseph Walton <http://www.kafsemo.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2004 Joseph Walton"

import os, sys

curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
srcdir = os.path.split(curdir)[0]
if srcdir not in sys.path:
  sys.path.insert(0, srcdir)
basedir = os.path.split(srcdir)[0]

import unittest
from feedvalidator import xmlEncoding
from feedvalidator.logging import *

ctAX='application/xml'

class TestDecode(unittest.TestCase):
  def _assertEqualUnicode(self, a, b):
    self.assertNotEqual(a, None, 'Decoded strings should not equal None')
    self.assertEqual(type(a), str, 'Decoded strings should be Unicode (was ' + str(type(a)) + ')')
    self.assertEqual(type(b), str, 'Test suite error: test strings must be Unicode')
    self.assertEqual(a, b)

  def testProvidedEncoding(self):
    loggedEvents=[]
    (encoding, decoded) = xmlEncoding.decode(ctAX, 'UTF-8', b'<x/>', loggedEvents)
    self.assertEqual('UTF-8', encoding)
    self._assertEqualUnicode(decoded, '<x/>')
    self.assertEqual(loggedEvents, [])

    loggedEvents=[]
    (encoding, decoded) = xmlEncoding.decode(ctAX, 'UTF-8', b'<?xml version="1.0" encoding="utf-8"?><x/>', loggedEvents)
    self.assertEqual('UTF-8', encoding)
    self._assertEqualUnicode(decoded, '<?xml version="1.0" encoding="utf-8"?><x/>')
    self.assertEqual(loggedEvents, [])

  def testNoDeclarationOrBOM(self):
    loggedEvents=[]
    self.assertEqual(xmlEncoding.decode(ctAX, None, b'<x/>', loggedEvents)[-1], None)
    self.assertEqual(len(loggedEvents), 1)
    self.assertEqual(loggedEvents[0].__class__, MissingEncoding, "Must warn if there's no clue as to encoding")

# This document is currently detected as UTF-8, rather than None.
#
#  def testMissingEncodingDeclaration(self):
#    loggedEvents=[]
#    self._assertEqualUnicode(xmlEncoding.decode(ctAX, None, '<?xml version="1.0"?><x/>', loggedEvents), u'<?xml version="1.0"?><x/>')
#    self.assertEquals(len(loggedEvents), 1)
#    self.assertEquals(loggedEvents[0].__class__, MissingEncoding, "Must warn if there's no clue as to encoding")

  def testJustDeclaration(self):
    loggedEvents=[]
    (encoding, decoded) = xmlEncoding.decode(ctAX, None, b'<?xml version="1.0" encoding="utf-8"?><x/>', loggedEvents)
    self.assertEqual(encoding, 'utf-8')
    self._assertEqualUnicode(decoded, '<?xml version="1.0" encoding="utf-8"?><x/>')
    self.assertEqual(loggedEvents, [])

  def testSupplyUnknownEncoding(self):
    loggedEvents=[]
    self.assertEqual(xmlEncoding.decode(ctAX, 'X-FAKE', b'<x/>', loggedEvents)[-1], None)
    self.assertEqual(len(loggedEvents), 1)
    self.assertEqual(loggedEvents[0].__class__, UnknownEncoding, 'Must fail if an unknown encoding is used')

  def testDeclareUnknownEncoding(self):
    loggedEvents=[]
    self.assertEqual(xmlEncoding.decode(ctAX, None, b'<?xml version="1.0" encoding="X-FAKE"?><x/>', loggedEvents)[-1], None)
    self.assertTrue(loggedEvents)
    self.assertEqual(loggedEvents[-1].__class__, UnknownEncoding)

  def testWarnMismatch(self):
    loggedEvents=[]
    self.assertEqual(xmlEncoding.decode(ctAX, 'US-ASCII', b'<?xml version="1.0" encoding="UTF-8"?><x/>', loggedEvents)[-1], '<?xml version="1.0" encoding="UTF-8"?><x/>')
    self.assertTrue(loggedEvents)
    self.assertEqual(loggedEvents[-1].__class__, EncodingMismatch)

  def testDecodeUTF8(self):
    loggedEvents=[]
    self.assertEqual(xmlEncoding.decode(ctAX, 'utf-8', b'<x>\xc2\xa3</x>', loggedEvents)[-1], '<x>\u00a3</x>')
    self.assertEqual(loggedEvents, [])

  def testDecodeBadUTF8(self):
    """Ensure bad UTF-8 is flagged as such, but still decoded."""
    loggedEvents=[]
    self.assertEqual(xmlEncoding.decode(ctAX, 'utf-8', b'<x>\xa3</x>', loggedEvents)[-1], '<x>\ufffd</x>')
    self.assertTrue(loggedEvents)
    self.assertEqual(loggedEvents[-1].__class__, UnicodeError)

  def testRemovedBOM(self):
    """Make sure the initial BOM signature is not in the decoded string."""
    loggedEvents=[]
    self.assertEqual(xmlEncoding.decode(ctAX, 'UTF-16', b'\xff\xfe\x3c\x00\x78\x00\x2f\x00\x3e\x00', loggedEvents)[-1], '<x/>')
    self.assertEqual(loggedEvents, [])


class TestRemoveDeclaration(unittest.TestCase):
  def testRemoveSimple(self):
    self.assertEqual(xmlEncoding.removeDeclaration(
        '<?xml version="1.0" encoding="utf-8"?>'),
        '<?xml version="1.0"                 ?>')

    self.assertEqual(xmlEncoding.removeDeclaration(
      "<?xml version='1.0' encoding='us-ascii'  ?>"),
      "<?xml version='1.0'                      ?>")

  def testNotRemoved(self):
    """Make sure that invalid, or missing, declarations aren't affected."""
    for x in [
      '<?xml encoding="utf-8"?>', # Missing version
      '<doc />', # No declaration
      ' <?xml version="1.0" encoding="utf-8"?>' # Space before declaration
    ]:
      self.assertEqual(xmlEncoding.removeDeclaration(x), x)

def buildTestSuite():
  suite = unittest.TestSuite()
  loader = unittest.TestLoader()
  suite.addTest(loader.loadTestsFromTestCase(TestDecode))
  suite.addTest(loader.loadTestsFromTestCase(TestRemoveDeclaration))
  return suite

if __name__ == "__main__":
  unittest.main()
