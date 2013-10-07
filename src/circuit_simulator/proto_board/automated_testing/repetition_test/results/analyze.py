"""
Script to analyze repetition test results.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from numpy import mean
from numpy import std
from sys import argv
import pylab

def sequence_generator():
  i = 0
  while True:
    yield i
    i += 1

def get_int(val):
  try:
    return int(val)
  except:
    return None

def get_float(val):
  try:
    return float(val)
  except:
    return None

def get_int_list(val):
  try:
    return map(int, [e.strip() for e in val[1:-1].split(',')])
  except:
    return None

class Test_Result:
  def __init__(self, line):
    line = line.split(';')
    g = sequence_generator()
    self.run = get_int(line[g.next()])
    self.solved = line[g.next()] == 'True'
    self.placement_time = get_float(line[g.next()])
    self.wiring_time = get_float(line[g.next()])
    self.total_time = self.placement_time + self.wiring_time
    self.num_expanded = get_int_list(line[g.next()])
    self.num_schematic_pins = get_int(line[g.next()])
    self.num_resistors = get_int(line[g.next()])
    self.num_pots = get_int(line[g.next()])
    self.num_op_amps = get_int(line[g.next()])
    self.num_op_amp_packages = get_int(line[g.next()])
    self.num_motors = get_int(line[g.next()])
    self.head_present = int(line[g.next()] == 'True')
    self.robot_present = int(line[g.next()] == 'True')
    self.num_components = (self.num_resistors + self.num_pots +
        self.num_op_amps + self.num_motors + self.head_present +
        self.robot_present)
    self.num_wires = get_int(line[g.next()])
    self.total_wire_length = get_int(line[g.next()])
    self.num_wire_crosses = get_int(line[g.next()])

def analyze(results_file):
  lines = [line.strip() for line in open(results_file).readlines()]
  results = [Test_Result(line) for line in lines[1:]]
  success_times = [result.wiring_time for result in results if result.solved]
  failure_times = [result.wiring_time for result in results if not
      result.solved]
  print 'Success rate: %.2f' % (float(len(success_times)) / len(results))
  if success_times:
    print 'Success stats: %.2f, %.2f' % (mean(success_times),
        std(success_times))
  if failure_times:
    print 'Failure stats: %.2f, %.2f' % (mean(failure_times),
        std(failure_times))
  if success_times:
    pylab.hist(success_times, color='g', bins=20, alpha=0.5)
  if failure_times:
    pylab.hist(failure_times, color='r', bins=20, alpha=0.5)
  pylab.show()

if __name__ == '__main__':
  assert len(argv) == 2, 'No input'
  analyze(argv[1])
