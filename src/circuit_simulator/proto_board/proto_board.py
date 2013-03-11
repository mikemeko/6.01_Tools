"""
Representation for a proto board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from util import section_locs
from visualization.visualization import Proto_Board_Visualizer
from core.data_structures.disjoint_set_forest import Disjoint_Set_Forest

class Proto_Board:
  """
  Proto board representation.
  """
  def __init__(self, wire_mappings={}, wires=[],
      loc_disjoint_set_forest=Disjoint_Set_Forest()):
    """
    |wire_mappings|: a dictionary mapping locations to other locations to which
        they are connected by a wire.
    |wires|: a list of the Wires on this proto board.
    |loc_disjoint_set_forest|: an instance of Disjoint_Set_Forest representing
        disjoint sets of locations on the proto board that should alwas remain
        disconnected. This is used to avoid shorts.
    """
    self._wire_mappings = wire_mappings
    self._wires = wires
    self._loc_disjoint_set_forest = loc_disjoint_set_forest
  def get_wires(self):
    """
    Returns a generator of the Wires on this proto board.
    """
    for wire in self._wires:
      yield wire
  def num_wires(self):
    """
    Returns the number of wires on this proto board.
    """
    return len(self._wires)
  def _connected(self, loc_1, loc_2, visited=set()):
    """
    Helper for self.connected, see below.
    """
    if loc_1 in visited:
      return False
    group = set(section_locs(loc_1))
    group_links = set(self._wire_mappings[loc] for loc in group
        if loc in self._wire_mappings)
    return loc_2 in group or any(self._connected(new_loc_1, loc_2,
        visited | group) for new_loc_1 in group_links)
  def connected(self, loc_1, loc_2):
    """
    Returns True if |loc_1| and |loc_2| are connected by wires, False
        otherwise.
    """
    return self._connected(loc_1, loc_2)
  def with_loc_disjoint_set_forest(self, loc_disjoint_set_forest):
    """
    Returns a copy of this board with a new forest of disjoint location sets to
        keep disconnected. If this board violates the given forest, this method
        raises and Exception.
    """
    board = Proto_Board(loc_disjoint_set_forest=loc_disjoint_set_forest)
    for wire in self._wires:
      board = board.with_wire(wire)
      if board is None:
        raise Exception('board violates given forest')
    return board
  def with_wire(self, new_wire):
    """
    Returns a new Proto_Board containing the |new_wire|. If the wire connects
        nodes that are already connected, this method returns this proto board.
        If the wire connects nodes that are meant not to be connected, as per
        |self._loc_disjoint_set_forest|, this method returns None.
    """
    if self.connected(new_wire.loc_1, new_wire.loc_2):
      return self
    group_1 = self._loc_disjoint_set_forest.find_set(new_wire.loc_1)
    group_2 = self._loc_disjoint_set_forest.find_set(new_wire.loc_2)
    if group_1 and group_2 and group_1 != group_2:
      return None
    new_wire_mappings = self._wire_mappings.copy()
    new_wire_mappings[new_wire.loc_1] = new_wire.loc_2
    new_wire_mappings[new_wire.loc_2] = new_wire.loc_1
    new_loc_disjoint_set_forest = self._loc_disjoint_set_forest.copy()
    if bool(group_1) != bool(group_2):
      new_loc_disjoint_set_forest.make_set(new_wire.loc_1)
      new_loc_disjoint_set_forest.make_set(new_wire.loc_2)
      new_loc_disjoint_set_forest.union(new_wire.loc_1, new_wire.loc_2)
    return Proto_Board(new_wire_mappings, self._wires + [new_wire],
        new_loc_disjoint_set_forest)
  def occupied(self, loc):
    """
    Returns True if the given |loc| is occupied, False otherwise.
    """
    return loc in self._wire_mappings
  def visualize(self):
    """
    Displays a window to visualize this proto board.
    """
    visualizer = Proto_Board_Visualizer(self._wires)
    visualizer.show()
