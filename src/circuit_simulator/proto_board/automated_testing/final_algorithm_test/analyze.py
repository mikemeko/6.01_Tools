"""
Analysis for test results on final algorithm.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from collections import defaultdict
from layout_badness import badness
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
    # attributes added to most recent test runs
    self.num_piece_crosses = get_int(line[10]) if len(line) > 10 else 0
    self.num_diagonal_wires = get_int(line[11]) if len(line) > 11 else 0
    self.num_occlusions = get_int(line[12]) if len(line) > 12 else 0

def analyze(result_file):
  lines = [line.strip() for line in open(result_file).readlines()]
  results = [Test_Result(line) for line in lines[1:]]
  print 'Success rate: %.2f' % (float(len([result for result in results if
      result.solved])) / len(results))
  # num trials
  fig, ax = pylab.subplots()
  pylab.xlim(xmin=0.5, xmax=10.5)
  pylab.ylim(ymin=0, ymax=44000)
  num_trials = defaultdict(int)
  for result in results:
    if result.num_forced_wires > 0:
      num_trials[4 + result.num_forced_wires] += 1
    else:
      for i in range(1, 5):
        if result.num_runs == i:
          num_trials[i] += 1
          break
  keys = sorted(num_trials.keys())
  values = [num_trials[key] for key in keys]
  labels = ['1\ntrail'] + ['%d\ntrials' % i for i in keys if 2 <= i <= 4] + [
      '1\nfailed\npair'] + ['%d\nfailed\npairs' % (i-4) for i in keys if i > 5]
  colors = ['g'] * 4 + ['r'] * (len(keys) - 4)
  width = 0.8
  rects = ax.bar(keys, values, width=width, color=colors)
  total = float(sum(rect.get_height() for rect in rects))
  for rect in rects:
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width() / 2., height + 400, '%d\n%.1f%%' % (
        int(height), int(height) / total * 100), ha='center', va='bottom')
  ax.set_xticks([i + width/2 for i in keys])
  ax.set_xticklabels(labels)
  pylab.xlabel('Number of trials')
  pylab.ylabel('Count')
  pylab.show()
  # time trend
  pylab.autoscale(enable=True)
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
  # badness comparison
  pylab.figure()
  badness_mapping = defaultdict(list)
  for result in results:
    if result.solved:
      properties = defaultdict(int)
      properties['num_wire_crossings'] = result.num_wire_crosses
      properties['num_wire_occlusions'] = result.num_occlusions
      properties['num_diagonal_wires'] = result.num_diagonal_wires
      properties['num_wire_piece_crossings'] = result.num_piece_crosses
      properties['num_wires'] = result.num_wires
      properties['total_wire_length'] = result.total_wire_length
      badness_mapping[result.num_schematic_pins].append(badness(properties))
  pylab.errorbar(badness_mapping.keys(), map(mean, badness_mapping.values()),
      yerr=map(se, badness_mapping.values()))
  pylab.xlabel('Number of pins')
  pylab.ylabel('Layout badness')
  pylab.show()

if __name__ == '__main__':
  analyze(argv[1])
