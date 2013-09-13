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

if __name__ == '__main__':
  assert len(argv) == 2
  results = []
  for dir_path, dir_names, file_names in walk(argv[1]):
    for file_name in file_names:
      if file_name.endswith(FILE_EXTENSION):
        success, time = test_schematic(join(dir_path, file_name))
        results.append((file_name, success, time))
  pyplot.bar(left=range(len(results)), height=[t for f, s, t in results],
      color=['green' if s else 'red' for f, s, t in results])
  pyplot.xlabel('Test schematics')
  pyplot.ylabel('Time (seconds)')
  pyplot.show()
