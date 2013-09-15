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

  bases01 = {}
  bases01['T_resistors_01.circsim'] = [(310, 80), (470, 80), (390, 160)]
  bases01['divider_follower_01.circsim'] = [(350, 70), (480, 160), (350, 230)]

  bases02 = {}
  bases02['T_resistors_02.circsim'] = [(580, 80), (740, 80), (660, 160)]
  bases02['divider_follower_02.circsim'] = [(600, 70), (730, 160), (600, 230)]

  bases10 = {}
  bases10['T_resistors_10.circsim'] = [(50, 360), (210, 360), (130, 440)]
  bases10['divider_follower_10.circsim'] = [(70, 280), (200, 370), (70, 440)]

  bases11 = {}
  bases11['T_resistors_11.circsim'] = [(310, 360), (470, 360), (390, 440)]
  bases11['divider_follower_11.circsim'] = [(340, 280), (470, 370), (340, 440)]

  bases12 = {}
  bases12['T_resistors_12.circsim'] = [(590, 360), (750, 360), (670, 440)]
  bases12['divider_follower_12.circsim'] = [(620, 280), (750, 370), (620, 440)]

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
      else:
        print 'haha'
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
