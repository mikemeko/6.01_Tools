"""
Script that runs automated layout test on a directory of test schematic files.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.main.constants import FILE_EXTENSION
from matplotlib import pyplot
from os import walk
from os.path import join
from sys import argv
from test_schematic import test_schematic
from time import time

if __name__ == '__main__':
  assert len(argv) == 2
  start_time = time()
  results = []
  for dir_path, dir_names, file_names in walk(argv[1]):
    for file_name in file_names:
      if file_name.endswith(FILE_EXTENSION):
        print file_name
        success, run_time = test_schematic(join(dir_path, file_name))
        results.append((file_name, success, run_time))
        print
  stop_time = time()
  print 'Time elapsed: %.3f seconds' % (stop_time - start_time)
  pyplot.bar(left=range(len(results)), height=[t for f, s, t in results],
      color=['green' if s else 'red' for f, s, t in results])
  pyplot.xlabel('Test schematics')
  pyplot.ylabel('Time (seconds)')
  pyplot.xticks([i + 0.5 for i in xrange(len(results))],
      [f.split('.')[0] for f, s, t in results], rotation=60, size='small')
  pyplot.show()
