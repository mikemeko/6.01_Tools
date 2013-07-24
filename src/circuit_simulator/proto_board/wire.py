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
  def __init__(self, loc_1, loc_2, node):
    """
    |loc_1|, |loc_2|: start end end locations of this wire.
    |node|: the circuit node this wire is a part of.
    """
    r_1, c_1 = loc_1
    r_2, c_2 = loc_2
    assert r_1 == r_2 or c_1 == c_2, 'wire must be horizontal or vertical'
    self.loc_1 = loc_1
    self.loc_2 = loc_2
    self.r_1 = r_1
    self.c_1 = c_1
    self.r_2 = r_2
    self.c_2 = c_2
    # row and column supports, i.e. min's and max's
    self.row_support = min(r_1, r_2), max(r_1, r_2)
    self.column_support = min(c_1, c_2), max(c_1, c_2)
    self.node = node
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
  def horizontal(self):
    """
    Returns True if this wire is horizontal, or False if it is vertical.
    """
    return not self.vertical()
  def vertical(self):
    """
    Returns True if this wire is vertical, or False if it is horizontal.
    """
    return self.c_1 == self.c_2
  def __eq__(self, other):
    return (isinstance(other, Wire) and self.row_support == other.row_support
        and self.column_support == other.column_support)
  def __ne__(self, other):
    return not self == other
  def __hash__(self):
    return hash((self.row_support, self.column_support))
  def __str__(self):
    return '%s-%s' % (self.loc_1, self.loc_2)
