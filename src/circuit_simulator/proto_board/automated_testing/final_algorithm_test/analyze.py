"""
Analysis for test results on final algorithm.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from collections import defaultdict
from numpy import mean
from scipy.stats import sem
from sys import argv
import pylab

def se(l):
  return 1.96 * sem(l)

def get_int(val):
  try:
    return int(float(val))
  except:
    return None

def get_float(val):
  try:
    return float(val)
  except:
    return None

class Test_Result:
  def __init__(self, line):
    line = line.split(';')
    self.file_name = line[0]
    self.run = get_int(line[1])
    self.solved = line[2] == 'True'
    self.total_time = get_float(line[3])
    self.num_schematic_pins = get_int(line[4])
    self.num_wires = get_int(line[5])
    self.num_wire_crosses = get_int(line[6])
    self.total_wire_length = get_int(line[7])
    self.num_runs = get_int(line[8])
    self.num_forced_wires = get_int(line[9])

def analyze(result_file):
  lines = [line.strip() for line in open(result_file).readlines()]
  results = [Test_Result(line) for line in lines[1:]]
  print 'Success rate: %.2f' % (float(len([result for result in results if
      result.solved])) / len(results))
  # time trend
  pylab.figure()
  time_mapping = defaultdict(list)
  for result in results:
    if result.solved:
      time_mapping[result.num_schematic_pins].append(result.total_time)
  pylab.errorbar(time_mapping.keys(), map(mean, time_mapping.values()),
      yerr=map(se, time_mapping.values()))
  pylab.xlabel('Number of pins')
  pylab.ylabel('Total time (seconds)')
  # quality
  pylab.figure()
  num_wires_mapping = defaultdict(list)
  num_wire_crosses_mapping = defaultdict(list)
  total_wire_length_mapping = defaultdict(list)
  for result in results:
    if result.solved:
      num_wires_mapping[result.num_schematic_pins].append(result.num_wires)
      num_wire_crosses_mapping[result.num_schematic_pins].append(
          result.num_wire_crosses)
      total_wire_length_mapping[result.num_schematic_pins].append(
          result.total_wire_length)
  ax1 = pylab.subplot(311)
  ax2 = pylab.subplot(312)
  ax3 = pylab.subplot(313)
  ax1.errorbar(num_wires_mapping.keys(), map(mean, num_wires_mapping.values()),
      yerr=map(se, num_wires_mapping.values()))
  ax1.set_ylabel('Wires')
  ax2.errorbar(num_wire_crosses_mapping.keys(), map(mean,
      num_wire_crosses_mapping.values()),
      yerr=map(se, num_wire_crosses_mapping.values()))
  ax2.set_ylabel('Wire crosses')
  ax3.errorbar(total_wire_length_mapping.keys(), map(mean,
      total_wire_length_mapping.values()),
      yerr=map(se, total_wire_length_mapping.values()))
  ax3.set_ylabel('Total wire length')
  pylab.xlabel('Number of pins')
  # forced wire trend
  pylab.figure()
  forced_wire_mapping = defaultdict(list)
  for result in results:
    if result.solved:
      forced_wire_mapping[result.num_schematic_pins].append(
          result.num_forced_wires)
  pylab.errorbar(forced_wire_mapping.keys(), map(mean,
      forced_wire_mapping.values()), yerr=map(se, forced_wire_mapping.values()))
  pylab.xlabel('Number of pins')
  pylab.ylabel('Number of forced wires')
  pylab.show()

if __name__ == '__main__':
  analyze(argv[1])
