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
from collections import defaultdict
from constants import GROUND_RAIL
from constants import MODE_PER_PAIR
from constants import ORDER_DECREASING
from constants import POWER_RAIL
from constants import RAIL_LEGAL_COLUMNS
from find_proto_board_wiring import find_wiring
from proto_board import Proto_Board
from sys import stdout
from time import clock
from traceback import print_exc
from util import node_disjoint_set_forest

def solve_layout(circuit, mode=MODE_PER_PAIR, order=ORDER_DECREASING,
    verbose=True):
  """
  Attempts to produce a layout for the given |circuit| and returns a dictionary
      containing data corresponding to the solution, most importantly the key
      'proto_board' mapped to the produced layout. The value will be None if no
      layout could be found. |mode| and |order| are parameters for how the
      wiring should be solved, see find_proto_board_wiring.py.
  """
  solve_data = defaultdict(lambda: None)
  try:
    # get a placement for the appropriate circuit pieces
    placement_start = clock()
    placement, resistor_node_pairs = get_piece_placement(circuit, verbose)
    solve_data['placement_time'] = clock() - placement_start
    solve_data['placement'] = placement
    solve_data['resistor_node_pairs'] = resistor_node_pairs
    if placement is None:
      print "Pieces don't fit on the board."
      return solve_data
    # put each of the pieces on the proto board
    proto_board = Proto_Board()
    for piece in placement:
      proto_board = proto_board.with_piece(piece)
    # get all the nodes in the circuit and their respective locations on the
    #     proto board
    nodes = all_nodes(placement)
    solve_data['nodes'] = nodes
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
    loc_pairs = loc_pairs_to_connect(placement, resistor_node_pairs)
    solve_data['loc_pairs'] = loc_pairs
    wiring_start = clock()
    proto_board, num_expanded = find_wiring(loc_pairs, proto_board, mode, order,
        verbose)
    solve_data['wiring_time'] = clock() - wiring_start
    solve_data['proto_board'] = proto_board
    solve_data['num_expanded'] = num_expanded
  except:
    print_exc(file=stdout)
  return solve_data
