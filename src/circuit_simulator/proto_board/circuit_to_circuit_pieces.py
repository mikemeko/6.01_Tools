"""
Tools to produce a list of circuit pieces to put on the proto board given a
    circuit (an instance of circuit_simulator.simulation.circuit.Circuit).
Terms used in this file:
  Let I be the list of items [i_0, i_1, i_2, i_3].
  A *partition* of I is a list of positive integers adding to 4, the size of I.
    Example: [2, 1, 1]
  A *grouping* is a list of subcollections of I respecting some partition.
    Example: for the partition above, one possible grouping is
        [(i_0, i_1), (i_2), (i_3)] (canonical grouping). Another possible
        grouping is [(i_0, i_2), (i_1), (i_3)]. Yet another different grouping
        is [(i_1, i_0), (i_2), (i_3)], i.e. subcollection order matters.
    In the representation used below, the subcollections are python tuples.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_piece_placement import find_placement
from circuit_pieces import Op_Amp_Piece
from circuit_pieces import Pot_Piece
from circuit_pieces import Resistor_Piece
# TODO(mikemeko): this is kind of hacky, coupled with board parsing
from circuit_simulator.main.constants import GROUND
from circuit_simulator.main.constants import POWER
from circuit_simulator.simulation.circuit import Circuit
from circuit_simulator.simulation.circuit import Op_Amp
from circuit_simulator.simulation.circuit import Pot
from circuit_simulator.simulation.circuit import Resistor
from itertools import permutations
from sys import maxint

def all_1_2_partitions(n):
  """
  Returns a list of all the sorted lists of 1s and 2s whose members add to |n|.
  For instance all_1_2_partitions(4) -> [[1, 1, 1, 1], [1, 1, 2], [2, 2]].
  """
  # base case
  if n <= 1:
    return [[1] * n]
  return [[1] * n] + [rest + [2] for rest in all_1_2_partitions(n - 2)]

def grouping(permuted_items, partition):
  """
  Returns the canonical grouping of the given |permuted_items| respecting
      the given |partition|.
  For instance, grouping([1, 2, 3, 4], [2, 2]) -> set([(1, 2), (3, 4)]).
  """
  assert len(permuted_items) == sum(partition), ('partition elements must sum '
      ' number of permuted_items')
  return set(tuple(permuted_items[sum(partition[:i]):sum(partition[:i + 1])])
      for i in range(len(partition)))

def all_groupings(items, partition):
  """
  Returns a list of all possible groupings of the given |items| respecting the
      given |partition|.
  TODO(mikemeko): better way to avoid duplicates
  """
  assert len(items) == sum(partition), ('partition elements must sum to number'
      ' of items')
  groupings = []
  for permuted_items in permutations(items):
    new_grouping = grouping(permuted_items, partition)
    if new_grouping not in groupings:
      groupings.append(new_grouping)
  return groupings

def resistor_piece_from_resistor(resistor):
  """
  Returns a Resistor_Piece constructed using |resistor|, an instance of
      Resistor.
  """
  assert isinstance(resistor, Resistor), 'resistor must be a Resistor'
  return Resistor_Piece(resistor.n1, resistor.n2)

def pot_piece_from_pot(pot):
  """
  Returns a Pot_Piece constructed using |pot|, an instance of Pot.
  """
  assert isinstance(pot, Pot), 'pot must be a Pot'
  return Pot_Piece(pot.n_top, pot.n_middle, pot.n_bottom)

def op_amp_piece_from_op_amp(op_amp_set):
  """
  Returns an Op_Amp_Piece constructed using |op_amp_set|, a set of 1 or 2
      instances of Op_Amp. The first op_amp in op_amp_set takes the first
      position in the Op_Amp_Piece (i.e. pins 1, 7, and 8).
  """
  assert 1 <= len(op_amp_set) <= 2, 'op_amp_set should have 1 or 2 items'
  assert all(isinstance(obj, Op_Amp) for obj in op_amp_set), ('all items in '
      'op_amp_set must be Op_Amps')
  # if only one of the two op amps is used, tie unused op amp negative input
  #     to output (pins 3 and 5), and tie positive input to ground (pin 6)
  unused_op_amp_node = str(id(op_amp_set))
  op_amp_1 = op_amp_set[0]
  op_amp_2 = op_amp_set[1] if len(op_amp_set) == 2 else None
  n_1 = op_amp_1.nb1
  n_2 = POWER
  n_3 = op_amp_2.nb1 if op_amp_2 else unused_op_amp_node
  n_4 = GROUND
  n_5 = op_amp_2.na2 if op_amp_2 else unused_op_amp_node
  n_6 = op_amp_2.na1 if op_amp_2 else GROUND
  n_7 = op_amp_1.na1
  n_8 = op_amp_1.na2
  return Op_Amp_Piece(n_1, n_2, n_3, n_4, n_5, n_6, n_7, n_8)

def get_piece_placement(circuit):
  """
  Returns a *good* ordering of Circuit_Pieces for the given |circuit|. Finding
      the best one (i.e. the one the requires minimal wiring) is too expensive.
  """
  assert isinstance(circuit, Circuit), 'circuit must be a Circuit'
  resistors = filter(lambda obj: isinstance(obj, Resistor), circuit.components)
  resistor_pieces = map(resistor_piece_from_resistor, resistors)
  pots = filter(lambda obj: isinstance(obj, Pot), circuit.components)
  pot_pieces = map(pot_piece_from_pot, pots)
  op_amps = filter(lambda obj: isinstance(obj, Op_Amp), circuit.components)
  num_op_amps = len(op_amps)
  best_placement = None
  best_placement_cost = maxint
  # search through all the ways of packaging up the op amps
  for partition in all_1_2_partitions(num_op_amps):
    for grouping in all_groupings(op_amps, partition):
      pieces = resistor_pieces + pot_pieces + map(op_amp_piece_from_op_amp,
          grouping)
      placement, cost = find_placement(pieces)
      if cost < best_placement_cost:
        best_placement = placement
        best_placement_cost = cost
  return best_placement
