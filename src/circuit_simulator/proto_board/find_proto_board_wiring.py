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
from util import disjoint_loc_pair_sets
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
  def __init__(self, proto_board, loc_pairs, current_ends=None, num_wires=0,
      parent=None, cost=0):
    if not current_ends:
      current_ends = tuple(loc_1 for loc_1, loc_2 in loc_pairs)
    Search_Node.__init__(self, (proto_board, loc_pairs, current_ends,
        num_wires), parent, cost)
  def _valid_not_occupied_filter(self, proto_board):
    return lambda loc: valid_loc(loc) and not proto_board.occupied(loc)
  def _wire_ends_from_rail_loc(self, loc, proto_board):
    assert is_rail_loc(loc)
    r, c = loc
    wire_ends = [(new_r, c) for new_r in ROWS]
    return filter(self._valid_not_occupied_filter(proto_board), wire_ends)
  def _wire_ends_from_body_loc(self, loc, proto_board):
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
    children = []
    proto_board, loc_pairs, current_ends, num_wires = self.state
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
                    loc_pairs, tuple(new_current_ends), num_wires + 1, self,
                    self.cost + crossing_wire * CROSSING_WIRE_PENALTY))
    return children

def goal_test(state):
  proto_board, loc_pairs, current_ends, num_wires = state
  return all(proto_board.connected(loc_1, loc_2) for loc_1, loc_2 in loc_pairs)

def heuristic(state):
  proto_board, loc_pairs, current_ends, num_wires = state
  return sum(dist(current_ends[i], loc_2) for i, (loc_1, loc_2) in
      enumerate(loc_pairs)) + num_wires

def find_wiring(loc_pairs, start_proto_board=Proto_Board()):
  start_node = Proto_Board_Search_Node(
      start_proto_board.with_disjoint_loc_sets(disjoint_loc_pair_sets(
      loc_pairs)), loc_pairs)
  return a_star(start_node, goal_test, heuristic)

if __name__ == '__main__':
  wires = (((0, 2), (8, 50)), ((5, 1), (10, 4)), ((3, 40), (9, 30)),
      ((10, 10), (1, 30)), ((3, 3), (5, 5)), ((4, 4), (4, 7)),
      ((5, 5), (0, 3)), ((2, 51), (2, 60)), ((13, 60), (12, 10)),
      ((4, 45), (8, 47)), ((13, 4), (9, 52)))[:10]
  prot = None
  run('prot = find_wiring(wires)[0]')
  prot.visualize()
