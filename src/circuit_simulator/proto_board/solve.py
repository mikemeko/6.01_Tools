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
from circuit_to_circuit_pieces import get_random_piece_placement
from collections import defaultdict
from constants import COST_TYPE_BLOCKING
from constants import COST_TYPE_DISTANCE
from constants import GROUND_RAIL
from constants import GROUND_RAIL_2
from constants import MODE_PER_NODE
from constants import MODE_PER_PAIR
from constants import ORDER_DECREASING
from constants import ORDER_INCREASING
from constants import POWER_RAIL
from constants import POWER_RAIL_2
from constants import RAIL_LEGAL_COLUMNS
from find_proto_board_wiring import find_terrible_wiring
from find_proto_board_wiring import find_wiring
from proto_board import Proto_Board
from sys import stdout
from time import clock
from traceback import print_exc
from util import dist
from util import node_disjoint_set_forest
from wire import Wire

def _setup(placement, resistor_node_pairs):
  """
  Produces a starting Proto_Board using the given |placement|.
  """
  proto_board = Proto_Board()
  for piece in placement:
    proto_board = proto_board.with_piece(piece)
  nodes = all_nodes(placement)
  node_locs_mapping = dict(zip(nodes, map(lambda node: locs_for_node(
      placement, node), nodes)))
  for node in (GROUND, POWER):
    if node not in node_locs_mapping:
      node_locs_mapping[node] = []
  legal_rail_column = iter(RAIL_LEGAL_COLUMNS).next()
  node_locs_mapping[GROUND].append((GROUND_RAIL, legal_rail_column))
  node_locs_mapping[POWER].append((POWER_RAIL, legal_rail_column))
  proto_board = proto_board.with_loc_disjoint_set_forest(
      node_disjoint_set_forest(node_locs_mapping))
  return proto_board, nodes, loc_pairs_to_connect(placement,
      resistor_node_pairs)

def solve_layout(circuit, resistors_as_components, cost_type, mode, order,
    best_first, filter_wire_lengths, random_placement, verbose=True):
  """
  Attempts to produce a layout for the given |circuit| and returns a dictionary
      containing data corresponding to the solution, most importantly the key
      'proto_board' mapped to the produced layout. The value will be None if no
      layout could be found. |cost_type| is a parameter for which placement cost
      to use, see circuit_piece_placement.py. |mode| and |order| are parameters
      for how the wiring should be solved, see find_proto_board_wiring.py. If
      |random_placement| evaluates to True, the placement will be random.
  """
  if verbose:
    print 'Resistors as components: %s' % resistors_as_components
    print 'Placement cost type: %s' % cost_type
    print 'Wiring mode: %s, order: %s' % (mode, order)
    print 'Search: %s' % ('Best First' if best_first else 'A*')
    print 'Filter wire lengths: %s' % filter_wire_lengths
    print
  solve_data = defaultdict(lambda: None)
  try:
    placement_start = clock()
    if random_placement:
      placement = get_random_piece_placement(circuit)
      resistor_node_pairs = []
    else:
      placement, resistor_node_pairs = get_piece_placement(circuit,
          resistors_as_components, cost_type, verbose)
    solve_data['placement_time'] = clock() - placement_start
    solve_data['placement'] = placement
    solve_data['resistor_node_pairs'] = resistor_node_pairs
    if placement is None:
      print "Pieces don't fit on the board."
      return solve_data
    proto_board, nodes, loc_pairs = _setup(placement, resistor_node_pairs)
    solve_data['nodes'] = nodes
    solve_data['loc_pairs'] = loc_pairs
    wiring_start = clock()
    proto_board, num_expanded = find_wiring(loc_pairs=loc_pairs,
        start_proto_board=proto_board, mode=mode, order=order,
        best_first=best_first, filter_wire_lengths=filter_wire_lengths,
        verbose=verbose)
    solve_data['wiring_time'] = clock() - wiring_start
    solve_data['proto_board'] = proto_board
    solve_data['num_expanded'] = num_expanded
  except:
    print_exc(file=stdout)
  return solve_data

def _wire_loc_pair(loc_pair, proto_board):
  """
  Runs a search to connect the given |loc_pair| starting from the given
      |proto_board|. Note that this method sets a very small number of states
      to expand.
  """
  return find_wiring(loc_pairs=[loc_pair], start_proto_board=proto_board,
      mode=MODE_PER_PAIR, order=ORDER_DECREASING, best_first=False,
      filter_wire_lengths=True, verbose=False)[0]

def combined_solve_layout(circuit, verbose=True):
  """
  Creates a layout for the given |circuit| by using a combination of methods.
      Returns None on failure.
  """
  solve_data = {'num_runs': 0, 'num_forced_wires': 0, 'proto_board': None}
  partially_solved = []
  for cost_type in (COST_TYPE_DISTANCE, COST_TYPE_BLOCKING):
    if verbose:
      print 'Cost type: %s' % cost_type
    placement, resistor_node_pairs = get_piece_placement(circuit,
        resistors_as_components=True, cost_type=cost_type, verbose=verbose)
    if placement is None:
      if verbose:
        print '\tToo many components.'
      continue
    for order_sign in (1, -1):
      solve_data['num_runs'] += 1
      proto_board, nodes, loc_pairs = _setup(placement, resistor_node_pairs)
      # use top rails only for power and ground
      proto_board = proto_board.with_wire(Wire((GROUND_RAIL, 2), (GROUND_RAIL_2,
          2), GROUND)).with_wire(Wire((POWER_RAIL, 3), (POWER_RAIL_2, 3),
          POWER))
      if verbose:
        print proto_board
      loc_pairs.sort(key=lambda (loc_1, loc_2, resistor, node): order_sign *
          dist(loc_1, loc_2))
      if verbose:
        print 'Order: %d' % order_sign
      failed_loc_pairs = []
      for loc_pair in loc_pairs:
        loc_1, loc_2, resistor, node = loc_pair
        if verbose:
          print 'Connecting %s -- %s' % (loc_1, loc_2)
        wired_proto_board = _wire_loc_pair(loc_pair, proto_board)
        if wired_proto_board:
          proto_board = wired_proto_board
          if verbose:
            print proto_board
            print 'Success'
        else:
          failed_loc_pairs.append(loc_pair)
          if verbose:
            print 'Fail'
      if not failed_loc_pairs:
        solve_data['proto_board'] = proto_board.prettified()
        return solve_data
      else:
        partially_solved.append((proto_board.prettified(), failed_loc_pairs))
  if not partially_solved:
    solve_data['proto_board'] = None
    return solve_data
  def cost((proto_board, failed_loc_pairs)):
    return sum(dist(loc_1, loc_2) ** 2 for loc_1, loc_2, resistor, node in
        failed_loc_pairs)
  proto_board, failed_loc_pairs = min(partially_solved, key=cost)
  if verbose:
    print 'Using terrible wirer for: %s' % [(loc_1, loc_2) for (loc_1, loc_2,
        resistor, node) in failed_loc_pairs]
  solve_data['proto_board'] = find_terrible_wiring(failed_loc_pairs,
      proto_board)
  solve_data['num_forced_wires'] = len(failed_loc_pairs)
  return solve_data

def many_layouts(circuit):
  """
  Generates layouts using verious methods. Returns a list of protoboards.
  """
  layouts = []
  print 'Distance'
  layouts.append(solve_layout(circuit,
      resistors_as_components=True,
      cost_type=COST_TYPE_DISTANCE,
      mode=MODE_PER_PAIR,
      order=ORDER_DECREASING,
      best_first=False,
      filter_wire_lengths=False,
      random_placement=False,
      verbose=True)['proto_board'])
  print 'Blocking'
  layouts.append(solve_layout(circuit,
      resistors_as_components=True,
      cost_type=COST_TYPE_BLOCKING,
      mode=MODE_PER_PAIR,
      order=ORDER_DECREASING,
      best_first=False,
      filter_wire_lengths=False,
      random_placement=False,
      verbose=True)['proto_board'])
  print 'All pairs'
  layouts.append(solve_layout(circuit,
      resistors_as_components=True,
      cost_type=COST_TYPE_BLOCKING,
      mode=MODE_ALL_PAIRS,
      order=ORDER_DECREASING,
      best_first=False,
      filter_wire_lengths=False,
      random_placement=False,
      verbose=True)['proto_board'])
  print 'Per-pair, decreasing'
  layouts.append(solve_layout(circuit,
      resistors_as_components=True,
      cost_type=COST_TYPE_BLOCKING,
      mode=MODE_PER_PAIR,
      order=ORDER_DECREASING,
      best_first=False,
      filter_wire_lengths=False,
      random_placement=False,
      verbose=True)['proto_board'])
  print 'Per-pair, increasing'
  layouts.append(solve_layout(circuit,
      resistors_as_components=True,
      cost_type=COST_TYPE_BLOCKING,
      mode=MODE_PER_PAIR,
      order=ORDER_INCREASING,
      best_first=False,
      filter_wire_lengths=False,
      random_placement=False,
      verbose=True)['proto_board'])
  print 'Per-node, decreasing'
  layouts.append(solve_layout(circuit,
      resistors_as_components=True,
      cost_type=COST_TYPE_BLOCKING,
      mode=MODE_PER_NODE,
      order=ORDER_DECREASING,
      best_first=False,
      filter_wire_lengths=False,
      random_placement=False,
      verbose=True)['proto_board'])
  print 'Per-node, increasing'
  layouts.append(solve_layout(circuit,
      resistors_as_components=True,
      cost_type=COST_TYPE_BLOCKING,
      mode=MODE_PER_NODE,
      order=ORDER_INCREASING,
      best_first=False,
      filter_wire_lengths=False,
      random_placement=False,
      verbose=True)['proto_board'])
  print 'Resistors as wires'
  layouts.append(solve_layout(circuit,
      resistors_as_components=False,
      cost_type=COST_TYPE_BLOCKING,
      mode=MODE_PER_PAIR,
      order=ORDER_DECREASING,
      best_first=False,
      filter_wire_lengths=False,
      random_placement=False,
      verbose=True)['proto_board'])
  print 'Best First Search'
  layouts.append(solve_layout(circuit,
      resistors_as_components=True,
      cost_type=COST_TYPE_BLOCKING,
      mode=MODE_PER_PAIR,
      order=ORDER_DECREASING,
      best_first=True,
      filter_wire_lengths=False,
      random_placement=False,
      verbose=True)['proto_board'])
  return layouts
