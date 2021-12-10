"""
Code to test URI references for validity, and give their normalized
 form, according to RFC 3986.
"""

__author__ = "Joseph Walton <http://www.kafsemo.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2004, 2007 Joseph Walton"

from urllib.parse import urljoin
from urllib.parse import quote, quote_plus, unquote, unquote_plus

from unicodedata import normalize
from codecs import lookup

import re

SUBDELIMS='!$&\'()*+,;='
PCHAR='-._~' + SUBDELIMS + ':@'
GENDELIMS=':/?#[]@'
RESERVED=GENDELIMS + SUBDELIMS

default_port = {
  'ftp': 21,
  'telnet': 23,
  'http': 80,
  'gopher': 70,
  'news': 119,
  'nntp': 119,
  'prospero': 191,
  'https': 443,
  'snews': 563,
  'snntp': 563,
}

class BadUri(Exception):
  pass

def _n(s):
  return normalize('NFC', s).encode('utf-8')

octetRe = re.compile('([^%]|%[a-fA-F0-9]{2})')

def asOctets(s):
  while (s):
    m = octetRe.match(s)

    if not(m):
      raise BadUri()

    c = m.group(1)
    if (c[0] == '%'):
      yield(c.upper(), int(c[1:], 0x10))
    else:
      yield(c, ord(c))

    s = s[m.end(1):]

def _qnu(s,safe=''):
  if s == None:
    return None
  # unquote{,_plus} leave high-bit octets unconverted in Unicode strings
  # This conversion will, correctly, cause UnicodeEncodeError if there are
  #  non-ASCII characters present in the string
  s = s

  res = ''
  b = []
  for (c,x) in asOctets(s):
    # convert x to char for comparison
    if chr(x) in RESERVED and chr(x) in safe:
      res += quote(_n(unquote(bytearray(b).decode('utf-8'))), safe)
      b = []
      res += c
    else:
      b.append(x)

  res += quote(_n(unquote(bytearray(b).decode('utf-8'))), safe)

  return res

# Match an optional port specification
portRe = re.compile(':(\d*)$')

def _normPort(netloc,defPort):
  nl = netloc.lower()
  p = defPort

  m = portRe.search(nl)
  if m:
    if m.group(1) != '':
      p = int(m.group(1))
    nl = nl[:m.start(1) - 1]

  if nl and nl[-1] == '.' and nl.rfind('.', 0, -2) >= 0:
    nl = nl[:-1]

  # Square brackets are allowed, and only allowed, delimiting IPv6 addresses
  if nl.startswith('[') != nl.endswith(']'):
    raise BadUri()

  if p != defPort:
    nl = nl + ':' + str(p)
  return nl

def _normAuth(auth,port):
  i = auth.rfind('@')
  if i >= 0:
    c = auth[:i]
    if c == ':':
      c = ''
    h = auth[i + 1:]
  else:
    c = None
    h = auth

  if c:
    return c + '@' + _normPort(h,port)
  else:
    return _normPort(h,port)

def _normPath(p):
  l = p.split('/')
  i = 0
  if l and l[0]:
    i = len(l)
  while i < len(l):
    c = l[i]
    if (c == '.'):
      if i < len(l) - 1:
        del l[i]
      else:
        l[i] = ''
    elif (c == '..'):
      if i < len(l) - 1:
        del l[i]
      else:
        l[i] = ''
      if i > 1 or (i > 0 and l[0]):
        i -= 1
        del l[i]
    else:
      i += 1
  if l == ['']:
    l = ['', '']
  return '/'.join([_qnu(c, PCHAR) for c in l])

# From RFC 2396bis, with added end-of-string marker
uriRe = re.compile('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?$')

def _canonical(s):
  m = uriRe.match(s)
  if not(m):
    raise BadUri()

  # Check for a relative URI
  if m.group(2) is None:
    scheme = None
  else:
    scheme = m.group(2).lower()

  if m.group(4) is None:
    authority = None

    p = m.group(5)

    # Don't try to normalise URI references with relative paths
    if scheme is None and not p.startswith('/'):
      return None

    if scheme == 'mailto':
      # XXX From RFC 2368, mailto equivalence needs to be subtler than this
      i = p.find('@')
      if i > 0:
        j = p.find('?')
        if j < 0:
          j = len(p)
        p = _qnu(p[:i]) + '@' + _qnu(p[i + 1:].lower()) + _qnu(p[j:])
      path = p
    else:
      if scheme is None or p.startswith('/'):
        path = _normPath(p)
      else:
        path = _qnu(p, PCHAR + '/')
  else:
    a = m.group(4)
    p = m.group(5)
    if scheme in default_port:
      a = _normAuth(a, default_port[scheme])
    else:
      a = _normAuth(a, None)

    authority = a
    path = _normPath(p)

  query = _qnu(m.group(7), PCHAR + "/?")
  fragment = _qnu(m.group(9), PCHAR + "/?")

  s = ''
  if scheme != None:
    s += scheme + ':'

  if authority != None:
    s += '//' + authority

  s += path
  if query != None:
    s += '?' + query
  if fragment != None:
    s += '#' + fragment
  return s

class Uri:
  """A Uri wraps a string and performs equality testing according to the
   rules for URI equivalence. """
  def __init__(self,s):
    self.s = s
    self.n = _canonical(s)

  def __str__(self):
    return self.s

  def __repr__(self):
    return repr(self.s)

  def __eq__(self, a):
    return self.n == a.n

def canonicalForm(u):
  """Give the canonical form for a URI, so char-by-char comparisons become valid tests for equivalence."""
  try:
    return _canonical(u)
  except BadUri:
    return None
  except UnicodeError:
    return None
