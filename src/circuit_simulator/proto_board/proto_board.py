"""
Representation for a proto board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.data_structures.union_find import UnionFind
from util import section_locs
from visualization.visualization import Proto_Board_Visualizer

class Proto_Board:
  """
  Proto board representation.
  """
  def __init__(self, wire_mappings={}, wires=[],
      disjoint_loc_sets=UnionFind()):
    """
    |wire_mappings|: a dictionary mapping locations to other locations to which
        they are connected by a wire.
    |wires|: a list of the Wires on this proto board.
    TODO(mikemeko)
    """
    self._wire_mappings = wire_mappings
    self._wires = wires
    self._disjoint_loc_sets = disjoint_loc_sets
  def get_wires(self):
    """
    Returns a generator of the Wires on this proto board.
    """
    for wire in self._wires:
      yield wire
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
  def with_disjoint_loc_sets(self, disjoint_loc_sets):
    """
    TODO(mikemeko)
    """
    new_wire_mappings = self._wire_mappings.copy()
    return Proto_Board(new_wire_mappings, self._wires[:], disjoint_loc_sets)
  def with_wire(self, new_wire):
    """
    Returns a new Proto_Board containing the |new_wire|.
    """
    group_1 = self._disjoint_loc_sets.find(new_wire.loc_1)
    group_2 = self._disjoint_loc_sets.find(new_wire.loc_2)
    if group_1 and group_2 and group_1 != group_2:
      return None
    new_wire_mappings = self._wire_mappings.copy()
    new_wire_mappings[new_wire.loc_1] = new_wire.loc_2
    new_wire_mappings[new_wire.loc_2] = new_wire.loc_1
    new_disjoint_loc_sets = self._disjoint_loc_sets.copy()
    if bool(group_1) != bool(group_2):
      new_disjoint_loc_sets.insert_object(new_wire.loc_1)
      new_disjoint_loc_sets.insert_object(new_wire.loc_2)
      new_disjoint_loc_sets.union(new_wire.loc_1, new_wire.loc_2)
    return Proto_Board(new_wire_mappings, self._wires + [new_wire],
        new_disjoint_loc_sets)
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
