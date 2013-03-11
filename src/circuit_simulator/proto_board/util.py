"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BODY_BOTTOM_ROWS
from constants import BODY_LEGAL_COLUMNS
from constants import BODY_ROWS
from constants import BODY_TOP_ROWS
from constants import RAIL_LEGAL_COLUMNS
from constants import RAIL_ROWS
from core.data_structures.disjoint_set_forest import Disjoint_Set_Forest

def valid_loc(loc):
  """
  Returns True if |loc| is a valid location for a connector on the proto board,
      False otherwise.
  """
  r, c = loc
  if r in RAIL_ROWS:
    return c in RAIL_LEGAL_COLUMNS
  elif r in BODY_ROWS:
    return c in BODY_LEGAL_COLUMNS
  return False

def is_body_loc(loc):
  """
  Returns True if |loc| resides in the body (middle) section of the proto
      board.
  """
  r, c = loc
  return valid_loc(loc) and r in BODY_ROWS

def is_rail_loc(loc):
  """
  Returns True if |loc| resides in the rail (bus) section of the proto board.
  """
  r, c = loc
  return valid_loc(loc) and r in RAIL_ROWS

def body_section_rows(r):
  """
  Returns the set of rows physically connected to the given row |r|.
  """
  assert r in BODY_ROWS, 'r must be a body row'
  return BODY_BOTTOM_ROWS if r in BODY_BOTTOM_ROWS else BODY_TOP_ROWS

def body_opp_section_rows(r):
  """
  Returns the set of rows on the opposite body side of the given row |r|.
  """
  assert r in BODY_ROWS, 'r must be a body row'
  return BODY_BOTTOM_ROWS if r in BODY_TOP_ROWS else BODY_TOP_ROWS

def section_locs(loc):
  """
  Returns the locations physically connected to the given |loc|.
  """
  r, c = loc
  return (((r, new_c) for new_c in RAIL_LEGAL_COLUMNS) if is_rail_loc(loc)
      else ((new_r, c) for new_r in body_section_rows(r)))

def dist(loc_1, loc_2):
  """
  Returns the Manhattan distance between |loc_1| and |loc_2|.
  """
  r_1, c_1 = loc_1
  r_2, c_2 = loc_2
  return abs(r_1 - r_2) + abs(c_1 - c_2)

def loc_disjoint_set_forest(loc_pairs):
  """
  Returns a forest of disjoint sets representing the grouping of locations
      given the pairs of locations in |loc_pairs|.
  """
  forest = Disjoint_Set_Forest()
  for loc_1, loc_2 in loc_pairs:
    forest.make_set(loc_1)
    for loc in section_locs(loc_1):
      forest.make_set(loc)
      forest.union(loc_1, loc)
    for loc in section_locs(loc_2):
      forest.make_set(loc)
      forest.union(loc_1, loc)
  return forest
