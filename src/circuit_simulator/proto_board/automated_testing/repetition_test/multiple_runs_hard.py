"""
Runs the layout algorithm multiple times on a difficult schematic and keeps
    track of the amount of success/failure.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.automated_testing.test_schematic import (
    Schematic_Tester)
from circuit_simulator.proto_board.constants import MODE_PER_PAIR
from circuit_simulator.proto_board.constants import ORDER_DECREASING
from ntpath import basename
from sys import argv
import pylab

def multiple_runs(schematic):
  tester = Schematic_Tester(MODE_PER_PAIR, ORDER_DECREASING)
  success_expanded = []
  failure_expanded = []
  for i in xrange(100):
    test_results = tester.test_schematic(schematic)
    success = test_results[0]
    num_expanded = test_results[1]
    print i, success, num_expanded
    (success_expanded if success else failure_expanded).append(num_expanded)
  if failure_expanded:
    pylab.hist(failure_expanded, color='r', alpha=0.5)
  if success_expanded:
    pylab.hist(success_expanded, color='g', alpha=0.5)
  pylab.savefig('variability_%s.png' % basename(schematic).split('.')[0])

if __name__ == '__main__':
  assert len(argv) == 2, 'No input'
  multiple_runs(argv[1])
