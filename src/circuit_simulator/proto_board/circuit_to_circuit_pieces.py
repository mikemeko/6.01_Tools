"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_piece_placement import find_placement
from circuit_pieces import Op_Amp_Piece
from circuit_pieces import Resistor_Piece
from circuit_simulator.simulation.circuit import Circuit
from circuit_simulator.simulation.circuit import Op_Amp
from circuit_simulator.simulation.circuit import Resistor
from find_proto_board_wiring import find_wiring
from itertools import combinations
from proto_board import Proto_Board
from visualization.visualization import visualize_proto_board
from sys import maxint
from util import dist

def same_groupings(grouping_1, grouping_2):
  return set(grouping_1) == set(grouping_2)

def remove_duplicates(items, duplicate):
  clean = []
  for i in range(len(items)):
    for j in range(i):
      if duplicate(items[i], items[j]):
        break
    else:
      clean.append(items[i])
  return clean

def all_groupings(items, partition):
  assert len(items) == sum(partition)
  if len(partition) == 0:
    return [tuple()]
  if len(partition) == 1:
    return [(tuple(items),)]
  groupings = []
  for comb in combinations(items, partition[0]):
    remaining_items = items[:]
    for item in comb:
      remaining_items.remove(item)
    for g in all_groupings(remaining_items, partition[1:]):
      groupings.append(tuple([comb] + list(g)))
  return remove_duplicates(groupings, same_groupings)

def all_partitions(n):
  if n == 0:
    return [[]]
  if n == 1:
    return [[1]]
  return [[1] * n] + [[2] + rest for rest in all_partitions(n - 2)]

def get_resistor_piece(resistor):
  return Resistor_Piece(resistor.n1, resistor.n2)

def get_op_amp_piece(op_amp_set):
  # TODO: picture
  op_amp_1 = op_amp_set[0]
  op_amp_2 = op_amp_set[1] if len(op_amp_set) == 2 else None
  n_1 = op_amp_1.nb1
  n_2 = None # pwr
  n_3 = op_amp_2.nb1 if op_amp_2 else None
  n_4 = None # pwr
  n_5 = op_amp_2.na2 if op_amp_2 else None
  n_6 = op_amp_2.na1 if op_amp_2 else None
  n_7 = op_amp_1.na1
  n_8 = op_amp_1.na2
  return Op_Amp_Piece(n_1, n_2, n_3, n_4, n_5, n_6, n_7, n_8, True)

def get_piece_placement(circuit):
  assert isinstance(circuit, Circuit)
  resistors = filter(lambda obj: isinstance(obj, Resistor), circuit.components)
  op_amps = filter(lambda obj: isinstance(obj, Op_Amp), circuit.components)
  num_op_amps = len(op_amps)
  best_placement = None
  best_placement_cost = maxint
  for partition in all_partitions(num_op_amps):
    for grouping in all_groupings(op_amps, partition):
      pieces = map(get_resistor_piece, resistors) + map(get_op_amp_piece,
          grouping)
      placement, cost = find_placement(pieces)
      if cost < best_placement_cost:
        best_placement = placement
        best_placement_cost = cost
  return best_placement

# TODO: put in another file
def loc_pairs_to_connect(placement):
  loc_pairs = []
  handled_locs = set()
  for piece in placement:
    for node in piece.nodes:
      for loc_1 in piece.locs_for(node):
        if loc_1 in handled_locs:
          continue
        other_locs = reduce(lambda l_1, l_2: l_1 + l_2, (
            other_piece.locs_for(node) for other_piece in placement))
        other_locs.remove(loc_1)
        if other_locs:
          loc_2 = min(other_locs, key=lambda loc: dist(loc_1, loc))
          loc_pairs.append((loc_1, loc_2))
  return tuple(loc_pairs)

if __name__ == '__main__':
  circuit = Circuit([Resistor('a', 'c', 'i', 1),
                     Resistor('b', 'd', 'i', 1),
                     Resistor('e', 'f', 'i', 1),
                     Op_Amp('c', 'd', 'i', 'e', 'x', 'i'),
                     Op_Amp('g', 'h', 'i', 'f', 'x', 'i')],
                     'gnd')
  placement = get_piece_placement(circuit)
  board = Proto_Board()
  for piece in placement:
    board = board.with_piece(piece)
  board = find_wiring(loc_pairs_to_connect(placement), board)
  visualize_proto_board(board)
