"""
Script to generate comparison plots.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from analyze_data import Test_Group
from analyze_data import Test_Result
from collections import defaultdict
from numpy import mean
from sys import argv
import pylab

colors = ['r', 'g', 'b', 'c', 'm']

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
  pylab.legend(methods, loc=2)

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
    pylab.plot(success_mapping.keys(), map(mean, success_mapping.values()),
        color=colors[i])
  pylab.xlabel('Number of pins')
  pylab.ylabel('Success rate')
  pylab.legend(methods, loc=2)

  # time trend
  pylab.figure()
  all_time_mappings = []
  for results in all_results:
    time_mapping = defaultdict(list)
    for result in results:
      time_mapping[result.num_schematic_pins].append(result.wiring_time)
    all_time_mappings.append(time_mapping)
  for i, time_mapping in enumerate(all_time_mappings):
    pylab.plot(time_mapping.keys(), map(mean, time_mapping.values()),
        color=colors[i])
  pylab.xlabel('Number of pins')
  pylab.ylabel('Wiring time (seconds)')
  pylab.legend(methods, loc=2)

  pylab.show()

if __name__ == '__main__':
  compare(argv[1:len(argv)/2+1], argv[len(argv)/2+1:])
