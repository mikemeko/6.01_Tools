"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BODY_BOTTOM_ROWS
from constants import BODY_TOP_ROWS
from constants import RAIL_LEGAL_COLUMNS
from copy import deepcopy
from util import is_rail_loc
from util import wires_cross

class Proto_Board:
  def __init__(self, wire_mappings={}, wires=()):
    self._wire_mappings = wire_mappings
    self._wires = wires
  def get_wires(self):
    return self._wires
  def any_crossing_wires(self):
    num_wires = len(self._wires)
    return any(wires_cross(self._wires[i], self._wires[j]) for i in
        xrange(num_wires) for j in xrange(i + 1, num_wires))
  def _connected(self, loc_1, loc_2, visited=set()):
    if loc_1 in visited:
      return False
    group = set(self.section_locs(loc_1))
    group_links = set(self._wire_mappings[loc] for loc in group
        if loc in self._wire_mappings)
    return loc_2 in group or any(self._connected(new_loc_1, loc_2,
        visited | group) for new_loc_1 in group_links)
  def connected(self, loc_1, loc_2):
    return self._connected(loc_1, loc_2)
  def section_locs(self, loc):
    r, c = loc
    return (((r, new_c) for new_c in RAIL_LEGAL_COLUMNS) if is_rail_loc(loc)
        else ((new_r, c) for new_r in self.body_section_rows(r)))
  def with_wire(self, loc_1, loc_2):
    assert not self.occupied(loc_1)
    assert not self.occupied(loc_2)
    new_wire_mappings = deepcopy(self._wire_mappings)
    new_wire_mappings[loc_1] = loc_2
    new_wire_mappings[loc_2] = loc_1
    new_wires = list(self._wires)
    new_wires.append((loc_1, loc_2))
    new_wires = tuple(new_wires)
    return Proto_Board(new_wire_mappings, new_wires)
  def occupied(self, loc):
    return loc in self._wire_mappings
  def body_section_rows(self, r):
    return BODY_BOTTOM_ROWS if r in BODY_BOTTOM_ROWS else BODY_TOP_ROWS
  def body_opp_section_rows(self, r):
    return BODY_BOTTOM_ROWS if r in BODY_TOP_ROWS else BODY_TOP_ROWS
  def __str__(self):
    return str(self._wires)
