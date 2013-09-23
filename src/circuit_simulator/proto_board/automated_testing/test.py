"""
Script that runs automated layout test on a directory of test schematic files.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.main.constants import FILE_EXTENSION
from datetime import datetime
from os import walk
from os.path import basename
from os.path import join
from os.path import normpath
from sys import argv
from test_schematic import test_schematic
from time import time

if __name__ == '__main__':
  assert len(argv) == 2
  start_time = time()
  header = ('file', 'solved', 'solve_time', 'num_resistors', 'num_pots',
      'num_op_amps', 'num_op_amp_packages', 'num_motors', 'head_present',
      'robot_present', 'num_wires', 'total_wire_length', 'num_wire_crosses',
      'num_nodes')
  output_file_name = ('circuit_simulator/proto_board/automated_testing/'
      'test_results/%s_%s' % (basename(normpath(argv[1])),
      datetime.now().strftime('%d%b%I:%M%p')))
  open(output_file_name, 'w').write(','.join(header))
  for dir_path, dir_names, file_names in walk(argv[1]):
    num_files = len(file_names)
    for n, file_name in enumerate(file_names):
      print '%d/%d' % (n + 1, num_files)
      if file_name.endswith(FILE_EXTENSION):
        print file_name
        result = (file_name,) + test_schematic(join(dir_path, file_name))
        results = [line.strip() for line in open(output_file_name,
            'r').readlines()]
        results.append(','.join(map(str, result)))
        open(output_file_name, 'w').write('\n'.join(results))
        print
  stop_time = time()
  print 'Time elapsed: %.3f seconds' % (stop_time - start_time)
