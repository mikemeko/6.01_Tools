"""
Representation for a wire on a proto board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from util import dist
from util import overlap

class Wire:
  """
  Wire representation.
  """
  def __init__(self, loc_1, loc_2):
    """
    |loc_1|, |loc_2|: start end end locations of this wire.
    """
    self.loc_1 = loc_1
    self.loc_2 = loc_2
    self.r_1, self.c_1 = loc_1
    self.r_2, self.c_2 = loc_2
    # row and column supports, i.e. min's and max's
    self.row_support = min(self.r_1, self.r_2), max(self.r_1, self.r_2)
    self.column_support = min(self.c_1, self.c_2), max(self.c_1, self.c_2)
  def crosses(self, other):
    """
    Returns True if this wire and the |other| wire intersect, False otherwise.
    """
    assert isinstance(other, Wire), 'other must be a Wire'
    return overlap(self.row_support, other.row_support) and overlap(
        self.column_support, other.column_support)
  def length(self):
    """
    Returns the length of this wire.
    """
    return dist(self.loc_1, self.loc_2)
  def __hash__(self):
    return hash((self.loc_1, self.loc_2))
  def __str__(self):
    return '%s-%s' % (self.loc_1, self.loc_2)
