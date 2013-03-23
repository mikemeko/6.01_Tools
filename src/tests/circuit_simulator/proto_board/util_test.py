"""
Unittests for util.py.
TODO(mikemeko): more tests once util methods are in good shape.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.util import dist
from circuit_simulator.proto_board.util import overlap
from circuit_simulator.proto_board.util import rects_overlap
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
  def test_overlap(self):
    assert not overlap((1, 2), (3, 4))
    assert not overlap((3, 4), (1, 2))
    assert overlap((1, 2), (2, 3))
    assert overlap((2, 3), (1, 2))
    assert overlap((1, 3), (2, 4))
    assert overlap((2, 4), (1, 3))
    assert overlap((1, 4), (2, 3))
    assert overlap((2, 3), (1, 4))
  def test_rects_overlap(self):
    assert not rects_overlap((0, 0, 1, 1), (2, 2, 3, 3))
    assert rects_overlap((0, 0, 1, 1), (1, 1, 2, 2))
    assert rects_overlap((0, 0, 2, 2), (1, 1, 3, 3))

if __name__ == '__main__':
  main()
