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
from constants import NUM_RUNS
from constants import SCHEMATIC_1
from constants import SCHEMATIC_2

def multiple_runs(schematic):
  """
  Runs the layout algorithm on the given |schematic| and returns a dictionary
      mapping hashes of the found layouts to the number of times they were
      found.
  """
  tester = Schematic_Tester(MODE_PER_PAIR, ORDER_DECREASING)
  counts = defaultdict(int)
  for i in xrange(NUM_RUNS):
    proto_board = tester.test_schematic(schematic)[-1]
    counts[hash(proto_board.to_ascii() if proto_board else None)] += 1
  return counts

if __name__ == '__main__':
  counts_1 = multiple_runs(SCHEMATIC_1)
  counts_2 = multiple_runs(SCHEMATIC_2)
  print
  print '\n'.join(map(str, sorted(counts_1.items())))
  print
  print '\n'.join(map(str, sorted(counts_2.items())))
