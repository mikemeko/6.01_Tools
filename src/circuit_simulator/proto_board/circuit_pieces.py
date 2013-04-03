"""
Representations for objects that can be placed on the proto board: op amps,
    resistors, pots ... TODO(mikemeko).
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import OP_AMP_BODY_COLOR
from constants import OP_AMP_DOT_COLOR
from constants import OP_AMP_DOT_OFFSET
from constants import OP_AMP_DOT_RADIUS
from constants import POT_CIRCLE_FILL
from constants import POT_CIRCLE_RADIUS
from constants import POT_FILL
from constants import POT_OUTLINE
from constants import RESISTOR_INNER_COLOR
from constants import RESISTOR_OUTER_COLOR
from core.gui.util import create_circle
from util import rects_overlap
from visualization.constants import CONNECTOR_SIZE
from visualization.constants import CONNECTOR_SPACING
from visualization.constants import VERTICAL_SEPARATION
from wire import Wire

class Circuit_Piece:
  """
  Abstract class to represent all objects that can be placed on the proto
      board. All subclasses should implement all_locs, locs_for, inverted,
      and draw_on.
  """
  # top left location row, subclasses can changes this as needed
  row = 6
  def __init__(self, nodes, width, height):
    """
    |nodes|: a set of the nodes this piece is connected to.
    |width|: the width of this piece (in number of columns).
    |height|: the height of this piece (in number of rows).
    """
    self.nodes = nodes
    self.width = width
    self.height = height
    # the (r, c) location of the top left corner of this piece
    # this is set (and possibly reset) during the piece placement process, see
    #     circuit_piece_placement.py
    self.top_left_loc = None
  def locs_for(self, node):
    """
    Should return a list of all the locations of this piece associated with the
        given |node|. All subclasses should implement this.
    """
    raise NotImplementedError('subclasses should implement this')
  def inverted(self):
    """
    Should return a new Circuit_Piece representing this piece inverted
        up-side-down. All subclasses should implement this.
    """
    raise NotImplementedError('subclasses should implement this')
  def draw_on(self, canvas, top_left):
    """
    Should draw this piece on the given |canvas|, assuming the given coordinate
        |top_left| to be the place to locate its top left corner. All
        subclasses should implement this.
    """
    raise NotImplementedError('subclasses should implement this')
  def _assert_top_left_loc_set(self):
    """
    Ensures that top_left_loc is set, or throws an Exeption.
    """
    assert self.top_left_loc, 'top left location has not been set'
  def all_locs(self):
    """
    Return a set of all the locations on the proto board occupied by this
        piece.
    """
    self._assert_top_left_loc_set()
    r, c = self.top_left_loc
    return set((r + i, c + j) for i in xrange(self.height) for j in xrange(
        self.width))
  def bbox(self):
    """
    Returns the bounding box of this piece in the form (r_min, c_min, r_max,
        c_max).
    """
    self._assert_top_left_loc_set()
    r_min, c_min = self.top_left_loc
    r_max, c_max = r_min + self.height - 1, c_min + self.width - 1
    return r_min, c_min, r_max, c_max
  def crossed_by(self, wire):
    """
    Returns True if the given |wire| crosses this piece, False otherwise.
    """
    assert isinstance(wire, Wire), 'wire must be a Wire'
    r_min, c_min, r_max, c_max = self.bbox()
    wire_r_min = min(wire.r_1, wire.r_2)
    wire_r_max = max(wire.r_1, wire.r_2)
    wire_c_min = min(wire.c_1, wire.c_2)
    wire_c_max = max(wire.c_1, wire.c_2)
    return rects_overlap(self.bbox(), (wire_r_min, wire_c_min, wire_r_max,
        wire_c_max))
  def overlaps_with(self, other):
    """
    Returns True if the given |other| piece overlaps with this piece, False
        otherwise.
    """
    assert isinstance(other, Circuit_Piece), 'other must be a Circuit_Piece'
    return rects_overlap(self.bbox(), other.bbox())

class Op_Amp_Piece(Circuit_Piece):
  """
  Representation for the op amp piece.
  See: http://mit.edu/6.01/www/circuits/opAmpCkt.jpg
  """
  def __init__(self, n_1, n_2, n_3, n_4, n_5, n_6, n_7, n_8,
      dot_bottom_left=True):
    """
    |n_1|, ..., |n_8|: the nodes for this op amp piece, see image linked above.
    |dot_bottom_left|: boolean indicating whether the dot is bottom left or
        top right (indicates orientation of piece).
    """
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
  def locs_for(self, node):
    self._assert_top_left_loc_set()
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
  def draw_on(self, canvas, top_left):
    x, y = top_left
    # pins
    for r in xrange(2):
      for c in xrange(4):
        pin_x = x + c * (CONNECTOR_SIZE + CONNECTOR_SPACING)
        pin_y = y + r * (CONNECTOR_SIZE + VERTICAL_SEPARATION)
        canvas.create_rectangle(pin_x, pin_y, pin_x + CONNECTOR_SIZE,
            pin_y + CONNECTOR_SIZE, fill='black')
    # body
    width = 4 * CONNECTOR_SIZE + 3 * CONNECTOR_SPACING
    height = 2 * CONNECTOR_SIZE + VERTICAL_SEPARATION
    h_offset = 2
    v_offset = 2 * CONNECTOR_SIZE / 3
    canvas.create_rectangle(x - h_offset, y + v_offset, x + width + h_offset,
        y + height - v_offset, fill=OP_AMP_BODY_COLOR)
    # dot
    dot_dx = (OP_AMP_DOT_OFFSET - h_offset) if self.dot_bottom_left else (
        width - OP_AMP_DOT_OFFSET + h_offset)
    dot_dy = ((height - OP_AMP_DOT_OFFSET - CONNECTOR_SIZE / 2) if
        self.dot_bottom_left else (OP_AMP_DOT_OFFSET + CONNECTOR_SIZE / 2))
    create_circle(canvas, x + dot_dx, y + dot_dy, OP_AMP_DOT_RADIUS,
        fill=OP_AMP_DOT_COLOR)
  def __str__(self):
    return 'Op_Amp_Piece %s %s' % (str([self.n_1, self.n_2, self.n_3, self.n_4,
        self.n_5, self.n_6, self.n_7, self.n_8]), self.dot_bottom_left)

class Resistor_Piece(Circuit_Piece):
  """
  Representation for the resistor piece.
  """
  def __init__(self, n_1, n_2):
    """
    |n_1|, |n_2|: the two nodes of the resistor.
    """
    assert n_1, 'invalid n_1'
    assert n_2, 'invalid n_2'
    Circuit_Piece.__init__(self, set([n_1, n_2]), 1, 2)
    self.n_1 = n_1
    self.n_2 = n_2
  def locs_for(self, node):
    self._assert_top_left_loc_set()
    r, c = self.top_left_loc
    locs = []
    if node == self.n_1:
      locs.append((r, c))
    if node == self.n_2:
      locs.append((r + 1, c))
    return locs
  def inverted(self):
    return Resistor_Piece(self.n_2, self.n_1)
  def draw_on(self, canvas, top_left):
    x, y = top_left
    # inner rectangle, i.e. the thin one that is partially covered
    canvas.create_rectangle(x, y, x + CONNECTOR_SIZE,
        y + VERTICAL_SEPARATION + 2 * CONNECTOR_SIZE,
        fill=RESISTOR_INNER_COLOR)
    # outer rectangle, i.e. the fat, short one on top
    dx = (CONNECTOR_SPACING - CONNECTOR_SIZE) / 2
    canvas.create_rectangle(x - dx, y + CONNECTOR_SIZE,
        x + CONNECTOR_SIZE + dx, y + VERTICAL_SEPARATION + CONNECTOR_SIZE,
        fill=RESISTOR_OUTER_COLOR)
  def __str__(self):
    return 'Resistor_Piece %s' % str([self.n_1, self.n_2])

class Pot_Piece(Circuit_Piece):
  """
  Representation for the pot piece.
  """
  # top left location row
  row = 8
  def __init__(self, n_top, n_middle, n_bottom, directed_up=True):
    """
    |n_top|, |n_middle|, |n_bottom|: the terminal nodes for this pot.
    |directed_up|: True if this pot is placed with the middle terminal facing
        up, False otherwise (facing down).
    """
    assert n_top, 'invalid n_top'
    assert n_middle, 'invalid n_middle'
    assert n_bottom, 'invalid n_bottom'
    Circuit_Piece.__init__(self, set([n_top, n_middle, n_bottom]), 3, 3)
    self.n_top = n_top
    self.n_middle = n_middle
    self.n_bottom = n_bottom
    self.directed_up = directed_up
  def locs_for(self, node):
    self._assert_top_left_loc_set()
    r, c = self.top_left_loc
    locs = []
    if node == self.n_top:
      locs.append((r + 2, c) if self.directed_up else (r, c + 2))
    if node == self.n_middle:
      locs.append((r, c + 1) if self.directed_up else (r + 2, c + 1))
    if node == self.n_bottom:
      locs.append((r + 2, c + 2) if self.directed_up else (r, c))
    return locs
  def inverted(self):
    return Pot_Piece(self.n_top, self.n_middle, self.n_bottom,
        not self.directed_up)
  def draw_on(self, canvas, top_left):
    x, y = top_left
    size = 3 * CONNECTOR_SIZE + 2 * CONNECTOR_SPACING
    offset = 2
    canvas.create_rectangle(x - offset, y - offset, x + size + offset,
        y + size + offset, fill=POT_FILL, outline=POT_OUTLINE)
    create_circle(canvas, x + size / 2, y + size / 2, POT_CIRCLE_RADIUS,
        fill=POT_CIRCLE_FILL)
    for (r, c) in ([(0, 1), (2, 0), (2, 2)] if self.directed_up else [(0, 0),
        (0, 2), (2, 1)]):
      pin_x = x + c * (CONNECTOR_SIZE + CONNECTOR_SPACING)
      pin_y = y + r * (CONNECTOR_SIZE + CONNECTOR_SPACING)
      canvas.create_rectangle(pin_x, pin_y, pin_x + CONNECTOR_SIZE,
          pin_y + CONNECTOR_SIZE, fill='#777', outline='black')
  def __str__(self):
    return 'Pot_Piece %s %s' % (str([self.n_top, self.n_middle,
        self.n_bottom]), self.directed_up)
