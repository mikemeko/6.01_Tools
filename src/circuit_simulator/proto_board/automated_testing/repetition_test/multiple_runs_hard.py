"""
Runs the layout algorithm multiple times on a difficult schematic and keeps
    track of the amount of success/failure.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.automated_testing.test_schematic import (
    Schematic_Tester)
from circuit_simulator.proto_board.constants import MODE_PER_PAIR
from circuit_simulator.proto_board.constants import ORDER_DECREASING
from os.path import basename
from os.path import normpath
from sys import argv

def multiple_runs(schematic):
  output_file_name = ('circuit_simulator/proto_board/automated_testing/'
      'repetition_test/results/%s_results' %
      basename(normpath(schematic)).split('.')[0])
  header = (
      'run #',
      'solved',
      'placement_time',
      'wiring_time',
      'num_expanded',
      'num_schematic_pins',
      'num_resistors',
      'num_pots',
      'num_op_amps',
      'num_op_amp_packages',
      'num_motors',
      'head_present',
      'robot_present',
      'num_wires',
      'total_wire_length',
      'num_wire_crosses',
      'num_nodes',
      'num_loc_pairs')
  open(output_file_name, 'w').write(';'.join(header))
  tester = Schematic_Tester(True, MODE_PER_PAIR, ORDER_DECREASING)
  for i in xrange(500):
    print 'run %d' % i
    result = (i,) + tester.test_schematic(schematic)[:-1]
    results = [line.strip() for line in open(output_file_name,
        'r').readlines()]
    results.append(';'.join(map(str, result)))
    open(output_file_name, 'w').write('\n'.join(results))

if __name__ == '__main__':
  assert len(argv) == 2, 'No input'
  multiple_runs(argv[1])
