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
  Placement:
    -b: blocking [DEFAULT]
    -t: distance
  Resistors:
    -c: as components [DEFAULT]
    -w: as wires
  Search:
    -r: A* [DEFAULT]
    -s: Best First
  Filter wire length:
    -f: True
    False otherwise [DEFAULT]
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.main.constants import FILE_EXTENSION
from circuit_simulator.proto_board.constants import COST_TYPE_BLOCKING
from circuit_simulator.proto_board.constants import COST_TYPE_DISTANCE
from circuit_simulator.proto_board.constants import MODE_ALL_PAIRS
from circuit_simulator.proto_board.constants import MODE_PER_NODE
from circuit_simulator.proto_board.constants import MODE_PER_PAIR
from circuit_simulator.proto_board.constants import ORDER_DECREASING
from circuit_simulator.proto_board.constants import ORDER_INCREASING
from collections import defaultdict
from datetime import datetime
from os import walk
from os.path import basename
from os.path import isfile
from os.path import join
from os.path import normpath
from sys import argv
from test_schematic import Schematic_Tester
from time import time

WIRING_MODE_OPTIONS = {'-a': MODE_ALL_PAIRS, '-n': MODE_PER_NODE,
    '-p': MODE_PER_PAIR}
WIRING_ORDER_OPTIONS = {'-d': ORDER_DECREASING, '-i': ORDER_INCREASING}
PLACEMENT_OPTIONS = {'-b': COST_TYPE_BLOCKING, '-t': COST_TYPE_DISTANCE}
RESISTOR_OPTIONS = {'-c': True, '-w': False}
SEARCH_OPTIONS = {'-r': False, '-s': True}
WIRE_FILTER_OPTIONS = {'-f': True}

if __name__ == '__main__':
  # schematics that have already been solved
  if isfile(argv[2]):
    counts = defaultdict(int)
    for line in open(argv[2]).readlines():
      counts[line.split(';')[0]] += 1
    solved = set(name for name, count in counts.items() if count == 10)
  else:
    solved = set()
  # options
  solve_mode_options = filter(WIRING_MODE_OPTIONS.has_key, argv)
  assert len(solve_mode_options) <= 1
  solve_mode = (WIRING_MODE_OPTIONS[solve_mode_options[0]] if solve_mode_options
      else MODE_PER_PAIR)
  solve_order_options = filter(WIRING_ORDER_OPTIONS.has_key, argv)
  assert len(solve_order_options) <= 1
  solve_order = (WIRING_ORDER_OPTIONS[solve_order_options[0]] if
      solve_order_options else ORDER_DECREASING)
  placement_options = filter(PLACEMENT_OPTIONS.has_key, argv)
  assert len(placement_options) <= 1
  cost_type = (PLACEMENT_OPTIONS[placement_options[0]] if placement_options
      else COST_TYPE_BLOCKING)
  resistor_options = filter(RESISTOR_OPTIONS.has_key, argv)
  assert len(resistor_options) <= 1
  resistors_as_components = (RESISTOR_OPTIONS[resistor_options[0]] if
      resistor_options else True)
  search_options = filter(SEARCH_OPTIONS.has_key, argv)
  assert len(search_options) <= 1
  best_first = SEARCH_OPTIONS[search_options[0]] if search_options else False
  wire_filter_options = filter(WIRE_FILTER_OPTIONS.has_key, argv)
  assert len(wire_filter_options) <= 1
  filter_wire_lengths = (WIRE_FILTER_OPTIONS[wire_filter_options[0]] if
      wire_filter_options else False)
  start_time = time()
  tester = Schematic_Tester(resistors_as_components, cost_type, solve_mode,
      solve_order, best_first, filter_wire_lengths)
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
      if file_name.endswith(FILE_EXTENSION) and file_name not in solved:
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
