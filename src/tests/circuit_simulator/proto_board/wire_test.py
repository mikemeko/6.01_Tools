"""
Unittests for wire.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.wire import Wire
from unittest import main
from unittest import TestCase

class Wire_Test(TestCase):
  """
  Tests for circuit_simulator/proto_board/wire.
  """
  def test_crosses(self):
    assert Wire((3, 0), (3, 2), None).crosses(Wire((2, 1), (4, 1), None))
    assert Wire((2, 0), (2, 2), None).crosses(Wire((2, 1), (4, 1), None))
    assert Wire((2, 0), (2, 2), None).crosses(Wire((2, 0), (4, 0), None))
    assert Wire((2, 0), (2, 3), None).crosses(Wire((2, 1), (2, 2), None))
    assert Wire((2, 0), (2, 2), None).crosses(Wire((2, 1), (2, 2), None))
    assert Wire((2, 1), (2, 2), None).crosses(Wire((2, 1), (2, 2), None))
    assert not Wire((2, 0), (2, 2), None).crosses(Wire((3, 0), (4, 0), None))
    assert not Wire((2, 0), (2, 2), None).crosses(Wire((3, 0), (3, 2), None))
  def test_eq(self):
    assert Wire((2, 2), (4, 2), None) == Wire((2, 2), (4, 2), None)
    assert Wire((2, 2), (4, 2), None) == Wire((4, 2), (2, 2), None)

if __name__ == '__main__':
  main()
