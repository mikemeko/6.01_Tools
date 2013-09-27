"""
Runs the layout algorithm multiple times on a difficult schematic and keeps
    track of the amount of success/failure.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.automated_testing.test_schematic import (
    Schematic_Tester)
from circuit_simulator.proto_board.constants import MODE_PER_PAIR
from circuit_simulator.proto_board.constants import ORDER_DECREASING
from constants import HARD_SCHEMATIC

def multiple_runs():
  tester = Schematic_Tester(MODE_PER_PAIR, ORDER_DECREASING)
  success_count = 0
  failure_count = 0
  for i in xrange(100):
    print i
    success = tester.test_schematic(HARD_SCHEMATIC)[0]
    print success
    success_count += success
    failure_count += not success
  return success_count, failure_count

if __name__ == '__main__':
  print multiple_runs()
  #  ************
  #  * (90, 10) *
  #  ************
