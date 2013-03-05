"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BOTTOM_SECTION
from constants import PROTO_BOARD_WIDTH
from constants import TOP_SECTION
from copy import deepcopy

# currently assumes that no pwr gnd rail locations
class Proto_Board:
  def __init__(self, wires={}):
    self._wires = wires
  def _connected(self, loc_1, loc_2, visited=set()):
    if loc_1 in visited:
      return False
    r, c = loc_1
    group = set((new_r, c) for new_r in self.section_rows(r))
    group_links = set(self._wires[loc] for loc in group if loc in self._wires)
    return loc_2 in group or any(self._connected(new_loc_1, loc_2,
        visited | group) for new_loc_1 in group_links)
  def connected(self, loc_1, loc_2):
    return self._connected(loc_1, loc_2)
  def neighbor_locs(self, loc):
    r, c = loc
    return ((new_r, c) for new_r in (self.section_rows(r) - set([r])))
  def with_wire(self, loc_1, loc_2):
    assert not self.occupied(loc_1)
    assert not self.occupied(loc_2)
    new_wires = deepcopy(self._wires)
    new_wires[loc_1] = loc_2
    new_wires[loc_2] = loc_1
    return Proto_Board(new_wires)
  def occupied(self, loc):
    return loc in self._wires
  def valid_loc(self, loc):
    r, c = loc
    return 0 <= c < PROTO_BOARD_WIDTH
  def section_rows(self, r):
    return BOTTOM_SECTION if r in BOTTOM_SECTION else TOP_SECTION
  def opp_section_rows(self, r):
    return BOTTOM_SECTION if r in TOP_SECTION else BOTTOM_SECTION
  def __str__(self):
    return str(self._wires)

if __name__ == '__main__':
  proto_board = Proto_Board()
  proto_board = proto_board.with_wire((2, 0), (2, 2))
  proto_board = proto_board.with_wire((4, 2), (4, 10))
  print proto_board.connected((2, 0), (4, 10))
