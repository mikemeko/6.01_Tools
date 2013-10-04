"""
Script to analyze test results.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from collections import defaultdict
from colorsys import hls_to_rgb
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

def analyze(results_file):
  # individial results
  lines = [line.strip() for line in open(results_file).readlines()]
  results = [Test_Result(line) for line in lines[1:]]
  # grouped results
  results_by_identifier = defaultdict(list)
  for result in results:
    results_by_identifier[result.identifier].append(result)
  groups = [Test_Group(value) for value in results_by_identifier.values()]

  def label_heights(ax, rects):
    for rect in rects:
      w, h = rect.get_width(), rect.get_height()
      ax.text(rect.get_x() + w / 2, h + 100, str(h), ha='center', va='bottom')

  # overall results plot part 1
  fig, ax = pylab.subplots()
  num_solved_count_mapping = defaultdict(int)
  for group in groups:
    num_solved_count_mapping[len(group.successful_results)] += 1
  plot_keys = range(11)
  rects = pylab.bar([k - 0.5 for k in plot_keys],
      [num_solved_count_mapping[10 - key] for key in plot_keys])
  label_heights(ax, rects)
  pylab.title('Success')
  pylab.xlabel('Number of times failed out of 10')
  pylab.ylabel('Schematic count')

  # overall results plot part 2
  fig, ax = pylab.subplots()
  rects = pylab.bar([k - 0.5 for k in plot_keys],
      [sum(num_solved_count_mapping[10 - k] for k in range(0, k + 1)) for k in
      plot_keys])
  label_heights(ax, rects)
  pylab.title('Success')
  pylab.xlabel('Maximum number of times failed out of 10')
  pylab.ylabel('Schematic count')

  # overall results plot part 3
  pylab.figure()
  pylab.pie([num_solved_count_mapping[key] for key in plot_keys],
      labels=map(str, plot_keys), autopct='%1.f%%', pctdistance=0.9,
      colors=[hls_to_rgb(k/10./3,0.5,1) for k in plot_keys])
  pylab.title('Number of times solved out of 10')

  # success trend plots
  def trend_plot_success(attr):
    pylab.figure()
    success_mapping = defaultdict(list)
    for result in results:
      success_mapping[getattr(result, attr)].append(result.solved)
    pylab.plot(success_mapping.keys(), map(mean, success_mapping.values()),
        'go')
    pylab.xlabel(attr.split('_')[-1])
    pylab.ylabel('Success rate')
  trend_plot_success('num_nodes')
  trend_plot_success('num_components')
  trend_plot_success('num_schematic_pins')

  # success time vs. failure time
  fig, ax = pylab.subplots()
  solved = []
  failed = []
  for result in results:
    (solved if result.solved else failed).append(result.num_expanded)
  p1 = ax.hist(solved, bins=30, color='g', alpha=0.5)
  p2 = ax.hist(failed, bins=30, color='r', alpha=0.5)
  pylab.xlabel('Number of states expanded')
  pylab.ylabel('Run count')
  pylab.legend(['Successful runs', 'Failed runs'])

  # time trend plots
  def trend_plot_time(attr):
    fig, ax = pylab.subplots()
    solved_mapping = defaultdict(list)
    failed_mapping = defaultdict(list)
    #all_x = []
    #all_y = []
    #color = []
    for result in results:
      #all_x.append(getattr(result, attr) + (0 if result.solved else 0.1))
      #all_y.append(result.num_expanded)
      #color.append('g' if result.solved else 'r')
      (solved_mapping if result.solved else failed_mapping)[getattr(
          result, attr)].append(result.num_expanded)
    #ax.scatter(all_x, all_y, marker='x', color=color)
    for mapping, color in ((solved_mapping, 'g'), (failed_mapping, 'r')):
      plot_keys = sorted(mapping.keys())
      ax.errorbar(plot_keys, [mean(mapping[key]) for key in plot_keys],
          yerr=[std(mapping[key]) for key in plot_keys], color=color)
    pylab.legend(['Solved', 'Failed'])
    pylab.xlabel(attr.split('_')[-1])
    pylab.ylabel('Number of expanded states')
  trend_plot_time('num_nodes')
  trend_plot_time('num_components')
  trend_plot_time('num_schematic_pins')

  # protoboard quality plots
  def quality_plot(attr):
    fig, ax = pylab.subplots()
    num_wires_mapping = defaultdict(list)
    num_wire_crosses_mapping = defaultdict(list)
    total_wire_length_mapping = defaultdict(list)
    for result in results:
      if result.solved:
        num_wires_mapping[getattr(result, attr)].append(result.num_wires)
        num_wire_crosses_mapping[getattr(result, attr)].append(
            result.num_wire_crosses)
        total_wire_length_mapping[getattr(result, attr)].append(
            result.total_wire_length)
    for mapping, color in ((num_wires_mapping, 'g'), (num_wire_crosses_mapping,
        'r'), (total_wire_length_mapping, 'b')):
      plot_keys = sorted(mapping.keys())
      ax.errorbar(plot_keys, [mean(mapping[key]) for key in plot_keys],
          yerr=[std(mapping[key]) for key in plot_keys], color=color)
    pylab.legend(['Num wires', 'Num wire crosses', 'Total length'])
    pylab.xlabel(attr.split('_')[-1])
  quality_plot('num_nodes')
  quality_plot('num_components')
  quality_plot('num_schematic_pins')

  pylab.show()

if __name__ == '__main__':
  assert len(argv) == 2, 'No input'
  analyze(argv[1])
