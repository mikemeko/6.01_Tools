"""
Search to find proto board wiring to connect a given list of pairs of locations
    on the proto board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import CROSSING_WIRE_PENALTY
from constants import DEBUG
from constants import DEBUG_SHOW_COST
from constants import DEBUG_SHOW_PROTO_BOARD
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
from visualization.visualization import visualize_proto_board
from wire import Wire

class Proto_Board_Search_Node(Search_Node):
  """
  Search_Node for proto board wiring problem.
  """
  def __init__(self, proto_board, loc_pairs, parent=None, cost=0):
    """
    |proto_board|: current Proto_Board in the search.
    |loc_pairs|: a tuple of the pairs of locations we are trying to connect.
    |parent|: this node's parent node, or None if this is the root node.
    |cost|: the cost of getting from the root node to this node.
    """
    Search_Node.__init__(self, (proto_board, loc_pairs), parent, cost)
  def _valid_not_occupied_filter(self, proto_board):
    """
    Returns a filter for locations that are valid and not occupied on the
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
    # can draw vertical wires to every other location in the same column
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
    # can draw horizontal wires to locations to the left and right of |loc|
    # note that we limit the lengh of these horizontal wires (can technically
    #     be very big, but considering all gets us a huge branching factor)
    for l in range(1, WIRE_LENGTH_LIMIT):
      wire_ends.append((r, c - l))
      wire_ends.append((r, c + l))
    # can draw vertical wires to the opposite half
    for new_r in body_opp_section_rows(r):
      wire_ends.append((new_r, c))
    # can draw vertical wires to the rails
    for rail_r in RAIL_ROWS:
      wire_ends.append((rail_r, c))
    return filter(self._valid_not_occupied_filter(proto_board), wire_ends)
  def get_children(self):
    """
    Returns the children of this Proto_Board_Search_Node.
    """
    children = []
    proto_board, loc_pairs = self.state
    for i, (loc_1, loc_2) in enumerate(loc_pairs):
      # if |loc_1| and |loc_2| are already connected, we're all set
      if not proto_board.connected(loc_1, loc_2):
        # can extend a wire from |loc_1| towards |loc_2| from any of the
        #     the locations |loc_1| is internally connected to
        for neighbor_loc in section_locs(loc_1):
          # make sure that the candidate start location is not occupied
          if not proto_board.occupied(neighbor_loc):
            # get candidate end locations for the new wire to draw
            wire_ends = (self._wire_ends_from_rail_loc(neighbor_loc,
                proto_board) if is_rail_loc(neighbor_loc) else
                self._wire_ends_from_body_loc(neighbor_loc, proto_board))
            for wire_end in wire_ends:
              new_wire = Wire(neighbor_loc, wire_end)
              # make sure that there is a wire to draw
              if len(new_wire) == 0:
                continue
              crossing_wire = any(wire.crosses(new_wire) for wire in
                  proto_board.get_wires())
              # continue if we do not want to allow crossing wires
              if crossing_wire and not MAYBE_ALLOW_CROSSING_WIRES:
                continue
              new_proto_board = proto_board.with_wire(new_wire)
              # make sure that the wire doesn't (1) connect things we want to
              #     keep disconnected or (2) connect things that are already
              #     connected
              if not new_proto_board or new_proto_board is proto_board:
                continue
              # we have a candidate proto board, update state and cost
              new_loc_pairs = list(loc_pairs)
              new_loc_pairs[i] = (wire_end, loc_2)
              # TODO(mikemeko): consider wire length in cost?
              new_cost = self.cost + crossing_wire * CROSSING_WIRE_PENALTY
              children.append(Proto_Board_Search_Node(new_proto_board,
                  tuple(new_loc_pairs), self, new_cost))
    return children

def goal_test(state):
  """
  Returns True if the given Proto_Board_Search_Node |state| satisfies the
      condition that all location pairs to be connected have been connected,
      False otherwise.
  """
  proto_board, loc_pairs = state
  return all(proto_board.connected(loc_1, loc_2) for loc_1, loc_2 in loc_pairs)

def heuristic(state):
  """
  Returns an estimate of the distance between the given Proto_Board_Search_Node
      |state| and a goal state.
  TODO(mikemeko): better heuristic, the right one might really do the trick :)
  """
  proto_board, loc_pairs = state
  return sum(dist(loc_1, loc_2) for loc_1, loc_2 in loc_pairs)

def progress(state, cost):
  """
  Displays some debug information to better understand search process.
  """
  if DEBUG & DEBUG_SHOW_COST:
    print cost
  if DEBUG & DEBUG_SHOW_PROTO_BOARD:
    proto_board, loc_pairs = state
    visualize_proto_board(proto_board)

def find_wiring(loc_pairs, start_proto_board=Proto_Board()):
  """
  Returns a Proto_Board in which all the pairs of locations in |loc_pairs| are
      properly connected, or None if no such Proto_Board can be found. Search
      starts from |start_proto_board|.
  """
  start_node = Proto_Board_Search_Node(
      start_proto_board.with_loc_disjoint_set_forest(loc_disjoint_set_forest(
      loc_pairs)), loc_pairs)
  proto_board, loc_pairs =  a_star(start_node, goal_test, heuristic, progress)
  return proto_board

if __name__ == '__main__':
  # test
  wires = (((0, 2), (8, 50)), ((5, 1), (10, 4)), ((3, 40), (9, 30)),
      ((10, 10), (1, 30)), ((3, 3), (5, 5)), ((4, 4), (4, 7)),
      ((5, 5), (0, 3)), ((2, 50), (2, 60)), ((13, 60), (12, 10)),
      ((4, 51), (8, 53)), ((5, 6), (5, 20)), ((9, 10), (11, 11)))
  board_with_wires = None
  run('board_with_wires = find_wiring(wires)')
  visualize_proto_board(board_with_wires)
