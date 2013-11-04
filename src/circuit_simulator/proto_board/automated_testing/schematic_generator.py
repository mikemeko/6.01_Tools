"""
Script to generate a large number of test schematics.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from math import factorial
from os import mkdir
from os import walk
from os.path import join
from random import sample
from random import seed
from shutil import move

MAX_NUM_CONNECTIONS = {1:0, 2:6, 3:8, 4:10, 5:14, 6:16}

# the idea is that we divide the board into 6 parts (2 rows, 3 cols) and put a
#     various combinations of sub-circuits in the 6 slots, we consider various
#     ways of interconnecting the sub-circuits
# connection points for slot 00 (row 0, column 0)
bases00 = {}
bases00['T_resistors_00.circsim'] = [(40, 80), (200, 80), (120, 160)]
bases00['divider_follower_00.circsim'] = [(90, 70), (220, 160), (90, 230)]
bases00['pot_follower_00.circsim'] = [(90, 70), (90, 150), (200, 120)]
bases00['motor_00.circsim'] = [(110, 50), (110, 150)]
# connection points for slot 01 (row 0, column 1)
bases01 = {}
bases01['T_resistors_01.circsim'] = [(310, 80), (470, 80), (390, 160)]
bases01['divider_follower_01.circsim'] = [(350, 70), (480, 160), (350, 230)]
bases01['pot_follower_01.circsim'] = [(350, 70), (350, 150), (460, 120)]
bases01['motor_01.circsim'] = [(390, 50), (390, 150)]
# connection points for slot 02 (row 0, column 2)
bases02 = {}
bases02['T_resistors_02.circsim'] = [(580, 80), (740, 80), (660, 160)]
bases02['divider_follower_02.circsim'] = [(600, 70), (730, 160), (600, 230)]
# connection points for slot 10 (row 1, column 0)
bases10 = {}
bases10['T_resistors_10.circsim'] = [(50, 360), (210, 360), (130, 440)]
bases10['divider_follower_10.circsim'] = [(70, 280), (200, 370), (70, 440)]
# connection points for slot 11 (row 1, column 1)
bases11 = {}
bases11['T_resistors_11.circsim'] = [(310, 360), (470, 360), (390, 440)]
bases11['divider_follower_11.circsim'] = [(340, 280), (470, 370), (340, 440)]
bases11['head_11.circsim'] = [(290, 350), (290, 450), (380, 350), (430, 400),
    (380, 450), (480, 350), (530, 400), (480, 450)]
# connection points for slot 12 (row 1, column 2)
bases12 = {}
bases12['T_resistors_12.circsim'] = [(590, 360), (750, 360), (670, 440)]
bases12['divider_follower_12.circsim'] = [(620, 280), (750, 370), (620, 440)]
bases12['robot_12.circsim'] = [(620, 340), (670, 340), (570, 420), (620, 420),
    (670, 420), (730, 370), (730, 470)]

def to_multiple_dirs(num_files_per_dir):
  """
  Puts the test files in several directories containing at most
      |num_files_per_dir| test files.
  """
  output_dir = 'auto_generated_dataset'
  for dir_path, dir_names, file_names in walk(output_dir):
    for i, file_name in enumerate(file_names):
      if i % num_files_per_dir == 0:
        current_dir = join(output_dir, 'part%d' % (i / num_files_per_dir))
        mkdir(current_dir)
      move(join(output_dir, file_name), current_dir)

def generate():
  """
  Generates and saves a large number of test schematics.
  """
  seed(1000)
  bases_dir = 'auto_generation_bases'
  output_dir = 'auto_generated_dataset'
  def _generate_for(b00, b01, b02, b10, b11, b12, combo):
    """
    Generates schematics using the 6 given sub-circuits in the 6 slots. |combo|
        describes the combination of sub-circuits.
    """
    # jot down the subcircuits themselves
    common_lines = []
    for b in filter(bool, [b00, b01, b02, b10, b11, b12]):
      common_lines.extend([l.strip() for l in open(join(bases_dir,
          b)).readlines() if not l.startswith('Probe')])
    common_lines.sort(key=lambda line: line.startswith('Wire ('))
    # now consider various ways of interconnecting the sub-circuits
    base_dict_pairs = [(b00, bases00), (b01, bases01), (b02, bases02), (b10,
        bases10), (b11, bases11), (b12, bases12)]
    connections = []
    for i, (base, base_dict) in enumerate(base_dict_pairs):
      if base is not None:
        for base_point in base_dict[base]:
          # a point on a sub-circuit can be connected to any point on any OTHER
          #     sub-circuit
          for other_base, other_base_dict in base_dict_pairs[i + 1:]:
            if other_base is not None:
              for other_base_point in other_base_dict[other_base]:
                connections.append((base_point, other_base_point))
    for num_connections in xrange(min(MAX_NUM_CONNECTIONS[len(combo)],
        len(connections)) + 1):
      wire_lines = ['Wire %s %s' % pair for pair in sample(connections,
          num_connections)]
      open(join(output_dir, '%s%d.circsim' % (combo, num_connections)),
          'w').write('\n'.join(common_lines + wire_lines))
  # avoid repeating sub-circuit combinations
  combos = set()
  for b00 in bases00:
    for b01 in bases01:
      for b02 in bases02:
        for b10 in bases10:
          for b11 in bases11:
            for b12 in bases12:
              for j in xrange(1, 2 ** 6):
                bin_j = '{0:06b}'.format(j)
                _b00 = b00 if bin_j[0] == '1' else None
                _b01 = b01 if bin_j[1] == '1' else None
                _b02 = b02 if bin_j[2] == '1' else None
                _b10 = b10 if bin_j[3] == '1' else None
                _b11 = b11 if bin_j[4] == '1' else None
                _b12 = b12 if bin_j[5] == '1' else None
                combo = ''.join(sorted([b[0] for b in filter(bool, [_b00, _b01,
                    _b02, _b10, _b11, _b12])]))
                if combo not in combos:
                  combos.add(combo)
                  _generate_for(_b00, _b01, _b02, _b10, _b11, _b12, combo)

def nCr(n, r):
  """
  Returns n choose r.
  """
  if 0 <= r <= n:
    return factorial(n) / factorial(r) / factorial(n - r)
  return 0

def num_possible_schematics():
  """
  Returns the number of schematics that could possibly be generated by our
      scheme.
  """
  num_possible = 0
  num_samples = 0
  combos = set()
  for b00 in bases00:
    for b01 in bases01:
      for b02 in bases02:
        for b10 in bases10:
          for b11 in bases11:
            for b12 in bases12:
              for j in xrange(1, 2 ** 6):
                bin_j = '{0:06b}'.format(j)
                _b00 = b00 if bin_j[0] == '1' else None
                _b01 = b01 if bin_j[1] == '1' else None
                _b02 = b02 if bin_j[2] == '1' else None
                _b10 = b10 if bin_j[3] == '1' else None
                _b11 = b11 if bin_j[4] == '1' else None
                _b12 = b12 if bin_j[5] == '1' else None
                combo = ''.join(sorted([b[0] for b in filter(bool, [_b00, _b01,
                    _b02, _b10, _b11, _b12])]))
                if combo not in combos:
                  combos.add(combo)
                  num_connection_points = [len(base_dict[base]) for (base,
                      base_dict) in [(_b00, bases00), (_b01, bases01), (_b02,
                      bases02), (_b10, bases10), (_b11, bases11), (_b12,
                      bases12)] if base is not None]
                  # for convenience in the following line
                  num_connection_points.append(0)
                  num_possible_connections = sum(l * sum(
                      num_connection_points[i + 1:]) for i, l in enumerate(
                      num_connection_points[:-1]))
                  max_num_connections = min(MAX_NUM_CONNECTIONS[len(combo)],
                      num_possible_connections)
                  num_samples += max_num_connections + 1
                  for num_connections in xrange(max_num_connections + 1):
                    num_possible += nCr(num_possible_connections,
                        num_connections)
  return num_possible, num_samples

if __name__ == '__main__':
  num_possible, num_samples = num_possible_schematics()
  generate()
  to_multiple_dirs(num_samples / 8 + 1)
  print 'Generated %d schematics out of a possible %d' % (num_samples,
      num_possible)
