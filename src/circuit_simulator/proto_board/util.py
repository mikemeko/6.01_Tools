"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BODY_BOTTOM_ROWS
from constants import BODY_LEGAL_COLUMNS
from constants import BODY_ROWS
from constants import BODY_TOP_ROWS
from constants import RAIL_LEGAL_COLUMNS
from constants import RAIL_ROWS
from core.data_structures.union_find import UnionFind

def valid_loc(loc):
  r, c = loc
  if r in RAIL_ROWS:
    return c in RAIL_LEGAL_COLUMNS
  elif r in BODY_ROWS:
    return c in BODY_LEGAL_COLUMNS
  return False

def is_body_loc(loc):
  r, c = loc
  return valid_loc(loc) and r in BODY_ROWS

def is_rail_loc(loc):
  r, c = loc
  return valid_loc(loc) and r in RAIL_ROWS

def body_section_rows(r):
  return BODY_BOTTOM_ROWS if r in BODY_BOTTOM_ROWS else BODY_TOP_ROWS

def body_opp_section_rows(r):
  return BODY_BOTTOM_ROWS if r in BODY_TOP_ROWS else BODY_TOP_ROWS

def section_locs(loc):
  r, c = loc
  return (((r, new_c) for new_c in RAIL_LEGAL_COLUMNS) if is_rail_loc(loc)
      else ((new_r, c) for new_r in body_section_rows(r)))

def dist(loc_1, loc_2):
  r_1, c_1 = loc_1
  r_2, c_2 = loc_2
  return abs(r_1 - r_2) + abs(c_1 - c_2)

def disjoint_loc_pair_sets(loc_pairs):
  union_find = UnionFind()
  for loc_1, loc_2 in loc_pairs:
    locs_to_add = set(section_locs(loc_1)) | set(section_locs(loc_2))
    union_find.insert_objects(locs_to_add)
    for loc in locs_to_add:
      union_find.union(loc_1, loc)
  return union_find.disjoint_sets()

def disjoint_wire_sets(wires):
  return disjoint_loc_pair_sets((wire.loc_1, wire.loc_2) for wire in wires)

def disjoint_set_containing_wire(disjoint_sets, wire):
  for s in disjoint_sets:
    if wire in s:
      return s
  return False
