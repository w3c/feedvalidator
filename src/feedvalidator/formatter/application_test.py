__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

"""Output class for testing that all output messages are defined properly"""

from .base import BaseFormatter
import feedvalidator
import os
LANGUAGE = os.environ.get('LANGUAGE', 'en_US:en').split(':')[-1]
try:
  lang = __import__('feedvalidator.i18n.%s' % LANGUAGE, globals(), locals(), LANGUAGE)
except ImportError:
  LANGUAGE = 'en'
  lang = __import__('feedvalidator.i18n.%s' % LANGUAGE, globals(), locals(), LANGUAGE)

class Formatter(BaseFormatter):
  def getMessage(self, event):
    classes = [event.__class__]
    while len(classes):
      if classes[0] in lang.messages:
        return lang.messages[classes[0]] % event.params
      classes = classes + list(classes[0].__bases__)
      del classes[0]
    return None

  def format(self, event):
    """returns the formatted representation of a single event"""
    return self.getMessage(event)
