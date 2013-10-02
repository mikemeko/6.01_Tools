"""
Script to analyze test results.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from collections import defaultdict
from sys import argv

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

class Test_Result:
  """
  Concise representation for results from one run.
  """
  def __init__(self, line):
    line = line.split(',')
    g = sequence_generator()
    self.file_name = line[g.next()]
    self.identifier = self.file_name.split('.')[0]
    self.run = get_int(line[g.next()])
    self.solved = line[g.next()] == 'True'
    self.num_expanded = get_int(line[g.next()])
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
    self.num_nodes = get_int(line[g.next()])

def analyze(results_file):
  """
  Analyzes the results in the given |results_file|.
  """
  lines = [line.strip() for line in open(results_file).readlines()]
  results = [Test_Result(line) for line in lines[1:]]
  results_by_identifier = defaultdict(list)
  for result in results:
    results_by_identifier[result.identifier].append(result)

if __name__ == '__main__':
  assert len(argv) == 2, 'No input'
  analyze(argv[1])
