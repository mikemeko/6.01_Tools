"""
Script to generate a large number of test schematics.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from os.path import join
from random import sample

def generate():
  """
  Generates and saves a large number of test schematics.
  """
  bases_dir = 'auto_generation_bases'
  output_dir = 'auto_generated_dataset'
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
  bases02['pot_follower_02.circsim'] = [(590, 70), (590, 150), (700, 120)]
  bases02['motor_02.circsim'] = [(680, 50), (680, 150)]
  # connection points for slot 10 (row 1, column 0)
  bases10 = {}
  bases10['T_resistors_10.circsim'] = [(50, 360), (210, 360), (130, 440)]
  bases10['divider_follower_10.circsim'] = [(70, 280), (200, 370), (70, 440)]
  bases10['pot_follower_10.circsim'] = [(70, 330), (70, 410), (180, 380)]
  bases10['motor_10.circsim'] = [(110, 330), (110, 430)]
  # connection points for slot 11 (row 1, column 1)
  bases11 = {}
  bases11['T_resistors_11.circsim'] = [(310, 360), (470, 360), (390, 440)]
  bases11['divider_follower_11.circsim'] = [(340, 280), (470, 370), (340, 440)]
  bases11['pot_follower_11.circsim'] = [(360, 330), (360, 410), (470, 380)]
  bases11['motor_11.circsim'] = [(410, 330), (410, 430)]
  bases11['head_11.circsim'] = [(290, 350), (290, 450), (380, 350), (430, 400),
      (380, 450), (480, 350), (530, 400), (480, 450)]
  # connection points for slot 12 (row 1, column 2)
  bases12 = {}
  bases12['T_resistors_12.circsim'] = [(590, 360), (750, 360), (670, 440)]
  bases12['divider_follower_12.circsim'] = [(620, 280), (750, 370), (620, 440)]
  bases12['pot_follower_12.circsim'] = [(600, 330), (600, 410), (710, 380)]
  bases12['motor_12.circsim'] = [(670, 330), (670, 430)]
  bases12['robot_12.circsim'] = [(620, 340), (670, 340), (570, 420), (620, 420),
      (670, 420), (730, 370), (730, 470)]
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
    for num_connections in xrange(min(10, len(connections) + 1)):
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

if __name__ == '__main__':
  generate()
