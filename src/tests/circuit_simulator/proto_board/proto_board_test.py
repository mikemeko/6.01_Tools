"""
Unittests for proto_board.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.proto_board import Proto_Board
from circuit_simulator.proto_board.wire import Wire
from unittest import main
from unittest import TestCase

class Proto_Board_Test(TestCase):
  """
  Tests for circuit_simulator/proto_board/proto_board.
  """
  def _board_with_wires(self, wires):
    board = Proto_Board()
    for loc_1, loc_2 in wires:
      board = board.with_wire(Wire(loc_1, loc_2, None))
    return board
  def test_connected(self):
    board = self._board_with_wires([((2, 0), (2, 10)), ((3, 10), (9, 10)),
        ((8, 10), (12, 10)), ((4, 45), (7, 45)), ((8, 45), (8, 50))])
    group_1 = [(2, 0), (2, 10), (3, 10), (9, 10), (8, 10), (12, 10)]
    group_2 = [(4, 45), (7, 45), (8, 45), (8, 50)]
    for group in group_1, group_2:
      for loc_1 in group:
        for loc_2 in group:
          assert board.connected(loc_1, loc_2)
    for loc_1 in group_1:
      for loc_2 in group_2:
        assert not board.connected(loc_1, loc_2)
    assert not board.connected((2, 0), (2, 1))
  def test_num_wires(self):
    board = self._board_with_wires([])
    assert board.num_wires() == 0
    board = self._board_with_wires([((2, 0), (2, 10))])
    assert board.num_wires() == 1
    board = self._board_with_wires([((2, 0), (2, 10)), ((3, 10), (9, 10))])
    assert board.num_wires() == 2
  def test_num_wire_crosses(self):
    board = self._board_with_wires([])
    assert board.num_wire_crosses() == 0
    board = self._board_with_wires([((2, 0), (2, 10))])
    assert board.num_wire_crosses() == 0
    board = self._board_with_wires([((2, 0), (2, 10)), ((3, 10), (9, 10))])
    assert board.num_wire_crosses() == 0
    board = self._board_with_wires([((2, 0), (2, 10)), ((2, 5), (9, 5))])
    assert board.num_wire_crosses() == 1

if __name__ == '__main__':
  main()
