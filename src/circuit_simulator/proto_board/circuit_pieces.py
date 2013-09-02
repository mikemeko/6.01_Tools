"""
Representations for objects that can be placed on the proto board: op amps,
    resistors, pots, motor connectors, head connectors, and robot connectors.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import DISABLED_PINS_HEAD_CONNECTOR
from constants import DISABLED_PINS_MOTOR_CONNECTOR
from constants import DISABLED_PINS_ROBOT_CONNECTOR
from constants import N_PIN_CONNECTOR_FILL
from constants import N_PIN_CONNECTOR_OUTLINE
from constants import OP_AMP_BODY_COLOR
from constants import OP_AMP_DOT_COLOR
from constants import OP_AMP_DOT_OFFSET
from constants import OP_AMP_DOT_RADIUS
from constants import POT_CIRCLE_FILL
from constants import POT_CIRCLE_RADIUS
from constants import POT_FILL
from constants import POT_OUTLINE
from constants import PROTO_BOARD_HEIGHT
from constants import RESISTOR_COLORS
from constants import RESISTOR_INNER_COLOR
from constants import RESISTOR_OUTER_COLOR
from core.gui.util import create_circle
from core.util.util import rects_overlap
from Tkinter import CENTER
from util import loc_to_cmax_rep
from util import section_locs
from visualization.constants import CONNECTOR_SIZE
from visualization.constants import CONNECTOR_SPACING
from visualization.constants import VERTICAL_SEPARATION
from wire import Wire

class Circuit_Piece:
  """
  Abstract class to represent all objects that can be placed on the proto
      board. All subclasses should implement locs_for, inverted, and draw_on.
  """
  # top left location row possibilities, subclasses can changes this as needed
  # default puts piece in the middle strip of the proto board
  possible_top_left_rows = [PROTO_BOARD_HEIGHT / 2 - 1]
  def __init__(self, nodes, width, height, label=None):
    """
    |nodes|: a set of the nodes this piece is connected to.
    |width|: the width of this piece (in number of columns).
    |height|: the height of this piece (in number of rows).
    |label|: a label for this Circuit_Piece to show as a tooltip.
    """
    self.nodes = nodes
    self.width = width
    self.height = height
    self.label = label
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
  def to_cmax_str(self):
    """
    Should return a string for the CMax representation (when saved in a file) of
        this Circuit_Piece. All subclasses should implement this.
    """
    raise NotImplementedError('subclasses should implement this')
  def _assert_top_left_loc_set(self):
    """
    Ensures that top_left_loc is set, or throws an Exeption.
    """
    assert self.top_left_loc, 'top left location has not been set'
  def node_for(self, loc):
    """
    If |loc| is internally connected to one of the locations on the proto board
        occupied by this piece, returns the node for |loc|. Returns None
        otherwise.
    """
    for node in self.nodes:
      for node_loc in self.locs_for(node):
        if loc in section_locs(node_loc):
          return node
    return None
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
  def get_sacred_locs(self):
    """
    Returns a list of the locations on the proto board in contact with this
        piece that are not connected to any other circuit component, but should
        still be kept disconnected from all other things on the proto board.
    Default is an empty list, but subclasses can override this method as
        necessary.
    """
    return []

class Op_Amp_Piece(Circuit_Piece):
  """
  Representation for the op amp piece.
  See: http://mit.edu/6.01/www/circuits/opAmpCkt.jpg
  """
  def __init__(self, n_1, n_2, n_3, n_4, n_5, n_6, n_7, n_8, label,
      dot_bottom_left=True):
    """
    |n_1|, ..., |n_8|: the nodes for this op amp piece, see image linked above.
    |label|: label for the two op amps contained in this package, separated by
        a comma. Order is important. If there is only one op amp in this
        package, |label| should just be the label of that op amp (no commas).
    |dot_bottom_left|: boolean indicating whether the dot is bottom left or
        top right (indicates orientation of piece).
    """
    Circuit_Piece.__init__(self, set(filter(bool, [n_1, n_2, n_3, n_4, n_5,
        n_6, n_7, n_8])), 4, 2, label)
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
    new_label = (','.join(reversed(self.label.split(','))) if ',' in self.label
        else self.label)
    return Op_Amp_Piece(self.n_1, self.n_2, self.n_3, self.n_4, self.n_5,
        self.n_6, self.n_7, self.n_8, new_label, not self.dot_bottom_left)
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
  def to_cmax_str(self):
    self._assert_top_left_loc_set()
    c, r = loc_to_cmax_rep(self.top_left_loc)
    if self.dot_bottom_left:
      return 'opamp: (%d,%d)--(%d,%d)' % (c, r + 3, c, r)
    else:
      return 'opamp: (%d,%d)--(%d,%d)' % (c + 3, r, c + 3, r + 3)
  def __str__(self):
    return 'Op_Amp_Piece %s %s' % (str([self.n_1, self.n_2, self.n_3, self.n_4,
        self.n_5, self.n_6, self.n_7, self.n_8]), self.dot_bottom_left)
  def __eq__(self, other):
    return (isinstance(other, Op_Amp_Piece) and self.n_1 == other.n_1 and
        self.n_2 == other.n_2 and self.n_3 == other.n_3 and self.n_4 ==
        other.n_4 and self.n_5 == other.n_5 and self.n_6 == other.n_6 and
        self.n_7 == other.n_7 and self.n_8 == other.n_8 and self.label ==
        other.label and self.top_left_loc == other.top_left_loc and
        self.dot_bottom_left == other.dot_bottom_left)
  def __hash__(self):
    return hash((self.n_1, self.n_2, self.n_3, self.n_4, self.n_5, self.n_6,
        self.n_7, self.n_8, self.label, self.top_left_loc,
        self.dot_bottom_left))

class Place_Holder_Piece(Circuit_Piece):
  """
  Circuit_Piece used to hold a place for a particular node that isn't
      present on any other Circuit_Piece, but is present in a circuit. This is
      particularly important for resistor nodes that are not connected to any
      other component in the circuit. Look at get_piece_placement in
      circuit_to_circuit_pieces.py for usage.
  """
  possible_top_left_rows = [PROTO_BOARD_HEIGHT / 2 - 1, PROTO_BOARD_HEIGHT / 2]
  def __init__(self, n):
    """
    |n|: the node for this Place_Holder_Piece.
    """
    assert n, 'invalid n'
    Circuit_Piece.__init__(self, set([n]), 0, 0)
    self.n = n
  def locs_for(self, node):
    self._assert_top_left_loc_set()
    return [self.top_left_loc] if node == self.n else []
  def inverted(self):
    return self
  def draw_on(self, canvas, top_left):
    # nothing to draw
    pass
  def to_cmax_str(self):
    # won't be seen on CMax
    return ''
  def __str__(self):
    return 'Place_Holder_Piece %s' % self.n
  def __eq__(self, other):
    return (isinstance(other, Place_Holder_Piece) and self.n == other.n and
        self.top_left_loc == other.top_left_loc)
  def __hash__(self):
    return hash((self.n, self.top_left_loc))

class Resistor_Piece(Circuit_Piece):
  """
  Representation for the resistor piece.
  """
  def __init__(self, n_1, n_2, r, vertical, label):
    """
    |n_1|, |n_2|: the two nodes of the resistor.
    |r|: resistance of the resistor.
    |vertical|: True if orientation is vertical, False otherwise.
    """
    assert n_1, 'invalid n_1'
    assert n_2, 'invalid n_2'
    width = 1 if vertical else 4
    height = 2 if vertical else 1
    Circuit_Piece.__init__(self, set([n_1, n_2]), width, height, label)
    self.n_1 = n_1
    self.n_2 = n_2
    self.r = r
    self.vertical = vertical
  def locs_for(self, node):
    self._assert_top_left_loc_set()
    r, c = self.top_left_loc
    locs = []
    if node == self.n_1:
      locs.append((r, c))
    if node == self.n_2:
      locs.append((r + 1, c) if self.vertical else (r, c + 3))
    return locs
  def inverted(self):
    return Resistor_Piece(self.n_2, self.n_1, self.r, self.vertical, self.label)
  def _get_color_indices(self):
    """
    Returns a list of the indices (in RESISTOR_COLORS) of the three colors that
        display the resistance of this resistor.
    """
    coeff, exp = ('%.1E' % max(self.r, 10)).split('E+')
    return map(int, str(int(10 * float(coeff)))) + [int(exp) - 1]
  def draw_on(self, canvas, top_left):
    x, y = top_left
    dx = (CONNECTOR_SPACING - CONNECTOR_SIZE) / 2
    # state for color bands
    color_indices = self._get_color_indices()
    size = 2 * CONNECTOR_SIZE + 3 * CONNECTOR_SPACING
    color_size = 5
    color_spacing = 3
    colors_size = 3 * color_size + 2 * color_spacing
    colors_offset = CONNECTOR_SIZE + (size - colors_size) / 2
    if self.vertical:
      # inner rectangle, i.e. the thin one that is partially covered
      canvas.create_rectangle(x, y, x + CONNECTOR_SIZE, y + 4 *
          CONNECTOR_SIZE + 3 * CONNECTOR_SPACING, fill=RESISTOR_INNER_COLOR)
      # outer rectangle, i.e. the fat, short one on top
      canvas.create_rectangle(x - dx, y + CONNECTOR_SIZE, x + CONNECTOR_SIZE +
          dx, y + 3 * CONNECTOR_SIZE + 3 * CONNECTOR_SPACING,
          fill=RESISTOR_OUTER_COLOR)
      for i in xrange(3):
        canvas.create_rectangle(x - dx, y + colors_offset, x + CONNECTOR_SIZE +
            dx, y + colors_offset + color_size, fill=RESISTOR_COLORS[
            color_indices[i]])
        colors_offset += color_size + color_spacing
    else: # horizontal
      # inner rectangle, i.e. the thin one that is partially covered
      canvas.create_rectangle(x, y, x + 4 * CONNECTOR_SIZE + 3 *
          CONNECTOR_SPACING, y + CONNECTOR_SIZE, fill=RESISTOR_INNER_COLOR)
      # outer rectangle, i.e. the fat, short one on top
      canvas.create_rectangle(x + CONNECTOR_SIZE, y - dx, x + 3 *
          CONNECTOR_SIZE + 3 * CONNECTOR_SPACING, y + CONNECTOR_SIZE + dx,
          fill=RESISTOR_OUTER_COLOR)
      for i in xrange(3):
        canvas.create_rectangle(x + colors_offset, y - dx, x + colors_offset +
            color_size, y + CONNECTOR_SIZE + dx, fill=RESISTOR_COLORS[
            color_indices[i]])
        colors_offset += color_size + color_spacing
  def to_cmax_str(self):
    self._assert_top_left_loc_set()
    c, r = loc_to_cmax_rep(self.top_left_loc)
    i1, i2, i3 = self._get_color_indices()
    return 'resistor(%d,%d,%d): (%d,%d)--(%d,%d)' % (i1, i2, i3, c, r, c, r + 3)
  def __str__(self):
    return 'Resistor_Piece %s r=%s vertical=%s' % (str([self.n_1, self.n_2]),
        self.r, self.vertical)
  def __eq__(self, other):
    return (isinstance(other, Resistor_Piece) and self.n_1 == other.n_1 and
        self.n_2 == other.n_2 and self.label == other.label and
        self.top_left_loc == other.top_left_loc and self.r == other.r and
        self.vertical == other.vertical)
  def __hash__(self):
    return hash((self.n_1, self.n_2, self.label, self.top_left_loc, self.r,
        self.vertical))

class Pot_Piece(Circuit_Piece):
  """
  Representation for the pot piece.
  """
  possible_top_left_rows = [3, PROTO_BOARD_HEIGHT / 2 + 1]
  def __init__(self, n_top, n_middle, n_bottom, label, directed_up=True):
    """
    |n_top|, |n_middle|, |n_bottom|: the terminal nodes for this pot.
    |directed_up|: True if this pot is placed with the middle terminal facing
        up, False otherwise (facing down).
    """
    assert n_top, 'invalid n_top'
    assert n_middle, 'invalid n_middle'
    assert n_bottom, 'invalid n_bottom'
    Circuit_Piece.__init__(self, set([n_top, n_middle, n_bottom]), 3, 3, label)
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
    return Pot_Piece(self.n_top, self.n_middle, self.n_bottom, self.label,
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
  def to_cmax_str(self):
    self._assert_top_left_loc_set()
    c, r = loc_to_cmax_rep(self.top_left_loc)
    if self.directed_up:
      return 'pot: (%d,%d)--(%d,%d)--(%d,%d)' % (c, r + 2, c + 1, r, c + 2,
          r + 2)
    else:
      return 'pot: (%d,%d)--(%d,%d)--(%d,%d)' % (c + 2, r, c + 1, r + 2, c, r)
  def __str__(self):
    return 'Pot_Piece %s %s' % (str([self.n_top, self.n_middle,
        self.n_bottom]), self.directed_up)
  def __eq__(self, other):
    return (isinstance(other, Pot_Piece) and self.n_top == other.n_top and
        self.n_middle == other.n_middle and self.n_bottom == other.n_bottom and
        self.label == other.label and self.top_left_loc == other.top_left_loc
        and self.directed_up == other.directed_up)
  def __hash__(self):
    return hash((self.n_top, self.n_middle, self.n_bottom, self.label,
        self.top_left_loc, self.directed_up))

class N_Pin_Connector_Piece(Circuit_Piece):
  """
  Abstract representation for the connector pieces (i.e. motor connector, head
      connector, and robot connector).
  """
  possible_top_left_rows = [0, PROTO_BOARD_HEIGHT - 3]
  def __init__(self, nodes, n, name, disabled_pins, label):
    """
    |n|: the number of pins for this connector.
    |name|: the name for this connector.
    |disabled_pins|: pins that are not meant to be connected to anything.
    """
    Circuit_Piece.__init__(self, set(filter(bool, nodes)), n + 2, 3, label)
    self.n = n
    self.name = name
    self.disabled_pins = disabled_pins
  def loc_for_pin(self, i):
    """
    Returns the location for the |i|th pin of this connector, where |i| is an
        integer between 1 and the number of pins for this connector.
    """
    assert 1 <= i <= self.n, 'i must be between 1 and %d' % self.n
    self._assert_top_left_loc_set()
    r, c = self.top_left_loc
    assert r in self.possible_top_left_rows, 'invalid top left row'
    return (2, c + self.n + 1 - i) if r == 0 else (r, c + i)
  def inverted(self):
    return self
  def draw_on(self, canvas, top_left):
    self._assert_top_left_loc_set()
    r, c = self.top_left_loc
    assert r in self.possible_top_left_rows, 'invalid top left row'
    x, y = top_left
    # draw box
    width = (self.n + 2) * CONNECTOR_SIZE + (self.n + 1) * CONNECTOR_SPACING
    offset_top = (r == 0) * (CONNECTOR_SIZE + 2 * CONNECTOR_SPACING)
    offset_bottom = ((5 * CONNECTOR_SIZE + 4 * CONNECTOR_SPACING) if r == 0
        else (6 * CONNECTOR_SIZE + 6 * CONNECTOR_SPACING))
    padding = 4
    canvas.create_rectangle(x - padding, y - offset_top - padding,
        x + width + padding, y + offset_bottom + padding,
        fill=N_PIN_CONNECTOR_FILL, outline=N_PIN_CONNECTOR_OUTLINE)
    # draw pins
    for i in xrange(1, self.n + 1):
      cr, cc = self.loc_for_pin(i)
      pin_x = x + (cc - c) * (CONNECTOR_SIZE + CONNECTOR_SPACING)
      pin_y = y + (cr - r + 2 * (r == 0)) * (CONNECTOR_SIZE +
          CONNECTOR_SPACING)
      canvas.create_rectangle(pin_x, pin_y, pin_x + CONNECTOR_SIZE,
          pin_y + CONNECTOR_SIZE, fill='#777', outline='black')
      canvas.create_text(pin_x + 3, pin_y + (-CONNECTOR_SIZE - 5 if r == 0 else
          2 * CONNECTOR_SIZE + 5), text=str(i), fill='white')
    # display the connector's name
    canvas.create_text(x + width / 2, y + (r != 0) * 4 * (CONNECTOR_SIZE +
        CONNECTOR_SPACING), text=self.name, width=width, fill='white',
        justify=CENTER)
  def _disconnected_pins(self):
    """
    Returns a tuple of the pins for this connector that are enabled, but are
        not connected to anything else. These pins should be kept sacred along
        with the disabled pins.
    Returns empty tuple by default assuming that all enabled pins are connected
        to something else, but subclasses can override this as necessary.
    """
    return ()
  def get_sacred_locs(self):
    # keep disabled pins and disconnected enabled pins disconnected from
    #     everything else
    return list(self.loc_for_pin(i) for i in (self.disabled_pins +
        self._disconnected_pins()))

class Motor_Connector_Piece(N_Pin_Connector_Piece):
  """
  Representation for the motor connecotor piece.
  """
  def __init__(self, n_pin_5, n_pin_6, label):
    """
    |n_pin_5|: node at pin 5, motor+.
    |n_pin_6|: node at pin 6, motor-.
    """
    assert n_pin_5, 'invalid n_pin_5'
    assert n_pin_6, 'invalid n_pin_6'
    N_Pin_Connector_Piece.__init__(self, [n_pin_5, n_pin_6], 6,
        'Motor Connector', DISABLED_PINS_MOTOR_CONNECTOR, label)
    self.n_pin_5 = n_pin_5
    self.n_pin_6 = n_pin_6
  def locs_for(self, node):
    locs = []
    if node == self.n_pin_5:
      locs.append(self.loc_for_pin(5))
    if node == self.n_pin_6:
      locs.append(self.loc_for_pin(6))
    return locs
  def to_cmax_str(self):
    c1, r1 = loc_to_cmax_rep(self.loc_for_pin(1))
    c6, r6 = loc_to_cmax_rep(self.loc_for_pin(6))
    return 'motor: (%d,%d)--(%d,%d)' % (c1, r1, c6, r6)
  def __str__(self):
    return 'Motor_Connector_Piece pin 5: %s, pin 6: %s' % (self.n_pin_5,
        self.n_pin_6)
  def __eq__(self, other):
    return (isinstance(other, Motor_Connector_Piece) and self.n_pin_5 ==
        other.n_pin_5 and self.n_pin_6 == other.n_pin_6 and self.label ==
        other.label and self.top_left_loc == other.top_left_loc)
  def __hash__(self):
    return hash((self.n_pin_5, self.n_pin_6, self.label, self.top_left_loc))

class Robot_Connector_Piece(N_Pin_Connector_Piece):
  """
  Representation for the robot connector piece.
  """
  def __init__(self, n_pin_2, n_pin_4, label):
    """
    |n_pin_2|: node at pin 2, power.
    |n_pin_4|: node at pin 4, ground.
    """
    assert n_pin_2, 'invalid n_pin_2'
    assert n_pin_4, 'invalid n_pin_4'
    N_Pin_Connector_Piece.__init__(self, [n_pin_2, n_pin_4], 8,
        'Robot Connector', DISABLED_PINS_ROBOT_CONNECTOR, label)
    self.n_pin_2 = n_pin_2
    self.n_pin_4 = n_pin_4
  def locs_for(self, node):
    locs = []
    if node == self.n_pin_2:
      locs.append(self.loc_for_pin(2))
    if node == self.n_pin_4:
      locs.append(self.loc_for_pin(4))
    return locs
  def to_cmax_str(self):
    c1, r1 = loc_to_cmax_rep(self.loc_for_pin(1))
    c8, r8 = loc_to_cmax_rep(self.loc_for_pin(8))
    return 'robot: (%d,%d)--(%d,%d)' % (c1, r1, c8, r8)
  def __str__(self):
    return 'Robot_Connector_Piece pin 2: %s, pin 4: %s' % (self.n_pin_2,
        self.n_pin_4)
  def __eq__(self, other):
    return (isinstance(other, Robot_Connector_Piece) and self.n_pin_2 ==
        other.n_pin_2 and self.n_pin_4 == other.n_pin_4 and self.label ==
        other.label and self.top_left_loc == other.top_left_loc)
  def __hash__(self):
    return hash((self.n_pin_2, self.n_pin_4, self.label, self.top_left_loc))

class Head_Connector_Piece(N_Pin_Connector_Piece):
  """
  Representation for the head connector piece.
  """
  def __init__(self, pin_nodes, label):
    """
    |pin_nodes|: a list containing the nodes from pin 1 to pin 8 in that order.
    """
    assert isinstance(pin_nodes, list) and len(pin_nodes) == 8, ('pin_nodes '
        'should be a list containing 8 values')
    N_Pin_Connector_Piece.__init__(self, pin_nodes, 8, 'Head Connector',
        DISABLED_PINS_HEAD_CONNECTOR, label)
    self.pin_nodes = pin_nodes
  def locs_for(self, node):
    return [self.loc_for_pin(i + 1) for i, pin_node in enumerate(
        self.pin_nodes) if node == pin_node]
  def to_cmax_str(self):
    c1, r1 = loc_to_cmax_rep(self.loc_for_pin(1))
    c8, r8 = loc_to_cmax_rep(self.loc_for_pin(8))
    return 'head: (%d,%d)--(%d,%d)' % (c1, r1, c8, r8)
  def _disconnected_pins(self):
    return tuple(i + 1 for i, pin_node in enumerate(self.pin_nodes) if not
        pin_node)
  def __str__(self):
    return 'Head_Connector_Piece pin_nodes: %s' % str(self.pin_nodes)
  def __eq__(self, other):
    return (isinstance(other, Head_Connector_Piece) and self.pin_nodes ==
        other.pin_nodes and self.label == other.label and self.top_left_loc ==
        other.top_left_loc)
  def __hash__(self):
    return hash(tuple(self.pin_nodes) + (self.label, self.top_left_loc))
