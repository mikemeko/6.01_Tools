"""
Script to analyze test data.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from collections import defaultdict
from matplotlib import pyplot as plt
from sys import argv

def sequence_generator():
  """
  Generator that produces 0, 1, 2, 3, etc.
  """
  i = 0
  while True:
    yield i
    i += 1

def get_int(val):
  """
  Returns the int value of |val| if it could be computed, or None otherwise.
  """
  try:
    return int(val)
  except:
    return None

class Test_Result:
  """
  Concise representation for results from on schematic.
  """
  def __init__(self, line):
    line = line.split(',')
    g = sequence_generator()
    self.file_name = line[g.next()]
    self.solved = line[g.next()] == 'True'
    self.solve_time = float(line[g.next()])
    self.num_resistors = get_int(line[g.next()])
    self.num_pots = get_int(line[g.next()])
    self.num_op_amps = get_int(line[g.next()])
    self.num_op_amp_packages = get_int(line[g.next()])
    self.num_motors = get_int(line[g.next()])
    self.head_present = int(line[g.next()] == 'True')
    self.robot_present = int(line[g.next()] == 'True')
    self.num_wires = get_int(line[g.next()])
    self.total_wire_length = get_int(line[g.next()])
    self.num_wire_crosses = get_int(line[g.next()])
    self.num_nodes = get_int(line[g.next()])

def compare(solved, unsolved, attr):
  """
  Compares the various values of |attr| in the |solved| versus |unsolved|
      schematics.
  """
  num_solved = defaultdict(int)
  for result in solved:
    num_solved[getattr(result, attr)] += 1
  num_unsolved = defaultdict(int)
  for result in unsolved:
    num_unsolved[getattr(result, attr)] += 1
  keys = sorted(set(num_solved.keys() + num_unsolved.keys()))
  fig, ax = plt.subplots()
  width = 0.35
  rects1 = ax.bar(keys, [num_solved[key] for key in keys], width, color='g')
  rects2 = ax.bar([key + width for key in keys], [num_unsolved[key] for key in
      keys], width, color='r')
  ax.set_title(attr)

def analyze(results_file):
  """
  Analyzes the results in the given |results_file|.
  """
  lines = [line.strip() for line in open(results_file).readlines()]
  results = [Test_Result(line) for line in lines[1:]]
  solved = [result for result in results if result.solved]
  unsolved = [result for result in results if not result.solved]
  print 'Success: {0:.2f}%'.format(100 * (float(len(solved)) / len(results)))
  compare(solved, unsolved, 'num_resistors')
  compare(solved, unsolved, 'num_pots')
  compare(solved, unsolved, 'num_op_amps')
  compare(solved, unsolved, 'num_motors')
  compare(solved, unsolved, 'head_present')
  compare(solved, unsolved, 'robot_present')
  compare(solved, unsolved, 'num_nodes')
  plt.show()

if __name__ == '__main__':
  assert len(argv) == 2, 'No input'
  analyze(argv[1])
