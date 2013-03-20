"""
Unittests for circuit_piece_placement.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.circuit_piece_placement import (
    loc_pairs_for_node)
from unittest import main
from unittest import TestCase

class Circuit_Piece_Placement_Test(TestCase):
  """
  Tests for circuit_simulator/proto_board/circuit_piece_placement.
  """
  def test_loc_pairs_for_node(self):
    loc_pairs = loc_pairs_for_node([(0, 0), (2, 0), (1, 0), (3, 0)])
    assert len(loc_pairs) == 3
    assert ((0, 0), (1, 0)) in loc_pairs or ((1, 0), (0, 0)) in loc_pairs
    assert ((1, 0), (2, 0)) in loc_pairs or ((2, 0), (1, 0)) in loc_pairs
    assert ((2, 0), (3, 0)) in loc_pairs or ((3, 0), (2, 0)) in loc_pairs

if __name__ == '__main__':
  main()
