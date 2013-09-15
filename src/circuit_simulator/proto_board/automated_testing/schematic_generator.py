"""
Script to generate a large number of test schematics.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from os.path import join
from random import choice

def generate():
  """
  Generates and saves a large number of test schematics.
  """
  bases_dir = 'auto_generation_bases'
  output_dir = 'auto_generated_dataset'

  bases00 = {}
  bases00['T_resistors_00.circsim'] = [(40, 80), (200, 80), (120, 160)]
  bases00['divider_follower_00.circsim'] = [(90, 70), (220, 160), (90, 230)]
  bases00['pot_follower_00.circsim'] = [(90, 70), (90, 150), (200, 120)]
  bases00['motor_00.circsim'] = [(110, 70), (110, 130)]

  bases01 = {}
  bases01['T_resistors_01.circsim'] = [(310, 80), (470, 80), (390, 160)]
  bases01['divider_follower_01.circsim'] = [(350, 70), (480, 160), (350, 230)]
  bases01['pot_follower_01.circsim'] = [(350, 70), (350, 150), (460, 120)]
  bases01['motor_01.circsim'] = [(390, 70), (390, 130)]

  bases02 = {}
  bases02['T_resistors_02.circsim'] = [(580, 80), (740, 80), (660, 160)]
  bases02['divider_follower_02.circsim'] = [(600, 70), (730, 160), (600, 230)]
  bases02['pot_follower_02.circsim'] = [(590, 70), (590, 150), (700, 120)]
  bases02['motor_02.circsim'] = [(680, 70), (680, 130)]

  bases10 = {}
  bases10['T_resistors_10.circsim'] = [(50, 360), (210, 360), (130, 440)]
  bases10['divider_follower_10.circsim'] = [(70, 280), (200, 370), (70, 440)]
  bases10['pot_follower_10.circsim'] = [(70, 330), (70, 410), (180, 380)]
  bases10['motor_10.circsim'] = [(110, 350), (110, 410)]

  bases11 = {}
  bases11['T_resistors_11.circsim'] = [(310, 360), (470, 360), (390, 440)]
  bases11['divider_follower_11.circsim'] = [(340, 280), (470, 370), (340, 440)]
  bases11['pot_follower_11.circsim'] = [(360, 330), (360, 410), (470, 380)]
  bases11['motor_11.circsim'] = [(410, 350), (410, 410)]
  bases11['head_11.circsim'] = [(330, 370), (330, 430), (400, 370), (430, 400),
      (400, 430), (470, 370), (500, 400), (470, 430)]

  bases12 = {}
  bases12['T_resistors_12.circsim'] = [(590, 360), (750, 360), (670, 440)]
  bases12['divider_follower_12.circsim'] = [(620, 280), (750, 370), (620, 440)]
  bases12['pot_follower_12.circsim'] = [(600, 330), (600, 410), (710, 380)]
  bases12['motor_12.circsim'] = [(670, 350), (670, 410)]
  bases12['robot_12.circsim'] = [(570, 410), (620, 410), (670, 410), (620, 360),
      (670, 360), (730, 400), (730, 460)]

  def _generate_for(b00, b01, b02, b10, b11, b12, n):
    base_dict_pairs = [(b00, bases00), (b01, bases01), (b02, bases02), (b10,
        bases10), (b11, bases11), (b12, bases12)]
    connections = {}
    for (base, base_dict) in base_dict_pairs:
      for base_point in base_dict[base]:
        connections[base_point] = reduce(list.__add__, [b_d[b] for b, b_d in
            base_dict_pairs if b != base])
    common_lines = []
    for b in (b00, b01, b02, b10, b11, b12):
      common_lines.extend([l.strip() for l in open(join(bases_dir,
          b)).readlines() if not l.startswith('Probe')])
    common_lines.sort(key=lambda line: line.startswith('Wire ('))
    wire_combos = set()
    for k in xrange(10):
      wire_lines = []
      seen_wires = set()
      used_points = set()
      for base_point in connections:
        if base_point in used_points:
          continue
        choices = [point for point in connections[base_point] if point not in
            used_points]
        if not choices:
          continue
        other_point = choice(choices)
        wire_lines.append('Wire %s %s' % (base_point, other_point))
        seen_wires.add(frozenset([base_point, other_point]))
        used_points.add(base_point)
        used_points.add(other_point)
      seen_wires = frozenset(seen_wires)
      if seen_wires not in wire_combos:
        wire_combos.add(seen_wires)
        open(join(output_dir, 'test%d.circsim' % n), 'w').write('\n'.join(
            common_lines + wire_lines))
        n += 1
    return n

  n = 0
  combos = set()
  for b00 in bases00:
    for b01 in bases01:
      for b02 in bases02:
        for b10 in bases10:
          for b11 in bases11:
            for b12 in bases12:
              bases = (b00, b01, b02, b10, b11, b12)
              combo = ' '.join(sorted([b[:-11] for b in bases]))
              if combo not in combos:
                combos.add(combo)
                n = _generate_for(b00, b01, b02, b10, b11, b12, n)

if __name__ == '__main__':
  generate()
