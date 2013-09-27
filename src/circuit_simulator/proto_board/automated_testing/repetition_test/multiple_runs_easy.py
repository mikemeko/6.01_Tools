"""
Runs the layout algorithm multiple times on two different schematics of the same
    circuit and compares the results.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.automated_testing.test_schematic import (
    Schematic_Tester)
from circuit_simulator.proto_board.constants import MODE_PER_PAIR
from circuit_simulator.proto_board.constants import ORDER_DECREASING
from collections import defaultdict
from constants import EASY_SCHEMATIC_1
from constants import EASY_SCHEMATIC_2

def multiple_runs(schematic):
  """
  Runs the layout algorithm on the given |schematic| 500 times and returns a
      dictionary mapping hashes of the found layouts to the number of times they
      were found.
  """
  tester = Schematic_Tester(MODE_PER_PAIR, ORDER_DECREASING)
  counts = defaultdict(int)
  for i in xrange(500):
    print i, schematic
    proto_board = tester.test_schematic(schematic)[-1]
    counts[hash(proto_board.to_ascii() if proto_board else None)] += 1
  return counts

if __name__ == '__main__':
  counts_1 = multiple_runs(EASY_SCHEMATIC_1)
  print
  counts_2 = multiple_runs(EASY_SCHEMATIC_2)
  print
  print '\n'.join(map(str, sorted(counts_1.items())))
  print
  print '\n'.join(map(str, sorted(counts_2.items())))
  ###############################
  # (-8421700445019170113, 226) #
  # (-2029925199188032241, 230) #
  # (-901703899342649549, 21)   #
  # (7945660514142453099, 23)   #
  #                             #
  # (-8421700445019170113, 222) #
  # (-2029925199188032241, 232) #
  # (-901703899342649549, 21)   #
  # (7945660514142453099, 25)   #
  ###############################
