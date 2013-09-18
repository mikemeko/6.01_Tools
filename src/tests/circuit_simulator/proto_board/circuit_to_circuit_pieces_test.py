"""
Unittests for circuit_to_circuit_pieces.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.circuit_to_circuit_pieces import (
    all_1_2_partitions)
from circuit_simulator.proto_board.circuit_to_circuit_pieces import (
    all_groupings)
from circuit_simulator.proto_board.circuit_to_circuit_pieces import grouping
from math import factorial
from unittest import main
from unittest import TestCase

class Circuit_To_Circuit_Pieces_Test(TestCase):
  """
  Tests for circuit_simulator/proto_board/circuit_to_circuit_pieces.
  """
  def test_all_1_2_partitions(self):
    assert all_1_2_partitions(0) == [[]]
    assert all_1_2_partitions(1) == [[1]]
    assert all_1_2_partitions(2) == [[1, 1], [2]]
    assert all_1_2_partitions(3) == [[1, 1, 1], [1, 2]]
    assert all_1_2_partitions(4) == [[1, 1, 1, 1], [1, 1, 2], [2, 2]]
  def test_grouping(self):
    assert grouping([1, 2, 3, 4], [2, 2]) == set([(1, 2), (3, 4)])
  def test_all_groupings(self):
    groupings = all_groupings([1, 2, 3], [2, 1])
    assert len(groupings) == 6
    assert set([(1, 2), (3,)]) in groupings
    assert set([(2, 1), (3,)]) in groupings
    assert set([(1, 3), (2,)]) in groupings
    assert set([(3, 1), (2,)]) in groupings
    assert set([(2, 3), (1,)]) in groupings
    assert set([(3, 2), (1,)]) in groupings
  def _num_all_op_amp_groupings(self, n):
    return sum(factorial(n) / (factorial(k) * factorial(n - 2 * k)) for k in
        xrange(n / 2 + 1))
  def test_num_all_op_amp_groupings(self):
    for n in xrange(8):
      items = range(n)
      num_all_groupings = sum(len(all_groupings(items, partition)) for partition
          in all_1_2_partitions(n))
      assert num_all_groupings == self._num_all_op_amp_groupings(n)

if __name__ == '__main__':
  main()
