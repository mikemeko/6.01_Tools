"""
Script to analyze test results.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from collections import defaultdict
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

def mean(l):
  assert l
  return float(sum(l)) / len(l)

class Test_Result:
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

class Test_Group:
  def __init__(self, group_results):
    self.num_schematic_pins = group_results[0].num_schematic_pins
    self.num_components = group_results[0].num_components
    self.num_nodes = group_results[0].num_nodes
    self.successful_results = filter(lambda r: r.solved, group_results)
    self.success_rate = float(len(self.successful_results)) / len(group_results)
    self.failed_results = filter(lambda r: not r.solved, group_results)

def analyze(results_file):
  # individial results
  lines = [line.strip() for line in open(results_file).readlines()]
  results = [Test_Result(line) for line in lines[1:]]
  # grouped results
  results_by_identifier = defaultdict(list)
  for result in results:
    results_by_identifier[result.identifier].append(result)
  groups = [Test_Group(value) for value in results_by_identifier.values()]
  # overall results plot
  pylab.figure()
  num_solved_count_mapping = defaultdict(int)
  for group in groups:
    num_solved_count_mapping[len(group.successful_results)] += 1
  plot_keys = range(11)
  pylab.plot(plot_keys, [num_solved_count_mapping[key] for key in plot_keys],
      'o--')
  pylab.title('success')
  # num nodes vs. success rate plot
  pylab.figure()
  nodes_success_mapping = defaultdict(list)
  for result in results:
    nodes_success_mapping[result.num_nodes].append(result.solved)
  pylab.plot(nodes_success_mapping.keys(), map(mean,
      nodes_success_mapping.values()), 'o')
  pylab.title('num nodes vs. success')
  # num components vs. success rate plot
  pylab.figure()
  components_success_mapping = defaultdict(list)
  for result in results:
    components_success_mapping[result.num_components].append(result.solved)
  pylab.plot(components_success_mapping.keys(), map(mean,
      components_success_mapping.values()), 'o')
  pylab.title('num components vs. success')
  # num pins vs. success rate plot
  pylab.figure()
  pins_success_mapping = defaultdict(list)
  for result in results:
    pins_success_mapping[result.num_schematic_pins].append(result.solved)
  pylab.plot(pins_success_mapping.keys(), map(mean,
      pins_success_mapping.values()), 'o')
  pylab.title('num pins vs. success')
  # num nodes vs. solved num expanded mean plot
  pylab.figure()
  nodes_expanded_mapping = defaultdict(list)
  for result in results:
    if result.solved:
      nodes_expanded_mapping[result.num_nodes].append(result.num_expanded)
  pylab.boxplot([nodes_expanded_mapping[key] for key in sorted(
      nodes_expanded_mapping.keys())])
  pylab.title('num nodes vs. expanded')
  # num components vs. solved num expanded mean plot
  pylab.figure()
  components_expanded_mapping = defaultdict(list)
  for result in results:
    if result.solved:
      components_expanded_mapping[result.num_components].append(
          result.num_expanded)
  pylab.boxplot([components_expanded_mapping[key] for key in sorted(
      components_expanded_mapping.keys())])
  pylab.title('num components vs. expanded')
  # num pins vs. solved num expanded mean plot
  pylab.figure()
  pins_expanded_mapping = defaultdict(list)
  for result in results:
    if result.solved:
      pins_expanded_mapping[result.num_schematic_pins].append(
          result.num_expanded)
  pylab.boxplot([pins_expanded_mapping[key] for key in sorted(
      pins_expanded_mapping.keys())])
  pylab.title('num pins vs. expanded')
  # show
  pylab.show()

if __name__ == '__main__':
  assert len(argv) == 2, 'No input'
  analyze(argv[1])
