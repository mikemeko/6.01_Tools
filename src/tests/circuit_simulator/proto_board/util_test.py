"""
Unittests for util.py.
TODO(mikemeko): more tests once util methods are in good shape.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.util import disjoint_loc_pair_sets
from circuit_simulator.proto_board.util import dist
from unittest import main
from unittest import TestCase

class Util_Test(TestCase):
  """
  Tests for circuit_simulator/proto_board/util.
  """
  def setUp(self):
    loc_pairs = [((2, 0), (2, 10)), ((3, 10), (7, 10)), ((2, 1), (2, 4))]
    self.disjoint_sets = disjoint_loc_pair_sets(loc_pairs)
  def test_dist(self):
    assert dist((2, 0), (2, 2)) == 2
    assert dist((2, 0), (4, 0)) == 2
    assert dist((2, 0), (4, 2)) == 4

if __name__ == '__main__':
  main()
