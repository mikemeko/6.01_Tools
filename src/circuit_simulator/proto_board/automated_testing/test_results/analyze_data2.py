"""
Script to analyze test results.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from collections import defaultdict
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
    self.file_name = line[g.next()]
    self.identifier = self.file_name.split('.')[0]
    self.run = get_int(line[g.next()])
    self.solved = line[g.next()] == 'True'
    self.placement_time = get_float(line[g.next()])
    self.wiring_time = get_float(line[g.next()])
    self.total_time = self.placement_time + self.wiring_time
    self.num_expanded = get_int_list(line[g.next()])
    if self.num_expanded is None:
      self.num_expanded = [0]
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
    self.num_loc_pairs = get_int(line[g.next()])

class Test_Group:
  def __init__(self, group_results):
    self.num_schematic_pins = group_results[0].num_schematic_pins
    self.num_components = group_results[0].num_components
    self.num_nodes = group_results[0].num_nodes
    self.num_loc_pairs = group_results[0].num_loc_pairs
    self.successful_results = filter(lambda r: r.solved, group_results)
    self.success_rate = float(len(self.successful_results)) / len(group_results)

def analyze(results_file):
  # individial results
  lines = [line.strip() for line in open(results_file).readlines()]
  results = [Test_Result(line) for line in lines[1:]]
  # grouped results
  results_by_identifier = defaultdict(list)
  for result in results:
    results_by_identifier[result.identifier].append(result)
  groups = [Test_Group(value) for value in results_by_identifier.values()]

  def label_heights(ax, rects, max_height):
    max_height = float(max_height)
    for rect in rects:
      w, h = rect.get_width(), rect.get_height()
      ax.text(rect.get_x() + w / 2, h + 150, '%d\n%.1f%%' % (h,
          100 * h / max_height), ha='center', va='bottom')

  # overall results plot part 1
  fig, ax = pylab.subplots()
  num_solved_count_mapping = defaultdict(int)
  for group in groups:
    num_solved_count_mapping[len(group.successful_results)] += 1
  plot_keys = range(11)
  rects = pylab.bar([k - 0.5 for k in plot_keys],
      [num_solved_count_mapping[key] for key in plot_keys])
  label_heights(ax, rects, sum(rect.get_height() for rect in rects))
  pylab.title('Success')
  pylab.xlabel('Number of times failed out of 10')
  pylab.ylabel('Schematic count')

  # overall results plot part 2
  fig, ax = pylab.subplots()
  rects = pylab.bar([k - 0.5 for k in plot_keys],
      [sum(num_solved_count_mapping[k] for k in range(0, k + 1)) for k in
      plot_keys])
  label_heights(ax, rects, rects[-1].get_height())
  pylab.title('Success')
  pylab.xlabel('Maximum number of times failed out of 10')
  pylab.ylabel('Schematic count')

  # success trend plots
  def trend_plot_success(attr):
    fig, ax = pylab.subplots()
    success_mapping = defaultdict(list)
    for group in groups:
      success_mapping[getattr(group, attr)].append(group.success_rate)
    ax.bar(success_mapping.keys(), map(len, success_mapping.values()),
        alpha=0.2, color='g')
    ax.set_xlabel(attr.split('_')[-1])
    ax.set_ylabel('Count')
    ax2 = ax.twinx()
    ax2.errorbar([k + 0.5 for k in success_mapping.keys()], map(mean,
        success_mapping.values()), map(std, success_mapping.values()))
    ax2.set_ylabel('Success rate')
  trend_plot_success('num_nodes')
  trend_plot_success('num_components')
  trend_plot_success('num_schematic_pins')
  trend_plot_success('num_loc_pairs')

  # time trend plots
  def trend_plot_time(attr, f=lambda result: max(result.num_expanded)):
    solved_mapping = defaultdict(list)
    failed_mapping = defaultdict(list)
    for result in results:
      (solved_mapping if result.solved else failed_mapping)[getattr(
          result, attr)].append(f(result))
    keys = sorted(solved_mapping.keys())
    sample_keys = [keys[i * len(keys) / 4] for i in (1, 2, 3)]
    pylab.figure()
    pylab.subplot(311)
    pylab.title('%s %s' % (attr.split('_')[-1], sample_keys))
    log = False
    pylab.hist(solved_mapping[sample_keys[0]], color='g', alpha=0.5, bins=20,
        log=log)
    if sample_keys[0] in failed_mapping:
      pylab.hist(failed_mapping[sample_keys[0]], color='r', alpha=0.5, bins=20,
          log=log)
    pylab.subplot(312)
    pylab.hist(solved_mapping[sample_keys[1]], color='g', alpha=0.5, bins=20,
        log=log)
    if sample_keys[1] in failed_mapping:
      pylab.hist(failed_mapping[sample_keys[1]], color='r', alpha=0.5, bins=20,
          log=log)
    pylab.subplot(313)
    pylab.hist(solved_mapping[sample_keys[2]], color='g', alpha=0.5, bins=20,
        log=log)
    if sample_keys[2] in failed_mapping:
      pylab.hist(failed_mapping[sample_keys[2]], color='r', alpha=0.5, bins=20,
          log=log)
  trend_plot_time('num_nodes')
  trend_plot_time('num_components')
  trend_plot_time('num_schematic_pins')
  trend_plot_time('num_loc_pairs')

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
    ax2 = ax.twinx()
    ax2.bar(num_wires_mapping.keys(), map(len, num_wires_mapping.values()),
        alpha=0.2, color='b')
  quality_plot('num_nodes')
  quality_plot('num_components')
  quality_plot('num_schematic_pins')
  quality_plot('num_loc_pairs')

  pylab.show()

if __name__ == '__main__':
  assert len(argv) == 2, 'No input'
  analyze(argv[1])