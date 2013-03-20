"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from visualization.constants import CONNECTOR_SIZE
from visualization.constants import CONNECTOR_SPACING
from visualization.constants import VERTICAL_SEPARATION

# TODO: move somewhere else
def overlap(interval_1, interval_2):
  min_1, max_1 = interval_1
  min_2, max_2 = interval_2
  return max(0, 1 + min(max_1, max_2) - max(min_1, min_2))

class Circuit_Piece:
  """
  TODO(mikemeko)
  """
  def __init__(self, nodes, width, height):
    self.nodes = nodes
    self.width = width
    self.height = height
    self.top_left_loc = None
  def all_locs(self):
    # TODO
    pass
  def locs_for(self, node):
    # TODO
    pass
  def inverted(self):
    # TODO
    pass
  def draw_on(self, canvas, top_left):
    # TODO: override
    x, y = top_left
    rect_width = CONNECTOR_SIZE * self.width + CONNECTOR_SPACING * (
        self.width- 1)
    rect_height = VERTICAL_SEPARATION + 2 * CONNECTOR_SIZE
    canvas.create_rectangle(x, y, x + rect_width, y + rect_height, fill='#BBB')
  def crossed_by(self, wire):
    # TODO
    # TODO: define a between function
    # TODO: assign different colors for different nodes
    assert self.top_left_loc
    r_min, c_min = self.top_left_loc
    r_max, c_max = r_min + self.height - 1, c_min + self.width - 1
    wire_r_min = min(wire.r_1, wire.r_2)
    wire_r_max = max(wire.r_1, wire.r_2)
    wire_c_min = min(wire.c_1, wire.c_2)
    wire_c_max = max(wire.c_1, wire.c_2)
    return (overlap((r_min, r_max), (wire_r_min, wire_r_max)) and
        overlap((c_min, c_max), (wire_c_min, wire_c_max)))

class Op_Amp_Piece(Circuit_Piece):
  # TODO: picture
  """
  TODO(mikemeko)
  """
  def __init__(self, n_1, n_2, n_3, n_4, n_5, n_6, n_7, n_8, dot_bottom_left):
    Circuit_Piece.__init__(self, set(filter(bool, [n_1, n_2, n_3, n_4, n_5,
        n_6, n_7, n_8])), 4, 2)
    self.n_1 = n_1
    self.n_2 = n_2
    self.n_3 = n_3
    self.n_4 = n_4
    self.n_5 = n_5
    self.n_6 = n_6
    self.n_7 = n_7
    self.n_8 = n_8
    self.dot_bottom_left = dot_bottom_left
  def all_locs(self):
    assert self.top_left_loc
    r, c = self.top_left_loc
    return set([(r, c), (r, c + 1), (r, c + 2), (r, c + 3), (r + 1, c),
        (r + 1, c + 1), (r + 1, c + 2), (r + 1, c + 3)])
  def locs_for(self, node):
    assert self.top_left_loc
    r, c = self.top_left_loc
    locs = []
    if node == self.n_1:
      locs.append((r + 1, c) if self.dot_bottom_left else (r, c + 3))
    if node == self.n_2:
      locs.append((r + 1, c + 1) if self.dot_bottom_left else (r, c + 2))
    if node == self.n_3:
      locs.append((r + 1, c + 2) if self.dot_bottom_left else (r, c + 1))
    if node == self.n_4:
      locs.append((r + 1, c + 3) if self.dot_bottom_left else (r, c))
    if node == self.n_5:
      locs.append((r, c + 3) if self.dot_bottom_left else (r + 1, c))
    if node == self.n_6:
      locs.append((r, c + 2) if self.dot_bottom_left else (r + 1, c + 1))
    if node == self.n_7:
      locs.append((r, c + 1) if self.dot_bottom_left else (r + 1, c + 2))
    if node == self.n_8:
      locs.append((r, c) if self.dot_bottom_left else (r + 1, c + 3))
    return locs
  def inverted(self):
    return Op_Amp_Piece(self.n_1, self.n_2, self.n_3, self.n_4, self.n_5,
        self.n_6, self.n_7, self.n_8, not self.dot_bottom_left)
  def __str__(self):
    return '%s %s %s %s %s %s %s %s %s %s' % (self.n_1, self.n_2, self.n_3,
        self.n_4, self.n_5, self.n_6, self.n_7, self.n_8, self.top_left_loc,
        self.dot_bottom_left)

class Resistor_Piece(Circuit_Piece):
  """
  TODO(mikemeko)
  """
  def __init__(self, n_1, n_2):
    assert n_1
    assert n_2
    Circuit_Piece.__init__(self, set([n_1, n_2]), 1, 2)
    self.n_1 = n_1
    self.n_2 = n_2
  def all_locs(self):
    assert self.top_left_loc
    r, c = self.top_left_loc
    return set([(r, c), (r + 1, c)])
  def locs_for(self, node):
    assert self.top_left_loc
    r, c = self.top_left_loc
    locs = []
    if node == self.n_1:
      locs.append((r, c))
    if node == self.n_2:
      locs.append((r + 1, c))
    return locs
  def inverted(self):
    return Resistor_Piece(self.n_2, self.n_1)
  def __str__(self):
    return '%s %s %s' % (self.n_1, self.n_2, self.top_left_loc)
