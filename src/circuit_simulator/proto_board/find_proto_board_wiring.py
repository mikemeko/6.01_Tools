"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import WIRE_LENGTH_LIMIT
from copy import deepcopy
from core.search.search import a_star
from core.search.search import Search_Node
from proto_board import Proto_Board

# currently assumes that no pwr gnd rail locations
class Proto_Board_Search_Node(Search_Node):
  def __init__(self, proto_board, loc_pairs, current_wires, parent=None):
    Search_Node.__init__(self, (proto_board, loc_pairs, current_wires), parent)
  def _get_new_node(self, proto_board, loc_pairs, current_wires, new_wire, i):
    loc_1, loc_2 = new_wire
    new_proto_board = proto_board.with_wire(loc_1, loc_2)
    new_current_wires = deepcopy(current_wires)
    new_current_wires[i].append(new_wire)
    return Proto_Board_Search_Node(new_proto_board, loc_pairs,
        new_current_wires, self)
  def get_children(self):
    children = []
    proto_board, loc_pairs, current_wires = self.state
    for i, (loc_1, loc_2) in enumerate(loc_pairs):
      if not proto_board.connected(loc_1, loc_2):
        last_loc = current_wires[i][-1][1] if current_wires[i] else loc_2
        for neighbor_loc in proto_board.neighbor_locs(last_loc):
          if not proto_board.occupied(neighbor_loc):
            new_wire_ends = []
            r, c = neighbor_loc
            for l in range(1, WIRE_LENGTH_LIMIT):
              new_wire_ends.append((r, c - l))
              new_wire_ends.append((r, c + l))
            for opp_section_row in proto_board.opp_section_rows(r):
              new_wire_ends.append((opp_section_row, c))
            for new_wire_end in new_wire_ends:
              if proto_board.valid_loc(new_wire_end) and (not
                  proto_board.occupied(new_wire_end)):
                new_wire = (neighbor_loc, new_wire_end)
                children.append(self._get_new_node(proto_board, loc_pairs,
                    current_wires, new_wire, i))
    return children

def goal_test(state):
  proto_board, loc_pairs, current_wires = state
  return all(proto_board.connected(loc_1, loc_2) for loc_1, loc_2 in loc_pairs)

def find_wiring(loc_pairs, start_proto_board=Proto_Board()):
  start_node = Proto_Board_Search_Node(start_proto_board, loc_pairs,
      [[] for pair in loc_pairs])
  return a_star(start_node, goal_test)
