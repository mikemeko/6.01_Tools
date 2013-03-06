"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import CROSSING_WIRE_PENALTY
from constants import WIRE_LENGTH_LIMIT
from core.search.search import a_star
from core.search.search import Search_Node
from proto_board import Proto_Board
from util import dist

# currently assumes that no pwr gnd rail locations
class Proto_Board_Search_Node(Search_Node):
  def __init__(self, proto_board, loc_pairs, current_ends=None, parent=None):
    assert isinstance(proto_board, Proto_Board)
    for loc_1, loc_2 in loc_pairs:
      assert proto_board.valid_loc(loc_1)
      assert proto_board.valid_loc(loc_2)
    if not current_ends:
      current_ends = tuple(loc_1 for loc_1, loc_2 in loc_pairs)
    Search_Node.__init__(self, (proto_board, tuple(loc_pairs), current_ends),
        parent)
  def get_children(self):
    children = []
    proto_board, loc_pairs, current_ends = self.state
    for i, (loc_1, loc_2) in enumerate(loc_pairs):
      if not proto_board.connected(loc_1, loc_2):
        last_loc = current_ends[i]
        for neighbor_loc in proto_board.section_locs(last_loc):
          if not proto_board.occupied(neighbor_loc):
            r, c = neighbor_loc
            new_wire_ends = []
            for l in range(1, WIRE_LENGTH_LIMIT):
              new_wire_ends.append((r, c - l))
              new_wire_ends.append((r, c + l))
            for opp_section_row in proto_board.opp_section_rows(r):
              new_wire_ends.append((opp_section_row, c))
            for new_wire_end in new_wire_ends:
              if proto_board.valid_loc(new_wire_end) and (not
                  proto_board.occupied(new_wire_end)):
                new_proto_board = proto_board.with_wire(neighbor_loc,
                    new_wire_end)
                new_current_ends = list(current_ends)
                new_current_ends[i] = new_wire_end
                children.append(Proto_Board_Search_Node(new_proto_board,
                    loc_pairs, tuple(new_current_ends), self))
    return children

def goal_test(state):
  proto_board, loc_pairs, current_ends = state
  return all(proto_board.connected(loc_1, loc_2) for loc_1, loc_2 in loc_pairs)

def heuristic(state):
  proto_board, loc_pairs, current_ends = state
  return sum(dist(loc_2, current_ends[i]) for i, (loc_1, loc_2) in
      enumerate(loc_pairs)) + (CROSSING_WIRE_PENALTY if
      proto_board.any_crossing_wires() else 0)

def find_wiring(loc_pairs, start_proto_board=Proto_Board()):
  start_node = Proto_Board_Search_Node(start_proto_board, loc_pairs)
  return a_star(start_node, goal_test, heuristic)

if __name__ == '__main__':
  print find_wiring([((2, 0), (8, 10)), ((4, 0), (3, 5)),
      ((9, 9), (3, 10)), ((6, 11), (6, 13)), ((7, 7), (2, 0))])[0]
