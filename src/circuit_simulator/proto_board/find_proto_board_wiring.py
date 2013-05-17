"""
Search to find proto board wiring to connect a given list of pairs of locations
    on the proto board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_pieces import Resistor_Piece
from constants import ALLOW_CROSSING_WIRES
from constants import RAIL_ROWS
from constants import ROWS
from core.search.search import a_star
from core.search.search import Search_Node
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
    |loc_pairs|: a tuple of tuples of the form (loc_1, loc_2, resistor_flag),
        where loc_1 and loc_2 are to be connected and resistor_flag indicates
        whether there needs to be a resistor between them.
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
        location. |span| is the length of the longest wire that may be used.
    """
    assert is_body_loc(loc)
    # make max possible horizontal wire length at least 5
    span = max(span, 5)
    r, c = loc
    wire_ends = []
    # can draw horizontal wires to locations to the left and right of |loc|
    # note that we limit the lengh of these horizontal wires (can technically
    #     be very big, but considering all gets us a huge branching factor)
    for l in range(1, span + 1):
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
    for i, (loc_1, loc_2, resistor_flag) in enumerate(loc_pairs):
      # can extend a wire from |loc_1| towards |loc_2| from any of the
      #     the locations |loc_1| is internally connected to
      for neighbor_loc in section_locs(loc_1):
        # make sure that the candidate start location is not occupied
        if proto_board.occupied(neighbor_loc):
          continue
        # get candidate end locations for the new wire to draw
        wire_ends = (self._wire_ends_from_rail_loc(neighbor_loc,
            proto_board) if is_rail_loc(neighbor_loc) else
            self._wire_ends_from_body_loc(neighbor_loc, proto_board,
            span=dist(loc_1, loc_2)))
        for wire_end in wire_ends:
          # make sure that there is a wire to draw
          if wire_end == neighbor_loc:
            continue
          new_wire = Wire(neighbor_loc, wire_end)
          # make sure that the wire does not cross any piece
          if any(piece.crossed_by(new_wire) for piece in
              proto_board.get_pieces()):
            continue
          # track number of other wires this new wire crosses
          num_wire_crossings = sum(wire.crosses(new_wire) for wire in
              proto_board.get_wires())
          # continue if we do not want to allow any crossing wires
          if not ALLOW_CROSSING_WIRES and num_wire_crossings:
            continue
          # construct a proto board with this new wire
          wire_proto_board = proto_board.with_wire(new_wire)
          # check that adding the wire is reasonable
          wire_proto_board_valid = (wire_proto_board and wire_proto_board is
              not proto_board)
          # potentially create another proto board with a resistor in place of
          #     the new wire
          add_resistor = (resistor_flag and not num_wire_crossings and
              new_wire.length() == 3)
          if add_resistor:
            n1, n2 = resistor_flag
            # find representatives for the two groups, they better be there
            n1_group = proto_board.rep_for(n1)
            assert n1_group
            n2_group = proto_board.rep_for(n2)
            assert n2_group, str(n2)
            # find representative for the location we're trying to extend this
            #     resistor, representative better be there and match one of the
            #     node representatives
            wire_loc_1_group = proto_board.rep_for(new_wire.loc_1)
            if wire_loc_1_group == n1_group:
              new_group = n2_group
            elif wire_loc_1_group == n2_group:
              new_group = n1_group
            else:
              # should never get here
              raise Exception('unexpected: n1_group=%s, n2_group=%s, '
                  'wire_loc_1_group=%s' % (n1_group, n2_group,
                  wire_loc_1_group))
            # find representative for opposite location, might not be there
            wire_loc_2_group = proto_board.rep_for(new_wire.loc_2)
            if (not wire_loc_2_group) or wire_loc_2_group == new_group:
              # figure out correct orientation of Resistor_Piece n1 and n2
              if new_wire.c_1 < new_wire.c_2 or new_wire.r_1 < new_wire.r_2:
                top_left_loc = new_wire.loc_1
                if wire_loc_1_group == n2_group:
                  n1, n2 = n2, n1
              else:
                top_left_loc = new_wire.loc_2
                if wire_loc_1_group == n1_group:
                  n1, n2 = n2, n1
              # create Resistor_Piece
              resistor_piece = Resistor_Piece(n1, n2, new_wire.vertical())
              resistor_piece.top_left_loc = top_left_loc
              # create proto board with resistor
              new_proto_board = proto_board.with_piece(resistor_piece)
              if not wire_loc_2_group:
                # ensure to mark the oposite location with its apporpriate node
                new_proto_board = new_proto_board.with_loc_repped(new_group,
                    new_wire.loc_2)
              # would no longer need a resistor for this pair of locations
              new_resistor_flag = False
            else:
              # placing the resistor would create a violating connection
              add_resistor = False
          if not add_resistor:
            if wire_proto_board_valid:
              # can still put a wire down if allowed
              new_proto_board = wire_proto_board
              new_resistor_flag = resistor_flag
            else:
              continue
          # we have a candidate proto board, compute state and cost
          new_loc_pairs = list(loc_pairs)
          new_cost = self.cost
          if proto_board.connected(wire_end, loc_2):
            new_loc_pairs.pop(i)
            # favor connectedness a lot
            new_cost -= 100
          else:
            new_loc_pairs[i] = (wire_end, loc_2, new_resistor_flag)
          # penalize long wires
          new_cost += 5 * new_wire.length()
          # penalize many wires
          new_cost += 1
          # penalize crossing wires (if allowed at all)
          new_cost += 100 * num_wire_crossings
          # favor wires that get us close to the goal, and penalize wires
          #     that get us farther away
          new_cost += dist(wire_end, loc_2) - dist(loc_1, loc_2)
          children.append(Proto_Board_Search_Node(new_proto_board,
              tuple(new_loc_pairs), self, new_cost))
          # if added a resistor, also create a proto board where we use a wire
          #     instead of the resistor
          if add_resistor and wire_proto_board_valid:
            wire_loc_pairs = list(loc_pairs)
            wire_loc_pairs[i] = (wire_end, loc_2, resistor_flag)
            children.append(Proto_Board_Search_Node(wire_proto_board,
                tuple(wire_loc_pairs), self, new_cost))
    return children

def goal_test(state):
  """
  Returns True if the given Proto_Board_Search_Node |state| satisfies the
      condition that all location pairs to be connected have been connected,
      False otherwise.
  """
  proto_board, loc_pairs = state
  return all((not resistor_flag) and proto_board.connected(loc_1, loc_2) for
      (loc_1, loc_2, resistor_flag) in loc_pairs)

def heuristic(state):
  """
  Returns an estimate of the distance between the given Proto_Board_Search_Node
      |state| and a goal state.
  """
  proto_board, loc_pairs = state
  return sum(dist(loc_1, loc_2) for loc_1, loc_2, resistor_flag in loc_pairs)

def loc_pair_to_connect_next(loc_pairs):
  """
  Returns the loc pair to connect next out of the given |loc_pairs|.
  """
  assert loc_pairs, 'loc_pairs is empty'
  return max(loc_pairs, key=lambda (loc_1, loc_2, resistor_flag): dist(loc_1,
      loc_2) + 10 * bool(resistor_flag))

def condense_loc_pairs(loc_pairs, proto_board):
  """
  Updates the |loc_pairs| so as connecting them up will be easier, but no
      structural change is made.
  """
  condensed_loc_pairs = []
  for (loc_1, loc_2, resistor_flag) in loc_pairs:
    loc_1_condensed = (min(proto_board.locs_connected_to(loc_1),
        key=lambda loc: dist(loc, loc_2)), loc_2, resistor_flag)
    loc_2_condensed = (loc_1, min(proto_board.locs_connected_to(loc_2),
        key=lambda loc: dist(loc_1, loc)), resistor_flag)
    condensed_loc_pairs.append(min([loc_1_condensed, loc_2_condensed],
        key=lambda condensed: dist(*condensed[:2])))
  return condensed_loc_pairs

def find_wiring(loc_pairs, start_proto_board=Proto_Board()):
  """
  Returns a Proto_Board in which all the pairs of locations in |loc_pairs| are
      properly connected, or None if no such Proto_Board can be found. Search
      starts from |start_proto_board|.
  """
  proto_board = start_proto_board
  # connect one pair of locations at a time
  n = len(loc_pairs)
  while loc_pairs:
    next_pair = loc_pair_to_connect_next(loc_pairs)
    print '%d/%d connecting: %s' % (n - len(loc_pairs) + 1, n, next_pair)
    proto_board = a_star(Proto_Board_Search_Node(proto_board, (next_pair,)),
        goal_test, heuristic)[0]
    loc_pairs.remove(next_pair)
    loc_pairs = condense_loc_pairs(loc_pairs, proto_board)
  return proto_board
