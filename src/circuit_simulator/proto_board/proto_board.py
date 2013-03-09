"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from util import section_locs
from visualization.visualization import Proto_Board_Visualizer

class Proto_Board:
  def __init__(self, wire_mappings={}, wires=[]):
    self._wire_mappings = wire_mappings
    self._wires = wires
  def get_wires(self):
    for wire in self._wires:
      yield wire
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
  def with_wire(self, new_wire):
    loc_1, loc_2 = new_wire
    assert not self.occupied(loc_1)
    assert not self.occupied(loc_2)
    assert loc_1 != loc_2
    new_wire_mappings = self._wire_mappings.copy()
    new_wire_mappings[loc_1] = loc_2
    new_wire_mappings[loc_2] = loc_1
    return Proto_Board(new_wire_mappings, self._wires + [(loc_1, loc_2)])
  def occupied(self, loc):
    return loc in self._wire_mappings
  def visualize(self):
    visualizer = Proto_Board_Visualizer(self._wires)
    visualizer.show()
