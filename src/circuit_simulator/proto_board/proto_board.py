"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from copy import deepcopy
from util import section_locs
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
    group = set(section_locs(loc_1))
    group_links = set(self._wire_mappings[loc] for loc in group
        if loc in self._wire_mappings)
    return loc_2 in group or any(self._connected(new_loc_1, loc_2,
        visited | group) for new_loc_1 in group_links)
  def connected(self, loc_1, loc_2):
    return self._connected(loc_1, loc_2)
  def with_wire(self, loc_1, loc_2):
    assert not self.occupied(loc_1)
    assert not self.occupied(loc_2)
    assert loc_1 != loc_2
    new_wire_mappings = deepcopy(self._wire_mappings)
    new_wire_mappings[loc_1] = loc_2
    new_wire_mappings[loc_2] = loc_1
    new_wires = list(self._wires)
    new_wires.append((loc_1, loc_2))
    new_wires = tuple(new_wires)
    return Proto_Board(new_wire_mappings, new_wires)
  def occupied(self, loc):
    return loc in self._wire_mappings
  def __str__(self):
    return str(self._wires)
