"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import CROSSING_WIRE_PENALTY
from constants import ROWS
from constants import WIRE_LENGTH_LIMIT
from core.search.search import a_star
from core.search.search import Search_Node
from proto_board import Proto_Board
from util import dist
from util import is_body_loc
from util import is_rail_loc
from util import valid_loc
# TODO: remove
from Tkinter import mainloop
from Tkinter import Tk
from visualization.visualization import Proto_Board_Visualization

class Proto_Board_Search_Node(Search_Node):
  def __init__(self, proto_board, loc_pairs, current_ends=None, parent=None):
    assert isinstance(proto_board, Proto_Board)
    for loc_1, loc_2 in loc_pairs:
      assert valid_loc(loc_1)
      assert valid_loc(loc_2)
    if not current_ends:
      current_ends = tuple(loc_1 for loc_1, loc_2 in loc_pairs)
    Search_Node.__init__(self, (proto_board, tuple(loc_pairs), current_ends),
        parent)
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
    for new_r in proto_board.body_opp_section_rows(r):
      wire_ends.append((new_r, c))
    return filter(self._valid_not_occupied_filter(proto_board), wire_ends)
  def get_children(self):
    children = []
    proto_board, loc_pairs, current_ends = self.state
    for i, (loc_1, loc_2) in enumerate(loc_pairs):
      if not proto_board.connected(loc_1, loc_2):
        last_loc = current_ends[i]
        for neighbor_loc in proto_board.section_locs(last_loc):
          if not proto_board.occupied(neighbor_loc):
            r, c = neighbor_loc
            new_wire_ends = (self._wire_ends_from_rail_loc(neighbor_loc,
                proto_board) if is_rail_loc(neighbor_loc) else
                self._wire_ends_from_body_loc(neighbor_loc, proto_board))
            for new_wire_end in new_wire_ends:
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
  dist_from_targets = sum(dist(loc_2, current_ends[i]) for i, (loc_1, loc_2) in
      enumerate(loc_pairs))
  return (dist_from_targets + CROSSING_WIRE_PENALTY if
      proto_board.any_crossing_wires() else dist_from_targets)

def find_wiring(loc_pairs, start_proto_board=Proto_Board()):
  start_node = Proto_Board_Search_Node(start_proto_board, loc_pairs)
  return a_star(start_node, goal_test, heuristic)

if __name__ == '__main__':
  root = Tk()
  vis = Proto_Board_Visualization(root)
  prot = find_wiring([((0, 2), (8, 50))])[0]
  vis.display_proto_board(prot)
  mainloop()
