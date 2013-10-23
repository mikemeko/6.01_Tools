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
    return int(float(val))
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
  def __str__(self):
    return ('%s: identifier=%s, run=%s, solved=%s, placement_time=%s, '
        'wiring_time=%s, total_time=%s, num_expanded=%s, num_pin=%s, '
        'num_nodes=%s, num_loc_pairs=%s, num_wires=%s, num_wire_crosses=%s, '
        'total_wire_length=%s, ' % (self.file_name, self.identifier, self.run,
        self.solved, self.placement_time, self.wiring_time, self.total_time,
        self.num_expanded, self.num_schematic_pins, self.num_nodes,
        self.num_loc_pairs, self.num_wires, self.num_wire_crosses,
        self.total_wire_length))

class Test_Group:
  def __init__(self, group_results):
    self.identifier = group_results[0].identifier
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
  print 'Overall success rate: %.2f' % (float(len([result for result in results
      if result.solved])) / len(results))
  # grouped results
  results_by_identifier = defaultdict(list)
  for result in results:
    results_by_identifier[result.identifier].append(result)
  groups = [Test_Group(value) for value in results_by_identifier.values()]
  hard_schematics = sorted(group.identifier for group in groups if
      group.success_rate == 0)
  print '\n'.join(hard_schematics)

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
  pylab.xlabel('Number of times solved out of 10')
  pylab.ylabel('Schematic count')

  # overall results plot part 2
  fig, ax = pylab.subplots()
  rects = pylab.bar([k - 0.5 for k in plot_keys],
      [sum(num_solved_count_mapping[k] for k in range(0, k + 1)) for k in
      plot_keys])
  label_heights(ax, rects, rects[-1].get_height())
  pylab.title('Success')
  pylab.xlabel('Maximum number of times solved out of 10')
  pylab.ylabel('Schematic count')

  # success trend plots
  def trend_plot_success(attr):
    fig, ax = pylab.subplots()
    success_mapping = defaultdict(list)
    for group in groups:
      success_mapping[getattr(group, attr)].append(group.success_rate)
    ax.bar(success_mapping.keys(), map(len, success_mapping.values()),
        alpha=0.2, color='g')
    ax.set_xlabel('Number of %s' % attr.split('_')[-1])
    ax.set_ylabel('Count')
    ax2 = ax.twinx()
    ax2.errorbar([k for k in success_mapping.keys()], map(mean,
        success_mapping.values()), map(std, success_mapping.values()))
    ax2.set_ylabel('Success rate')
  trend_plot_success('num_nodes')
  trend_plot_success('num_components')
  trend_plot_success('num_schematic_pins')
  trend_plot_success('num_loc_pairs')

  # time trend plots
  def trend_plot_time(attr):
    fig, ax = pylab.subplots()
    success_mapping = defaultdict(list)
    failure_mapping = defaultdict(list)
    for result in results:
      (success_mapping if result.solved else failure_mapping)[getattr(result,
          attr)].append(result.wiring_time)
    bp = ax.boxplot(success_mapping.values(), positions=success_mapping.keys(),
        sym='')
    pylab.setp(bp['boxes'], color='green')
    pylab.setp(bp['whiskers'], color='green')
    bp = ax.boxplot(failure_mapping.values(), positions=failure_mapping.keys(),
        sym='')
    pylab.setp(bp['boxes'], color='red')
    pylab.setp(bp['whiskers'], color='red')
    ax.set_xlabel('Number of %s' % attr.split('_')[-1])
    ax.set_ylabel('Wiring time')
  trend_plot_time('num_nodes')
  trend_plot_time('num_components')
  trend_plot_time('num_schematic_pins')
  trend_plot_time('num_loc_pairs')

  # time trend hists
  def trend_hist_time(attr, f=lambda result: result.wiring_time):
    solved_mapping = defaultdict(list)
    failed_mapping = defaultdict(list)
    for result in results:
      (solved_mapping if result.solved else failed_mapping)[getattr(
          result, attr)].append(f(result))
    keys = sorted(solved_mapping.keys())
    sample_keys = [keys[i * len(keys) / 4] for i in (1, 2, 3)]
    pylab.figure()
    ax1 = pylab.subplot(311)
    ax1.set_ylabel('%d %s' % (sample_keys[0], attr.split('_')[-1]))
    log = False
    pylab.hist(solved_mapping[sample_keys[0]], color='g', alpha=0.50,
        log=log)
    if sample_keys[0] in failed_mapping:
      pylab.hist(failed_mapping[sample_keys[0]], color='r', alpha=0.5,
          log=log)
    ax2 = pylab.subplot(312)
    ax2.set_ylabel('%d %s' % (sample_keys[1], attr.split('_')[-1]))
    pylab.hist(solved_mapping[sample_keys[1]], color='g', alpha=0.5,
        log=log)
    if sample_keys[1] in failed_mapping:
      pylab.hist(failed_mapping[sample_keys[1]], color='r', alpha=0.5,
          log=log)
    ax3 = pylab.subplot(313)
    ax3.set_ylabel('%d %s' % (sample_keys[2], attr.split('_')[-1]))
    ax3.set_xlabel('Wiring time')
    pylab.hist(solved_mapping[sample_keys[2]], color='g', alpha=0.5,
        log=log)
    if sample_keys[2] in failed_mapping:
      pylab.hist(failed_mapping[sample_keys[2]], color='r', alpha=0.5,
          log=log)
  trend_hist_time('num_nodes')
  trend_hist_time('num_components')
  trend_hist_time('num_schematic_pins')
  trend_hist_time('num_loc_pairs')

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
    ax.bar(num_wires_mapping.keys(), map(len, num_wires_mapping.values()),
        alpha=0.2, color='b')
    ax.set_xlabel('Number of %s' % attr.split('_')[-1])
    ax.set_ylabel('Count')
    ax2 = ax.twinx()
    for mapping, color in ((num_wires_mapping, 'g'), (num_wire_crosses_mapping,
        'r'), (total_wire_length_mapping, 'b')):
      plot_keys = sorted(mapping.keys())
      ax2.errorbar(plot_keys, [mean(mapping[key]) for key in plot_keys],
          yerr=[std(mapping[key]) for key in plot_keys], color=color)
    pylab.legend(['Num wires', 'Num wire crosses', 'Total wire length'],
        bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode='expand',
        borderaxespad=0.)
  quality_plot('num_nodes')
  quality_plot('num_components')
  quality_plot('num_schematic_pins')
  quality_plot('num_loc_pairs')

  pylab.show()

if __name__ == '__main__':
  assert len(argv) == 2, 'No input'
  analyze(argv[1])
