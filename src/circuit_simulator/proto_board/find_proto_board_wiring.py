"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import CROSSING_WIRE_PENALTY
from constants import RAIL_ROWS
from constants import ROWS
from constants import WIRE_LENGTH_LIMIT
from core.search.search import a_star
from core.search.search import Search_Node
from proto_board import Proto_Board
from util import body_opp_section_rows
from util import disjoint_set_containing_wire
from util import disjoint_wire_sets
from util import dist
from util import is_body_loc
from util import is_rail_loc
from util import section_locs
from util import valid_loc

class Proto_Board_Search_Node(Search_Node):
  def __init__(self, proto_board, loc_pairs, current_ends=None, num_wires=0,
      parent=None):
    assert isinstance(proto_board, Proto_Board)
    for loc_1, loc_2 in loc_pairs:
      assert valid_loc(loc_1)
      assert valid_loc(loc_2)
    if not current_ends:
      current_ends = tuple(loc_1 for loc_1, loc_2 in loc_pairs)
    Search_Node.__init__(self, (proto_board, tuple(loc_pairs), current_ends,
        num_wires), parent)
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
        last_loc = current_ends[i]
        for neighbor_loc in section_locs(last_loc):
          if not proto_board.occupied(neighbor_loc):
            r, c = neighbor_loc
            wire_ends = (self._wire_ends_from_rail_loc(neighbor_loc,
                proto_board) if is_rail_loc(neighbor_loc) else
                self._wire_ends_from_body_loc(neighbor_loc, proto_board))
            for wire_end in wire_ends:
              if wire_end != neighbor_loc:
                new_proto_board = proto_board.with_wire(neighbor_loc,
                    wire_end)
                new_current_ends = list(current_ends)
                new_current_ends[i] = wire_end
                children.append(Proto_Board_Search_Node(new_proto_board,
                    loc_pairs, tuple(new_current_ends), num_wires + 1, self))
    return children

def goal_test(state):
  proto_board, loc_pairs, current_ends, num_wires = state
  proto_board_disjoint_wire_sets = disjoint_wire_sets(proto_board.get_wires())
  loc_pair_disjoint_wire_sets = disjoint_wire_sets(loc_pairs)
  if len(proto_board_disjoint_wire_sets) != len(loc_pair_disjoint_wire_sets):
    return False
  for s in loc_pair_disjoint_wire_sets:
    wire = iter(s).next()
    pair_s = disjoint_set_containing_wire(proto_board_disjoint_wire_sets, wire)
    if not pair_s:
      return False
    for next_wire in s:
      if not next_wire in pair_s:
        return False
    proto_board_disjoint_wire_sets.remove(pair_s)
  return True

def heuristic(state):
  proto_board, loc_pairs, current_ends, num_wires = state
  return sum(dist(current_ends[i], loc_2) for i, (loc_1, loc_2) in
      enumerate(loc_pairs)) + (proto_board.any_crossing_wires() *
      CROSSING_WIRE_PENALTY) + num_wires

def find_wiring(loc_pairs, start_proto_board=Proto_Board()):
  start_node = Proto_Board_Search_Node(start_proto_board, loc_pairs)
  return a_star(start_node, goal_test, heuristic)

if __name__ == '__main__':
  wires = [((0, 2), (8, 50)), ((5, 1), (10, 4)), ((3, 40), (9, 30)),
      ((10, 10), (1, 30))]
  prot = find_wiring(wires)[0]
  prot.visualize()
