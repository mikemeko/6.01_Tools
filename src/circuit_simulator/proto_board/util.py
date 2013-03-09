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

def wire_length(wire):
  (r_1, c_1), (r_2, c_2) = wire
  return abs(r_2 - r_1) + abs(c_2 - c_1)

def row_support(wire):
  (r_1, c_1), (r_2, c_2) = wire
  return (min(r_1, r_2), max(r_1, r_2))

def column_support(wire):
  (r_1, c_1), (r_2, c_2) = wire
  return (min(c_1, c_2), max(c_1, c_2))

def supports_intersect(s_1, s_2):
  m_1, M_1 = s_1
  m_2, M_2 = s_2
  if m_1 == M_1:
    return m_2 <= m_1 <= M_2
  return m_1 <= m_2 <= M_1 or m_1 <= M_2 <= M_1

def wires_cross(wire_1, wire_2):
  return (supports_intersect(row_support(wire_1), row_support(wire_2)) and
      supports_intersect(column_support(wire_1), column_support(wire_2)))

def disjoint_wire_sets(wires):
  union_find = UnionFind()
  for (loc_1, loc_2) in wires:
    locs_to_add = set(section_locs(loc_1)) | set(section_locs(loc_2))
    union_find.insert_objects(locs_to_add)
    for loc in locs_to_add:
      union_find.union(loc_1, loc)
  return union_find.disjoint_sets()

def disjoint_set_containing_wire(disjoint_sets, wire):
  for s in disjoint_sets:
    if wire in s:
      return s
  return False
