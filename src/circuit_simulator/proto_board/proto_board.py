"""
Representation for a proto board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from util import section_locs
from core.data_structures.disjoint_set_forest import Disjoint_Set_Forest

class Proto_Board:
  """
  Proto board representation.
  """
  def __init__(self, wire_mappings=None, wires=None, pieces=set(),
      loc_disjoint_set_forest=None):
    """
    |wire_mappings|: a dictionary mapping locations to other locations to which
        they are connected by a wire.
    |wires|: a list of the Wires on this proto board.
    |pieces|: a set of the Circuit_Pieces on this proto board.
    |loc_disjoint_set_forest|: an instance of Disjoint_Set_Forest representing
        disjoint sets of locations on the proto board that should alwas remain
        disconnected. This is used to avoid shorts.
    """
    self._wire_mappings = wire_mappings if wire_mappings is not None else {}
    self._wires = wires if wires is not None else []
    self._pieces = pieces
    self._loc_disjoint_set_forest = (loc_disjoint_set_forest if
        loc_disjoint_set_forest is not None else Disjoint_Set_Forest())
  def get_wires(self):
    """
    Returns a generator for the Wires on this proto board.
    """
    for wire in self._wires:
      yield wire
  def num_wires(self):
    """
    Returns the number of wires on this proto board.
    """
    return len(self._wires)
  def get_pieces(self):
    """
    Returns a generator for the Circuit_Pieces on this proto board.
    """
    for piece in self._pieces:
      yield piece
  def _connected(self, loc_1, loc_2, visited):
    """
    Helper for self.connected, see below.
    """
    if loc_1 in visited:
      return False
    group = set(section_locs(loc_1))
    new_visited = visited | group
    return loc_2 in group or any(map(lambda new_loc_1: self._connected(
        new_loc_1, loc_2, new_visited), (self._wire_mappings[loc] for loc in
        group if loc in self._wire_mappings)))
  def connected(self, loc_1, loc_2):
    """
    Returns True if |loc_1| and |loc_2| are connected by wires, False
        otherwise.
    """
    return self._connected(loc_1, loc_2, set())
  def locs_connected_to(self, loc):
    """
    Returns a set of the locations on this proto board that are connected (
        internally or by wires) to |loc|.
    """
    connected_locs = set()
    queue = set(section_locs(loc))
    while queue:
      connected_loc = queue.pop()
      connected_locs.add(connected_loc)
      if connected_loc in self._wire_mappings:
        for wire_neighbor in section_locs(self._wire_mappings[connected_loc]):
          if wire_neighbor not in connected_locs:
            queue.add(wire_neighbor)
    return connected_locs
  def rep_for(self, item):
    """
    Returns the representative for the group to which |item|, a location or
        node name, belongs.
    """
    return self._loc_disjoint_set_forest.find_set(item)
  def with_loc_disjoint_set_forest(self, loc_disjoint_set_forest):
    """
    Returns a copy of this board with a new forest of disjoint location sets to
        keep disconnected. If this board violates the given forest, this method
        raises and Exception.
    """
    board = Proto_Board(loc_disjoint_set_forest=loc_disjoint_set_forest)
    for piece in self._pieces:
      board = board.with_piece(piece)
    for wire in self._wires:
      board = board.with_wire(wire)
      if board is None:
        raise Exception('board violates given forest')
    return board
  def with_loc_repped(self, rep, loc):
    """
    Returns a new Proto_Board with the given |loc| and the locations internally
        connected to it being members of the group of locations represented by
        |rep|.
    """
    assert self.rep_for(rep)
    assert not self.rep_for(loc)
    new_loc_disjoint_set_forest = self._loc_disjoint_set_forest.copy()
    for section_loc in section_locs(loc):
      new_loc_disjoint_set_forest.make_set(section_loc)
      new_loc_disjoint_set_forest.union(rep, section_loc)
    return self.with_loc_disjoint_set_forest(new_loc_disjoint_set_forest)
  def with_wire(self, new_wire):
    """
    Returns a new Proto_Board containing the |new_wire|. If the wire connects
        nodes that are already connected, this method returns this proto board.
        If the wire connects nodes that are meant not to be connected, as per
        |self._loc_disjoint_set_forest|, this method returns None.
    TODO(mikemeko): can we do more here?
    """
    # if locations are already connected, no need for the wire
    if self.connected(new_wire.loc_1, new_wire.loc_2):
      return self
    # if the wire results in a short, no new proto board
    group_1 = self.rep_for(new_wire.loc_1)
    group_2 = self.rep_for(new_wire.loc_2)
    if group_1 and group_2 and group_1 != group_2:
      return None
    new_wire_mappings = self._wire_mappings.copy()
    new_wire_mappings[new_wire.loc_1] = new_wire.loc_2
    new_wire_mappings[new_wire.loc_2] = new_wire.loc_1
    new_loc_disjoint_set_forest = self._loc_disjoint_set_forest.copy()
    # update to avoid shorts that may result via the new wire
    if bool(group_1) != bool(group_2):
      present_loc = new_wire.loc_1 if group_1 else new_wire.loc_2
      absent_loc = new_wire.loc_1 if present_loc == new_wire.loc_2 else (
          new_wire.loc_2)
      for loc in section_locs(absent_loc):
        new_loc_disjoint_set_forest.make_set(loc)
        new_loc_disjoint_set_forest.union(present_loc, loc)
    return Proto_Board(new_wire_mappings, self._wires + [new_wire],
        self._pieces.copy(), new_loc_disjoint_set_forest)
  def with_piece(self, piece):
    """
    Returns a new Proto_Board containing the given |piece|. If the piece
        collides with another object on the board, this method returns raises
        an Exception.
    TODO(mikemeko): check that the piece is placed so that it's not connected
        to anything else that is already on the proto board.
    """
    # check for intersections with current objects on the board
    if any(piece.crossed_by(wire) for wire in self._wires) or any(
        piece.overlaps_with(other_piece) for other_piece in self._pieces):
      raise Exception('new piece overlaps with existing piece')
    # add new piece to pieces
    new_pieces = self._pieces.copy()
    new_pieces.add(piece)
    # account for piece sacred locations, i.e. make sure these locations never
    #     get connected to another node in the circuit
    new_loc_disjoint_set_forest = self._loc_disjoint_set_forest.copy()
    for loc in piece.get_sacred_locs():
      new_loc_disjoint_set_forest.make_set(loc)
      for section_loc in section_locs(loc):
        new_loc_disjoint_set_forest.make_set(section_loc)
        new_loc_disjoint_set_forest.union(loc, section_loc)
    return Proto_Board(self._wire_mappings.copy(), self._wires[:], new_pieces,
        new_loc_disjoint_set_forest)
  def occupied(self, loc):
    """
    Returns True if the given |loc| is occupied, False otherwise.
    """
    return loc in self._wire_mappings or any(loc in piece.all_locs() for piece
        in self._pieces)
