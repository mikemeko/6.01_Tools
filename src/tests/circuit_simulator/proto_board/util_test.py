"""
Unittests for util.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.util import dist
from unittest import main
from unittest import TestCase

class Util_Test(TestCase):
  """
  Tests for circuit_simulator/proto_board/util.
  """
  def test_dist(self):
    assert dist((2, 0), (2, 2)) == 2
    assert dist((2, 0), (4, 0)) == 2
    assert dist((2, 0), (4, 2)) == 4
    assert dist((0, 2), (1, 2)) == 1
    assert dist((0, 2), (2, 2)) == 4
    assert dist((0, 2), (6, 2)) == 8
    assert dist((0, 2), (7, 2)) == 11
    assert dist((0, 2), (11, 2)) == 15
    assert dist((0, 2), (12, 2)) == 18
    assert dist((0, 2), (13, 2)) == 19
    assert dist((0, 2), (13, 5)) == 22

if __name__ == '__main__':
  main()
