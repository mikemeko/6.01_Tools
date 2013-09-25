"""
Script to analyze test data.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from collections import defaultdict
from math import ceil
from numpy import mean
from numpy import std
from pylab import imshow
from pylab import show
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
    self.num_components = (self.num_resistors + self.num_pots +
        self.num_op_amps + self.num_motors + self.head_present +
        self.robot_present)
    self.num_wires = get_int(line[g.next()])
    self.total_wire_length = get_int(line[g.next()])
    self.num_wire_crosses = get_int(line[g.next()])
    self.num_nodes = get_int(line[g.next()])

def compare(solved, unsolved, attr):
  """
  Compares the various values of |attr| in the |solved| versus |unsolved|
      schematics.
  """
  solved_dict = defaultdict(list)
  for result in solved:
    solved_dict[getattr(result, attr)].append(result)
  unsolved_dict = defaultdict(list)
  for result in unsolved:
    unsolved_dict[getattr(result, attr)].append(result)
  print attr
  print '# #s \% _s _f'
  keys = sorted(set(solved_dict.keys() + unsolved_dict.keys()))
  for key in keys:
    key_total = len(solved_dict[key]) + len(unsolved_dict[key])
    print ('{0:d} {1:d} {2:.2f} '
        '{3:.2f} {4:.2f}'.format(key,
        key_total, float(len(solved_dict[key])) / key_total, mean([
        result.solve_time for result in solved_dict[key]]), mean([
        result.solve_time for result in unsolved_dict[key]])))

def analyze(results_file):
  """
  Analyzes the results in the given |results_file|.
  """
  lines = [line.strip() for line in open(results_file).readlines()]
  results = [Test_Result(line) for line in lines[1:]]
  solved = [result for result in results if result.solved]
  unsolved = [result for result in results if not result.solved]
  print 'Success rate: {0:.2f}%'.format((100. * len(solved) / len(results)))
  print 'Solve time: {0:.2f}, {1:.2f}'.format(mean([result.solve_time for result
      in solved]), std([result.solve_time for result in solved]))
  print 'Failure time: {0:.2f}, {1:.2f}'.format(mean([result.solve_time for
      result in unsolved]), std([result.solve_time for result in unsolved]))
  print 'Num wires: {0:.2f}, {1:.2f}'.format(mean([result.num_wires for result
      in solved]), std([result.num_wires for result in solved]))
  print 'Total wire length: {0:.2f}, {1:.2f}'.format(mean([
      result.total_wire_length for result in solved]), std([
      result.total_wire_length for result in solved]))
  print 'Num wire crosses: {0:.2f}, {1:.2f}'.format(mean([
      result.num_wire_crosses for result in solved]), std([
      result.num_wire_crosses for result in solved]))
  print
  compare(solved, unsolved, 'num_resistors')
  print
  compare(solved, unsolved, 'num_pots')
  print
  compare(solved, unsolved, 'num_op_amps')
  print
  compare(solved, unsolved, 'num_motors')
  print
  compare(solved, unsolved, 'head_present')
  print
  compare(solved, unsolved, 'robot_present')
  print
  compare(solved, unsolved, 'num_components')
  print
  compare(solved, unsolved, 'num_nodes')
  size = int(ceil(len(results) ** 0.5))
  grid = [[0.5] * size for i in xrange(int(ceil(float(len(results)) / size)))]
  for i, result in enumerate(results):
    grid[i / size][i % size] = 1 - result.solved
  imshow(grid, interpolation='nearest', cmap='Reds')
  show()

if __name__ == '__main__':
  assert len(argv) == 2, 'No input'
  analyze(argv[1])
