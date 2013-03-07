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

def section_dist(loc_1, loc_2):
  return min(dist(loc_1, new_loc_2) for new_loc_2 in section_locs(loc_2))

def wire_length(wire):
  (r_1, c_1), (r_2, c_2) = wire
  return abs(r_2 - r_1) + abs(c_2 - c_1)

def wire_points(wire):
  (r_1, c_1), (r_2, c_2) = wire
  length = wire_length(wire)
  dr = (r_2 - r_1) / length
  dc = (c_2 - c_1) / length
  return set((r_1 + i * dr, c_1 + i * dc) for i in xrange(length + 1))

def wires_cross(wire_1, wire_2):
  return wire_points(wire_1) & wire_points(wire_2)
