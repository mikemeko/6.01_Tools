"""
Script that runs automated layout test on a directory of test schematic files.
Options:
  Wiring:
    Mode:
      -a: all pairs
      -n: per node
      -p: per pair [DEFAULT]
    Order:
      -d: decreasing [DEFAULT]
      -i: increasing
  Resistors:
    -c: as components [DEFAULT]
    -w: as wires
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.main.constants import FILE_EXTENSION
from circuit_simulator.proto_board.constants import MODE_ALL_PAIRS
from circuit_simulator.proto_board.constants import MODE_PER_NODE
from circuit_simulator.proto_board.constants import MODE_PER_PAIR
from circuit_simulator.proto_board.constants import ORDER_DECREASING
from circuit_simulator.proto_board.constants import ORDER_INCREASING
from datetime import datetime
from os import walk
from os.path import basename
from os.path import join
from os.path import normpath
from sys import argv
from test_schematic import Schematic_Tester
from time import time

WIRING_MODE_OPTIONS = {'-a': MODE_ALL_PAIRS, '-n': MODE_PER_NODE,
    '-p': MODE_PER_PAIR}
WIRING_ORDER_OPTIONS = {'-d': ORDER_DECREASING, '-i': ORDER_INCREASING}
RESISTOR_OPTIONS = {'-c': True, '-w': False}

if __name__ == '__main__':
  solve_mode_options = filter(lambda o: o in WIRING_MODE_OPTIONS, argv)
  assert len(solve_mode_options) <= 1
  solve_mode = (WIRING_MODE_OPTIONS[solve_mode_options[0]] if solve_mode_options
      else MODE_PER_PAIR)
  solve_order_options = filter(lambda o: o in WIRING_ORDER_OPTIONS, argv)
  assert len(solve_order_options) <= 1
  solve_order = (WIRING_ORDER_OPTIONS[solve_order_options[0]] if
      solve_order_options else ORDER_DECREASING)
  resistor_options = filter(lambda o: o in RESISTOR_OPTIONS, argv)
  assert len(resistor_options) <= 1
  resistors_as_components = (RESISTOR_OPTIONS[resistor_options[0]] if
      resistor_options else True)
  start_time = time()
  tester = Schematic_Tester(resistors_as_components, solve_mode, solve_order)
  header = (
      'file',
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
  output_file_name = ('circuit_simulator/proto_board/automated_testing/'
      'test_results/%s_%s' % (basename(normpath(argv[1])),
      datetime.now().strftime('%d%b%I:%M%p')))
  open(output_file_name, 'w').write(';'.join(header))
  for dir_path, dir_names, file_names in walk(argv[1]):
    num_files = len(file_names)
    for n, file_name in enumerate(file_names):
      print '%d/%d' % (n + 1, num_files)
      if file_name.endswith(FILE_EXTENSION):
        print file_name
        for i in xrange(10):
          print 'run %d' % (i + 1)
          # [:-1] - don't include protoboard in result
          result = (file_name, i) + (
              tester.test_schematic(join(dir_path, file_name))[:-1])
          results = [line.strip() for line in open(output_file_name,
              'r').readlines()]
          results.append(';'.join(map(str, result)))
          open(output_file_name, 'w').write('\n'.join(results))
        print
  stop_time = time()
  print 'Time elapsed: %.3f seconds' % (stop_time - start_time)
