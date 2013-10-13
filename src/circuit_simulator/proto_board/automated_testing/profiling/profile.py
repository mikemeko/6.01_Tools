"""
Profiling.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.automated_testing.test_schematic import (
    Schematic_Tester)
from circuit_simulator.proto_board.constants import COST_TYPE_BLOCKING
from circuit_simulator.proto_board.constants import MODE_PER_PAIR
from circuit_simulator.proto_board.constants import ORDER_DECREASING
from cProfile import run

def profile():
  tester = Schematic_Tester(True, COST_TYPE_BLOCKING, MODE_PER_PAIR,
      ORDER_DECREASING, False)
  tester.test_schematic('circuit_simulator/proto_board/automated_testing/'
      'profiling/schematic.circsim')

if __name__ == '__main__':
  run('profile()')
