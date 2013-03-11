"""
Search to find proto board wiring to connect a given list of pairs of locations
    on the proto board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import CROSSING_WIRE_PENALTY
from constants import MAYBE_ALLOW_CROSSING_WIRES
from constants import RAIL_ROWS
from constants import ROWS
from constants import WIRE_LENGTH_LIMIT
from core.search.search import a_star
from core.search.search import Search_Node
from cProfile import run
from proto_board import Proto_Board
from util import body_opp_section_rows
from util import dist
from util import is_body_loc
from util import is_rail_loc
from util import loc_disjoint_set_forest
from util import section_locs
from util import valid_loc
from wire import Wire

class Proto_Board_Search_Node(Search_Node):
  """
  Search_Node for proto board wiring problem.
  """
  def __init__(self, proto_board, loc_pairs, current_ends=None, parent=None,
      cost=0):
    """
    |proto_board|: current Proto_Board in the search.
    |loc_pairs|: a tuple of the pairs of locations we are trying to connect.
    |current_ends|: a tuple of the end locations of the last wires placed
        for each of the location pairs we are trying to connect.
    |parent|: this nodes parent node, or None if this is the root node.
    |cost|: the cost of getting from the root node to this node.
    """
    if not current_ends:
      current_ends = tuple(loc_1 for loc_1, loc_2 in loc_pairs)
    state = (proto_board, loc_pairs, current_ends)
    Search_Node.__init__(self, state, parent, cost)
  def _valid_not_occupied_filter(self, proto_board):
    """
    Returns a filter for locations that are either valid or occupied on the
        given |proto_board|.
    """
    return lambda loc: valid_loc(loc) and not proto_board.occupied(loc)
  def _wire_ends_from_rail_loc(self, loc, proto_board):
    """
    Returns a list of the locations that can be connected by a wire with the
        given |loc| on the given |proto_board|, assuming that |loc| is a rail
        location.
    """
    assert is_rail_loc(loc)
    r, c = loc
    wire_ends = [(new_r, c) for new_r in ROWS]
    return filter(self._valid_not_occupied_filter(proto_board), wire_ends)
  def _wire_ends_from_body_loc(self, loc, proto_board):
    """
    Returns a list of the locations that can be connected by a wire with the
        given |loc| on the given |proto_board|, assuming that |loc| is a body
        location.
    """
    assert is_body_loc(loc)
    r, c = loc
    wire_ends = []
    for l in range(1, WIRE_LENGTH_LIMIT):
      wire_ends.append((r, c - l))
      wire_ends.append((r, c + l))
    for new_r in body_opp_section_rows(r):
      wire_ends.append((new_r, c))
    for rail_r in RAIL_ROWS:
      wire_ends.append((rail_r, c))
    return filter(self._valid_not_occupied_filter(proto_board), wire_ends)
  def get_children(self):
    """
    Returns the children of this Proto_Board_Search_Node.
    """
    children = []
    proto_board, loc_pairs, current_ends = self.state
    for i, (loc_1, loc_2) in enumerate(loc_pairs):
      if not proto_board.connected(loc_1, loc_2):
        for neighbor_loc in section_locs(current_ends[i]):
          if not proto_board.occupied(neighbor_loc):
            wire_ends = (self._wire_ends_from_rail_loc(neighbor_loc,
                proto_board) if is_rail_loc(neighbor_loc) else
                self._wire_ends_from_body_loc(neighbor_loc, proto_board))
            for wire_end in wire_ends:
              if wire_end != neighbor_loc:
                new_wire = Wire(neighbor_loc, wire_end)
                crossing_wire = any(wire.crosses(new_wire) for wire in
                    proto_board.get_wires())
                if crossing_wire and not MAYBE_ALLOW_CROSSING_WIRES:
                  continue
                new_proto_board = proto_board.with_wire(new_wire)
                if not new_proto_board:
                  continue
                new_current_ends = list(current_ends)
                new_current_ends[i] = wire_end
                children.append(Proto_Board_Search_Node(new_proto_board,
                    loc_pairs, tuple(new_current_ends), self,
                    self.cost + crossing_wire * CROSSING_WIRE_PENALTY))
    return children

def goal_test(state):
  """
  Returns True if the given Proto_Board_Search_Node |state| satisfies the
      condition that all location pairs to be connected have been connected,
      False otherwise.
  """
  proto_board, loc_pairs, current_ends = state
  return all(proto_board.connected(loc_1, loc_2) for loc_1, loc_2 in loc_pairs)

def heuristic(state):
  """
  Returns an estimate of the given Proto_Board_Search_Node |state| to a goal
      state.
  TODO(mikemeko): better heuristic, the right one might really do the trick :)
  """
  proto_board, loc_pairs, current_ends = state
  return sum(dist(current_ends[i], loc_2) for i, (loc_1, loc_2) in
      enumerate(loc_pairs)) + proto_board.num_wires()

def find_wiring(loc_pairs, start_proto_board=Proto_Board()):
  """
  Returns a Proto_Board in which all the pairs of locations in |loc_pairs| are
      properly connected, or None if no such Proto_Board can be found. Search
      starts from |start_proto_board|.
  """
  start_node = Proto_Board_Search_Node(
      start_proto_board.with_loc_disjoint_set_forest(loc_disjoint_set_forest(
      loc_pairs)), loc_pairs)
  return a_star(start_node, goal_test, heuristic)

if __name__ == '__main__':
  # test
  wires = (((0, 2), (8, 50)), ((5, 1), (10, 4)), ((3, 40), (9, 30)),
      ((10, 10), (1, 30)), ((3, 3), (5, 5)), ((4, 4), (4, 7)),
      ((5, 5), (0, 3)), ((2, 51), (2, 60)), ((13, 60), (12, 10)))
  prot = None
  run('prot = find_wiring(wires)[0]')
  prot.visualize()
