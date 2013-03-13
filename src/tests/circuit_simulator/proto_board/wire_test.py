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
    assert Wire((3, 0), (3, 2)).crosses(Wire((2, 1), (4, 1)))
    assert Wire((2, 0), (2, 2)).crosses(Wire((2, 1), (4, 1)))
    assert Wire((2, 0), (2, 2)).crosses(Wire((2, 0), (4, 0)))
    assert Wire((2, 0), (2, 3)).crosses(Wire((2, 1), (2, 2)))
    assert not Wire((2, 0), (2, 2)).crosses(Wire((3, 0), (4, 0)))
    assert not Wire((2, 0), (2, 2)).crosses(Wire((3, 0), (3, 2)))

if __name__ == '__main__':
  main()
