from .base import validatorBase
from .category import category
from .validators import yesno
from .logging import ConflictingCatAttr, ConflictingCatChildren

class categories(validatorBase):
  def getExpectedAttrNames(self):
    return [(None,'scheme'),(None,'fixed'),(None,'href')]

  def prevalidate(self):
    self.validate_optional_attribute((None,'fixed'), yesno)

    if (None,'href') in self.attrs:
      if (None,'fixed') in self.attrs:
        self.log(ConflictingCatAttr({'attr':'fixed'}))
      if (None,'scheme') in self.attrs:
        self.log(ConflictingCatAttr({'attr':'scheme'}))

  def validate(self):
    if (None,'href') in self.attrs and self.children:
      self.log(ConflictingCatChildren({}))

  def do_atom_category(self):
    return category()
