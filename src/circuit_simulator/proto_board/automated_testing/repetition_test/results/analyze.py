"""
Script to analyze repetition test results.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

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
    return 0

def get_float(val):
  try:
    return float(val)
  except:
    return 0

def get_int_list(val):
  try:
    return map(int, [e.strip() for e in val[1:-1].split(',')])
  except:
    return None

class Test_Result:
  def __init__(self, line):
    line = line.split(';')
    g = sequence_generator()
    self.run = get_int(line[g.next()])
    self.solved = line[g.next()] == 'True'
    self.placement_time = get_float(line[g.next()])
    self.wiring_time = get_float(line[g.next()])
    self.total_time = self.placement_time + self.wiring_time
    self.num_expanded = get_int_list(line[g.next()])
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

def analyze():
  easy_results = [Test_Result(line) for line in open(
      'easy_results').readlines()]
  medium_results = [Test_Result(line) for line in open(
      'medium_results').readlines()]
  hard_results = [Test_Result(line) for line in open(
      'hard_results').readlines()]
  strange_results = [Test_Result(line) for line in open(
      'strange_results').readlines()]
  all_solved = []
  all_failed = []
  for i, results in enumerate((easy_results, medium_results, hard_results,
      strange_results)):
    solved = []
    failed = []
    for result in results:
      (solved if result.solved else failed).append(result.wiring_time)
    all_solved.append(solved)
    all_failed.append(failed)
  pylab.figure()
  for i, sp in enumerate((411, 412, 413, 414)):
    pylab.subplot(sp)
    pylab.hist(all_solved[i], color='g', alpha=0.5)
    pylab.hist(all_failed[i], color='r', alpha=0.5)
  pylab.show()

if __name__ == '__main__':
  analyze()
