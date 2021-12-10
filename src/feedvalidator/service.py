from .base import validatorBase
from .validators import *
from .extension import extension_everywhere

class service(validatorBase, extension_everywhere):
  def getExpectedAttrNames(self):
    return [] # (None,u'scheme'),(None,u'fixed')]

  def validate(self):
    if not "app_workspace" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"app:workspace"}))

  def do_app_workspace(self):
    return workspace()

class workspace(validatorBase, extension_everywhere):
  def validate(self):
    if not "atom_title" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"atom:title"}))

  def do_app_collection(self):
    return collection()

  def do_atom_title(self):
    from .content import textConstruct
    return textConstruct(), noduplicates()

class collection(validatorBase, extension_everywhere):
  def getExpectedAttrNames(self):
    return [(None,'href')]

  def prevalidate(self):
    self.validate_required_attribute((None,'href'), rfc3987)

  def validate(self):
    if not "atom_title" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"atom:title"}))

  def do_atom_title(self):
    from .content import textConstruct
    return textConstruct(), noduplicates()

  def do_title(self):
    from .root import atom_namespace
    assert(atom_namespace in self.dispatcher.defaultNamespaces)
    self.child = 'atom_title'
    return self.do_atom_title()

  def do_app_categories(self):
    from .categories import categories
    return categories()

  def do_app_accept(self):
    from .categories import categories
    return MediaRange()
