"""
Puts the pieces together to go from circuit to layout.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_piece_placement import all_nodes
from circuit_piece_placement import loc_pairs_to_connect
from circuit_piece_placement import locs_for_node
from circuit_simulator.main.constants import GROUND
from circuit_simulator.main.constants import POWER
from circuit_to_circuit_pieces import get_piece_placement
from constants import GROUND_RAIL
from constants import POWER_RAIL
from constants import RAIL_LEGAL_COLUMNS
from find_proto_board_wiring import find_wiring
from proto_board import Proto_Board
from sys import stdout
from traceback import print_exc
from util import node_disjoint_set_forest

def solve_layout(circuit):
  """
  Returns a Proto_Board instance corresponding to the given |circuit|, or None
      if one could not be found.
  """
  try:
    # get a placement for the appropriate circuit pieces
    placement, resistor_node_pairs = get_piece_placement(circuit)
    if placement is None:
      print "Pieces don't fit on the board."
      return None
    # put each of the pieces on the proto board
    proto_board = Proto_Board()
    for piece in placement:
      proto_board = proto_board.with_piece(piece)
    # get all the nodes in the circuit and their respective locations on the
    #     proto board
    nodes = all_nodes(placement)
    node_locs_mapping = dict(zip(nodes, map(lambda node: locs_for_node(
        placement, node), nodes)))
    # force the bottom two rails to be power and ground rails
    for node in (GROUND, POWER):
      if node not in node_locs_mapping:
        node_locs_mapping[node] = []
    node_locs_mapping[GROUND].append((GROUND_RAIL, iter(
        RAIL_LEGAL_COLUMNS).next()))
    node_locs_mapping[POWER].append((POWER_RAIL, iter(
        RAIL_LEGAL_COLUMNS).next()))
    # find wiring on the proto board to interconnect all locations of the same
    #     node
    proto_board = proto_board.with_loc_disjoint_set_forest(
        node_disjoint_set_forest(node_locs_mapping))
    return find_wiring(loc_pairs_to_connect(placement, resistor_node_pairs),
        proto_board)
  except:
    print_exc(file=stdout)
    return None
