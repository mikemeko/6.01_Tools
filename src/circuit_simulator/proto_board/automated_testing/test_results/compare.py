"""
Script to generate comparison plots.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from analyze_data import Test_Group
from analyze_data import Test_Result
from collections import defaultdict
from numpy import mean
from numpy import std
from scipy.stats import sem
from sys import argv
import pylab

def se(l):
  """
  Computes 1.96 times the standard error for |l|.
  """
  return 1.96 * sem(l)

colors = ['r', 'b', 'g', 'c', 'm']

def compare(files, methods):
  all_results = []
  all_groups = []
  for f in files:
    lines = [line.strip() for line in open(f).readlines()]
    results = [Test_Result(line) for line in lines[1:]]
    all_results.append(results)
    results_by_identifier = defaultdict(list)
    for result in results:
      results_by_identifier[result.identifier].append(result)
    groups = [Test_Group(value) for value in results_by_identifier.values()]
    all_groups.append(groups)

  # success plot
  pylab.figure()
  plot_keys = range(11)
  all_successes = []
  for groups in all_groups:
    num_solved_count_mapping = defaultdict(int)
    for group in groups:
      num_solved_count_mapping[len(group.successful_results)] += 1
    all_successes.append([num_solved_count_mapping[k] for k in plot_keys])
  width = 0.9 / len(files)
  for i, successes in enumerate(all_successes):
    pylab.bar([k + i * width for k in plot_keys], successes, width,
        color=colors[i])
  pylab.xlabel('Number of times succeeded out of 10')
  pylab.ylabel('Count')
  pylab.legend(methods, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
        ncol=len(methods), mode='expand', borderaxespad=0.)

  # success table
  num_schematics = sum(all_successes[0])
  for i, method in enumerate(methods):
    s = method
    t = ''
    for count in all_successes[i]:
      s += ' & $%d$' % count
      t += ' & $%.2f$' % (float(count) / num_schematics)
    s += r' \\'
    print s
    t += r' \\'
    print t

  # success trend
  pylab.figure()
  all_success_mappings = []
  for results in all_results:
    success_mapping = defaultdict(list)
    for result in results:
      success_mapping[result.num_schematic_pins].append(result.solved)
    all_success_mappings.append(success_mapping)
  for i, success_mapping in enumerate(all_success_mappings):
    pylab.errorbar(success_mapping.keys(), map(mean, success_mapping.values()),
        yerr=map(se, success_mapping.values()), color=colors[i])
  pylab.xlabel('Number of pins')
  pylab.ylabel('Success rate')
  pylab.legend(methods, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
        ncol=len(methods), mode='expand', borderaxespad=0.)

  # time trend
  pylab.figure()
  all_time_mappings = []
  for results in all_results:
    time_mapping = defaultdict(list)
    for result in results:
      if result.solved:
        time_mapping[result.num_schematic_pins].append(result.wiring_time)
    all_time_mappings.append(time_mapping)
  for i, time_mapping in enumerate(all_time_mappings):
    pylab.errorbar(time_mapping.keys(), map(mean, time_mapping.values()),
        yerr=map(se, time_mapping.values()), color=colors[i])
  pylab.xlabel('Number of pins')
  pylab.ylabel('Wiring time (seconds)')
  pylab.legend(methods, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
        ncol=len(methods), mode='expand', borderaxespad=0.)

  # quality
  pylab.figure()
  all_quality_mappings = []
  for results in all_results:
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
    all_quality_mappings.append([num_wires_mapping, num_wire_crosses_mapping,
        total_wire_length_mapping])
  ax1 = pylab.subplot(311)
  ax2 = pylab.subplot(312)
  ax3 = pylab.subplot(313)
  for i, (m1, m2, m3) in enumerate(all_quality_mappings):
    ax1.errorbar(m1.keys(), map(mean, m1.values()), yerr=map(se, m1.values()),
        color=colors[i])
    ax1.set_ylabel('Wires')
    ax2.errorbar(m2.keys(), map(mean, m2.values()), yerr=map(se, m2.values()),
        color=colors[i])
    ax2.set_ylabel('Wire crosses')
    ax3.errorbar(m3.keys(), map(mean, m3.values()), yerr=map(se, m3.values()),
        color=colors[i])
    ax3.set_ylabel('Total wire length')
  pylab.xlabel('Number of pins')
  ax1.legend(methods, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
        ncol=len(methods), mode='expand', borderaxespad=0.)

  pylab.show()

if __name__ == '__main__':
  compare(argv[1:len(argv)/2+1], argv[len(argv)/2+1:])
