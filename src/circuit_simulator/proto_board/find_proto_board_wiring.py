"""
Search to find proto board wiring to connect a given list of pairs of locations
    on the proto board.
TODO(mikemeko): certain wire crossings (basically same shape crossings) should
    probably not be allowed at all.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_pieces import Resistor_Piece
from constants import ALLOW_CROSSING_WIRES
from constants import DEBUG
from constants import DEBUG_SHOW_COST
from constants import DEBUG_SHOW_PROFILE
from constants import PROTO_BOARD_MIDDLE
from constants import RAIL_ROWS
from constants import ROWS
from core.search.search import a_star
from core.search.search import Search_Node
from cProfile import runctx
from proto_board import Proto_Board
from util import body_opp_section_rows
from util import dist
from util import is_body_loc
from util import is_rail_loc
from util import section_locs
from util import valid_loc
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
  def _wire_ends_from_body_loc(self, loc, proto_board, span):
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
    for l in range(1, max(span, 5) + 1):
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
    TODO: update
    """
    children = []
    proto_board, loc_pairs = self.state
    for i, (loc_1, loc_2, resistor_flag) in enumerate(loc_pairs):
      # can extend a wire from |loc_1| towards |loc_2| from any of the
      #     the locations |loc_1| is internally connected to
      for neighbor_loc in section_locs(loc_1):
        # make sure that the candidate start location is not occupied
        if not proto_board.occupied(neighbor_loc):
          # get candidate end locations for the new wire to draw
          wire_ends = (self._wire_ends_from_rail_loc(neighbor_loc,
              proto_board) if is_rail_loc(neighbor_loc) else
              self._wire_ends_from_body_loc(neighbor_loc, proto_board,
              span=dist(loc_1, loc_2)))
          for wire_end in wire_ends:
            new_wire = Wire(neighbor_loc, wire_end)
            # make sure that there is a wire to draw
            if new_wire.length() == 0:
              continue
            # make sure that the wire does not cross any piece
            if any(piece.crossed_by(new_wire) for piece in
                proto_board.get_pieces()):
              continue
            crosses_wires = False
            same_orientation_crossing = False
            for wire in proto_board.get_wires():
              if wire.crosses(new_wire):
                crosses_wires = True
                if wire.vertical() == new_wire.vertical():
                  same_orientation_crossing = True
            # continue if we do not want to allow crossing wires
            if crosses_wires and not ALLOW_CROSSING_WIRES:
              continue
            # TODO: elaborate
            wire_proto_board = proto_board.with_wire(new_wire)
            valid_wire_proto_board = (wire_proto_board and wire_proto_board is
                not proto_board)
            # TODO: elaborate
            added_resistor = False
            if resistor_flag and not crosses_wires and new_wire.length() == 3:
              resistor_piece = Resistor_Piece('_', '_', new_wire.vertical())
              # TODO: cleanup
              if new_wire.horizontal():
                resistor_piece.top_left_loc = (new_wire.loc_1 if new_wire.c_1 <
                    new_wire.c_2 else new_wire.loc_2)
              else: # vertical resistor
                resistor_piece.top_left_loc = (new_wire.loc_1 if new_wire.r_1 <
                    new_wire.r_2 else new_wire.loc_2)
              new_proto_board = proto_board.with_piece(resistor_piece)
              new_resistor_flag = False
              added_resistor = True
            elif valid_wire_proto_board:
              new_proto_board = wire_proto_board
              new_resistor_flag = resistor_flag
            else:
              continue
            # we have a candidate proto board, compute state and cost
            new_loc_pairs = list(loc_pairs)
            new_cost = self.cost
            if not resistor_flag and wire_proto_board.connected(loc_1, loc_2):
              new_loc_pairs.pop(i)
              # favor connectedness a lot
              new_cost -= 100
            else:
              new_loc_pairs[i] = (wire_end, loc_2, new_resistor_flag)
            # TODO: cleanup
            if added_resistor:
              non_resistor_loc_pairs = list(loc_pairs)
              non_resistor_loc_pairs[i] = (wire_end, loc_2, True)
            # penalize long wires
            new_cost += 5 * new_wire.length()
            # penalize many wires
            new_cost += 1
            # penalize crossing wires (if allowed at all)
            # TODO(mikemeko): prefer certain kinds of crossings over others?
            if crosses_wires:
              new_cost += 200 if same_orientation_crossing else 50
            # favor wires that get us close to the goal, and penalize wires
            #     that get us farther away
            new_cost += dist(wire_end, loc_2) - dist(loc_1, loc_2)
            # favor keeping horizontal wires close to circuit pieces
            new_cost += new_wire.horizontal() * abs(new_wire.r_1 -
                PROTO_BOARD_MIDDLE)
            children.append(Proto_Board_Search_Node(new_proto_board,
                tuple(new_loc_pairs), self, new_cost))
            # TODO: elaborate; cleanup
            if added_resistor and valid_wire_proto_board:
              children.append(Proto_Board_Search_Node(wire_proto_board,
                  tuple(non_resistor_loc_pairs), self, new_cost))
    return children

def goal_test(state):
  """
  Returns True if the given Proto_Board_Search_Node |state| satisfies the
      condition that all location pairs to be connected have been connected,
      False otherwise.
  """
  proto_board, loc_pairs = state
  return all(not resistor_flag and proto_board.connected(loc_1, loc_2) for
      loc_1, loc_2, resistor_flag in loc_pairs)

def heuristic(state):
  """
  Returns an estimate of the distance between the given Proto_Board_Search_Node
      |state| and a goal state.
  """
  proto_board, loc_pairs = state
  return sum(dist(loc_1, loc_2) for loc_1, loc_2, resistor_flag in loc_pairs)

def progress(state, cost):
  """
  Displays some debug information to better understand search process.
  """
  if DEBUG & DEBUG_SHOW_COST:
    proto_board, loc_pairs = state
    print cost, '%d to connect' % len(loc_pairs)

def find_wiring(loc_pairs, start_proto_board=Proto_Board()):
  """
  Returns a Proto_Board in which all the pairs of locations in |loc_pairs| are
      properly connected, or None if no such Proto_Board can be found. Search
      starts from |start_proto_board|.
  TODO: update
  """
  global proto_board
  proto_board = None
  def run_search():
    global proto_board
    # first connect pairs that are farther apart; connect to rail last
    # TODO(mikemeko): this is ordering is very ad hoc, not well thought out
    loc_pairs.sort(key=lambda (loc_1, loc_2, resistor_flag): (not (is_rail_loc(
        loc_1) or is_rail_loc(loc_2))) * dist(loc_1, loc_2) + resistor_flag *
        10)
    proto_board = start_proto_board
    # connect one pair of locations at a time
    print 'Connecting %d pairs' % len(loc_pairs)
    def r_dist(loc_1, loc_2, resistor_flag):
      """
      TODO: docstring
      """
      d = dist(loc_1, loc_2)
      return d + 10 * resistor_flag * (d < 3)
    while loc_pairs:
      next_pair = loc_pairs.pop()
      loc_1, loc_2, resistor_flag = next_pair
      best_loc_1 = min(proto_board.locs_connected_to(loc_1),
          key=lambda loc: r_dist(loc, loc_2, resistor_flag))
      best_loc_2 = min(proto_board.locs_connected_to(loc_2),
          key=lambda loc: r_dist(loc, loc_1, resistor_flag))
      next_pair = (best_loc_1, loc_2, resistor_flag) if dist(best_loc_1,
          loc_2) < dist(loc_1, best_loc_2) else (loc_1, best_loc_2,
          resistor_flag)
      print '\t%d pairs left, connecting: %s' % (len(loc_pairs), next_pair)
      node = Proto_Board_Search_Node(proto_board, (next_pair,))
      proto_board = a_star(node, goal_test, heuristic, progress)[0]
  if DEBUG & DEBUG_SHOW_PROFILE:
    runctx('run_search()', globals(), locals())
  else:
    run_search()
  return proto_board
