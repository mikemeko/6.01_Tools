"""
All the Drawables for the circuit simulator.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import DIRECTION_DOWN
from constants import DIRECTION_LEFT
from constants import DIRECTION_RIGHT
from constants import DIRECTION_UP
from constants import GROUND
from constants import N_PIN_CONNECTOR_FILL
from constants import N_PIN_CONNECTOR_OUTLINE
from constants import N_PIN_CONNECTOR_PER_CONNECTOR
from constants import N_PIN_CONNECTOR_TEXT_SIZE
from constants import NEGATIVE_COLOR
from constants import OP_AMP_CONNECTOR_PADDING
from constants import OP_AMP_DOWN_VERTICES
from constants import OP_AMP_FILL
from constants import OP_AMP_LEFT_VERTICES
from constants import OP_AMP_OUTLINE
from constants import OP_AMP_RIGHT_VERTICES
from constants import OP_AMP_SIGN_PADDING
from constants import OP_AMP_UP_VERTICES
from constants import OPEN_POT_SIGNAL_FILE_TITLE
from constants import PIN_HORIZONTAL_HEIGHT
from constants import PIN_HORIZONTAL_WIDTH
from constants import PIN_OUTLINE
from constants import PIN_RIGHT_CONNECTORS
from constants import PIN_TEXT_COLOR
from constants import POSITIVE_COLOR
from constants import POT_ALPHA_EMPTY_FILL
from constants import POT_ALPHA_FILL
from constants import POT_ALPHA_HEIGHT
from constants import POT_ALPHA_OUTLINE
from constants import POT_ALPHA_TEXT
from constants import POT_ALPHA_WIDTH
from constants import POT_SIGNAL_FILE_EXTENSION
from constants import POT_SIGNAL_FILE_TYPE
from constants import POWER_VOLTS
from constants import PROBE_MINUS
from constants import PROBE_PLUS
from constants import PROBE_SIZE
from constants import PROTO_BOARD
from constants import RE_OP_AMP_VERTICES
from constants import RESISTOR_HORIZONTAL_CONNECTORS
from constants import RESISTOR_HORIZONTAL_HEIGHT
from constants import RESISTOR_HORIZONTAL_WIDTH
from constants import RESISTOR_TEXT_PADDING
from constants import SIMULATE
from core.gui.components import Drawable
from core.gui.components import Run_Drawable
from core.gui.util import create_editable_text
from core.gui.util import rotate_connector_flags
from core.save.constants import RE_INT
from core.save.constants import RE_INT_PAIR
from core.util.util import is_callable
from os.path import isfile
from os.path import relpath
from re import match
from tkFileDialog import askopenfilename
from Tkinter import CENTER
from util import draw_resistor_zig_zags

class Pin_Drawable(Drawable):
  """
  Abstract Drawable to represent pins: power, ground, and probes.
  """
  def __init__(self, text, fill, width, height, connectors):
    """
    |text|: label for this pin.
    |fill|: color for this pin.
    """
    Drawable.__init__(self, width, height, connectors)
    self.text = text
    self.fill = fill
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    self.parts.add(canvas.create_rectangle((ox, oy, ox + self.width,
        oy + self.height), fill=self.fill, outline=PIN_OUTLINE))
    self.parts.add(canvas.create_text(ox + self.width / 2,
        oy + self.height / 2, text=self.text, fill=PIN_TEXT_COLOR,
        width=self.width, justify=CENTER))

class Power_Drawable(Pin_Drawable):
  """
  Power pin.
  """
  def __init__(self, width=PIN_HORIZONTAL_WIDTH, height=PIN_HORIZONTAL_HEIGHT,
      connectors=PIN_RIGHT_CONNECTORS):
    Pin_Drawable.__init__(self, '+%d' % POWER_VOLTS, POSITIVE_COLOR, width,
        height, connectors)
  def rotated(self):
    return Power_Drawable(self.height, self.width,
        rotate_connector_flags(self.connector_flags))
  def serialize(self, offset):
    return 'Power %d %d %d %s' % (self.width, self.height,
        self.connector_flags, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Power %s %s %s %s' % (RE_INT, RE_INT, RE_INT, RE_INT_PAIR),
        item_str)
    if m:
      width, height, connectors, ox, oy = map(int, m.groups())
      board.add_drawable(Power_Drawable(width, height, connectors), (ox, oy))
      return True
    return False

class Ground_Drawable(Pin_Drawable):
  """
  Ground pin.
  """
  def __init__(self, width=PIN_HORIZONTAL_WIDTH, height=PIN_HORIZONTAL_HEIGHT,
      connectors=PIN_RIGHT_CONNECTORS):
    Pin_Drawable.__init__(self, GROUND, NEGATIVE_COLOR, width, height,
        connectors)
  def rotated(self):
    return Ground_Drawable(self.height, self.width,
        rotate_connector_flags(self.connector_flags))
  def serialize(self, offset):
    return 'Ground %d %d %d %s' % (self.width, self.height,
        self.connector_flags, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Ground %s %s %s %s' % (RE_INT, RE_INT, RE_INT, RE_INT_PAIR),
        item_str)
    if m:
      width, height, connectors, ox, oy = map(int, m.groups())
      board.add_drawable(Ground_Drawable(width, height, connectors), (ox, oy))
      return True
    return False

class Probe_Plus_Drawable(Pin_Drawable):
  """
  +probe pin.
  """
  def __init__(self, connectors=PIN_RIGHT_CONNECTORS):
    Pin_Drawable.__init__(self, PROBE_PLUS, POSITIVE_COLOR, PROBE_SIZE,
        PROBE_SIZE, connectors)
  def rotated(self):
    return Probe_Plus_Drawable(rotate_connector_flags(self.connector_flags))
  def deletable(self):
    return False
  def serialize(self, offset):
    return 'Probe_Plus %d %s' % (self.connector_flags, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Probe_Plus %s %s' % (RE_INT, RE_INT_PAIR), item_str)
    if m:
      connectors, ox, oy = map(int, m.groups())
      board.add_drawable(Probe_Plus_Drawable(connectors), (ox, oy))
      return True
    return False

class Probe_Minus_Drawable(Pin_Drawable):
  """
  -probe pin.
  """
  def __init__(self, connectors=PIN_RIGHT_CONNECTORS):
    Pin_Drawable.__init__(self, PROBE_MINUS, NEGATIVE_COLOR, PROBE_SIZE,
        PROBE_SIZE, connectors)
  def rotated(self):
    return Probe_Minus_Drawable(rotate_connector_flags(self.connector_flags))
  def deletable(self):
    return False
  def serialize(self, offset):
    return 'Probe_Minus %d %s' % (self.connector_flags, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Probe_Minus %s %s' % (RE_INT, RE_INT_PAIR), item_str)
    if m:
      connectors, ox, oy = map(int, m.groups())
      board.add_drawable(Probe_Minus_Drawable(connectors), (ox, oy))
      return True
    return False

class Resistor_Drawable(Drawable):
  """
  Drawable for Resistors.
  """
  def __init__(self, on_resistance_changed, width=RESISTOR_HORIZONTAL_WIDTH,
      height=RESISTOR_HORIZONTAL_HEIGHT,
      connectors=RESISTOR_HORIZONTAL_CONNECTORS, init_resistance=1):
    """
    |on_resistance_changed|: function to be called when resistance is changed.
    |init_resistance|: the initial resistance for this resistor.
    """
    assert is_callable(on_resistance_changed), ('on_resistance_changed must be'
        ' callable')
    Drawable.__init__(self, width, height, connectors)
    self.on_resistance_changed = on_resistance_changed
    self.init_resistance = init_resistance
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    w, h = self.width, self.height
    self.parts |= draw_resistor_zig_zags(canvas, ox, oy, w, h)
    if w > h: # horizontal
      resistor_text = create_editable_text(canvas, ox + w / 2,
          oy - RESISTOR_TEXT_PADDING, text=self.init_resistance,
          on_text_changed=self.on_resistance_changed)
    else: # vertical
      resistor_text = create_editable_text(canvas,
          ox + w + RESISTOR_TEXT_PADDING, oy + h / 2,
          text=self.init_resistance,
          on_text_changed=self.on_resistance_changed)
    self.parts.add(resistor_text)
    def get_resistance():
      """
      Returns a string representing this resistor's resistance.
      """
      return canvas.itemcget(resistor_text, 'text')
    self.get_resistance = get_resistance
  def rotated(self):
    return Resistor_Drawable(self.on_resistance_changed, self.height,
        self.width, rotate_connector_flags(self.connector_flags),
        self.get_resistance())
  def serialize(self, offset):
    return 'Resistor %s %d %d %d %s' % (self.get_resistance(), self.width,
        self.height, self.connector_flags, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Resistor (.+) %s %s %s %s' % (RE_INT, RE_INT, RE_INT,
        RE_INT_PAIR), item_str)
    if m:
      r = m.group(1)
      width, height, connectors, ox, oy = map(int, m.groups()[1:])
      board.add_drawable(Resistor_Drawable(lambda: board.set_changed(True),
          width, height, connectors, r), (ox, oy))
      return True
    return False

class Op_Amp_Drawable(Drawable):
  """
  Drawable for op amps.
  """
  def __init__(self, vertices=OP_AMP_RIGHT_VERTICES):
    """
    |vertices|: the vertices of the triangle for this op amp.
    """
    assert vertices in (OP_AMP_RIGHT_VERTICES, OP_AMP_DOWN_VERTICES,
        OP_AMP_LEFT_VERTICES, OP_AMP_UP_VERTICES), 'invalid op amp vertices'
    self.vertices = vertices
    x1, y1, x2, y2, x3, y3 = vertices
    min_x, max_x = [f(x1, x2, x3) for f in min, max]
    min_y, max_y = [f(y1, y2, y3) for f in min, max]
    Drawable.__init__(self, max_x - min_x, max_y - min_y)
  def draw_on(self, canvas, offset=(0, 0)):
    x1, y1, x2, y2, x3, y3 = self.vertices
    ox, oy = offset
    x1, x2, x3 = x1 + ox, x2 + ox, x3 + ox
    y1, y2, y3 = y1 + oy, y2 + oy, y3 + oy
    self.parts.add(canvas.create_polygon(x1, y1, x2, y2, x3, y3,
        fill=OP_AMP_FILL, outline=OP_AMP_OUTLINE))
    if self.vertices == OP_AMP_RIGHT_VERTICES:
      self.parts.add(canvas.create_text(x1 + OP_AMP_SIGN_PADDING,
          y1 + OP_AMP_CONNECTOR_PADDING, text='+'))
      self.parts.add(canvas.create_text(x2 + OP_AMP_SIGN_PADDING,
          y2 - OP_AMP_CONNECTOR_PADDING, text='-'))
    elif self.vertices == OP_AMP_DOWN_VERTICES:
      self.parts.add(canvas.create_text(x3 - OP_AMP_CONNECTOR_PADDING,
          y3 + OP_AMP_SIGN_PADDING, text='+'))
      self.parts.add(canvas.create_text(x1 + OP_AMP_CONNECTOR_PADDING,
          y1 + OP_AMP_SIGN_PADDING, text='-'))
    elif self.vertices == OP_AMP_LEFT_VERTICES:
      self.parts.add(canvas.create_text(x2 - OP_AMP_SIGN_PADDING,
          y2 - OP_AMP_CONNECTOR_PADDING, text='+'))
      self.parts.add(canvas.create_text(x3 - OP_AMP_SIGN_PADDING,
          y3 + OP_AMP_CONNECTOR_PADDING, text='-'))
    else: # OP_AMP_UP_VERTICES
      self.parts.add(canvas.create_text(x2 + OP_AMP_CONNECTOR_PADDING,
          y2 - OP_AMP_SIGN_PADDING, text='+'))
      self.parts.add(canvas.create_text(x3 - OP_AMP_CONNECTOR_PADDING,
          y3 - OP_AMP_SIGN_PADDING, text='-'))
  def draw_connectors(self, canvas, offset=(0, 0)):
    x1, y1, x2, y2, x3, y3 = self.vertices
    ox, oy = offset
    x1, x2, x3 = x1 + ox, x2 + ox, x3 + ox
    y1, y2, y3 = y1 + oy, y2 + oy, y3 + oy
    if self.vertices == OP_AMP_RIGHT_VERTICES:
      self.plus_port = self._draw_connector(canvas, (x1,
          y1 + OP_AMP_CONNECTOR_PADDING))
      self.minus_port = self._draw_connector(canvas, (x2,
          y2 - OP_AMP_CONNECTOR_PADDING))
      self.out_port = self._draw_connector(canvas, (x3, y3))
    elif self.vertices == OP_AMP_DOWN_VERTICES:
      self.plus_port = self._draw_connector(canvas,
          (x3 - OP_AMP_CONNECTOR_PADDING, y3))
      self.minus_port = self._draw_connector(canvas,
          (x1 + OP_AMP_CONNECTOR_PADDING, y1))
      self.out_port = self._draw_connector(canvas, (x2, y2))
    elif self.vertices == OP_AMP_LEFT_VERTICES:
      self.plus_port = self._draw_connector(canvas, (x2,
          y2 - OP_AMP_CONNECTOR_PADDING))
      self.minus_port = self._draw_connector(canvas, (x3,
          y3 + OP_AMP_CONNECTOR_PADDING))
      self.out_port = self._draw_connector(canvas, (x1, y1))
    else: # OP_AMP_UP_VERTICES
      self.plus_port = self._draw_connector(canvas,
          (x2 + OP_AMP_CONNECTOR_PADDING, y2))
      self.minus_port = self._draw_connector(canvas,
          (x3 - OP_AMP_CONNECTOR_PADDING, y3))
      self.out_port = self._draw_connector(canvas, (x1, y1))
  def rotated(self):
    if self.vertices == OP_AMP_RIGHT_VERTICES:
      return Op_Amp_Drawable(OP_AMP_DOWN_VERTICES)
    elif self.vertices == OP_AMP_DOWN_VERTICES:
      return Op_Amp_Drawable(OP_AMP_LEFT_VERTICES)
    elif self.vertices == OP_AMP_LEFT_VERTICES:
      return Op_Amp_Drawable(OP_AMP_UP_VERTICES)
    else: # OP_AMP_UP_VERTICES
      return Op_Amp_Drawable(OP_AMP_RIGHT_VERTICES)
  def serialize(self, offset):
    return 'Op amp %s %s' % (str(self.vertices), str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Op amp %s %s' % (RE_OP_AMP_VERTICES, RE_INT_PAIR), item_str)
    if m:
      x1, y1, x2, y2, x3, y3, ox, oy = map(int, m.groups())
      board.add_drawable(Op_Amp_Drawable((x1, y1, x2, y2, x3, y3)), (ox, oy))
      return True
    return False

class Pot_Drawable(Drawable):
  """
  Drawable for pots.
  """
  def __init__(self, on_signal_file_changed, width=RESISTOR_HORIZONTAL_WIDTH,
      height=RESISTOR_HORIZONTAL_HEIGHT, direction=DIRECTION_UP,
      signal_file=None):
    """
    |on_signal_file_changed|: function to be called when pot signal file is
        changed.
    |direction|: the direction of this pot, one of POT_DIRECTION_DOWN,
        POT_DIRECTION_LEFT, POT_DIRECTION_RIGHT, or POT_DIRECTION_UP.
    |signal_file|: the signal file associated with this pot.
    """
    assert is_callable(on_signal_file_changed), ('on_signal_file_changed must '
        'callable')
    Drawable.__init__(self, width, height)
    self.on_signal_file_changed = on_signal_file_changed
    self.direction = direction
    self.signal_file = signal_file
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    w, h = self.width, self.height
    self.parts |= draw_resistor_zig_zags(canvas, ox, oy, w, h)
    # create button that lets user select a signal file for this pot when
    #     right-clicked
    pot_alpha_window = canvas.create_rectangle(ox + (w - POT_ALPHA_WIDTH) / 2,
        oy + (h - POT_ALPHA_HEIGHT) / 2, ox + (w + POT_ALPHA_WIDTH) / 2,
        oy + (h + POT_ALPHA_HEIGHT) / 2, fill=POT_ALPHA_FILL if
        self.signal_file else POT_ALPHA_EMPTY_FILL, outline=POT_ALPHA_OUTLINE)
    pot_alpha_text = canvas.create_text(ox + w / 2, oy + h / 2 - 1,
        text=POT_ALPHA_TEXT, justify=CENTER, fill='white' if self.signal_file
        else 'black')
    def set_signal_file(event):
      """
      Opens a window to let the user choose a signal file for this pot.
      """
      new_signal_file = askopenfilename(title=OPEN_POT_SIGNAL_FILE_TITLE,
          filetypes=[('%s files' % POT_SIGNAL_FILE_TYPE,
          POT_SIGNAL_FILE_EXTENSION)], initialfile=self.signal_file)
      if new_signal_file and new_signal_file != self.signal_file:
        self.signal_file = relpath(new_signal_file)
        canvas.itemconfig(pot_alpha_window, fill=POT_ALPHA_FILL)
        canvas.itemconfig(pot_alpha_text, fill='white')
        self.on_signal_file_changed()
    for pot_alpha_part in (pot_alpha_window, pot_alpha_text):
      self.parts.add(pot_alpha_part)
      canvas.tag_bind(pot_alpha_part, '<Button-3>', set_signal_file)
  def draw_connectors(self, canvas, offset=(0, 0)):
    ox, oy = offset
    w, h = self.width, self.height
    if self.direction == DIRECTION_UP:
      self.top_connector = self._draw_connector(canvas, (ox, oy + h / 2))
      self.middle_connector = self._draw_connector(canvas, (ox + w / 2, oy))
      self.bottom_connector = self._draw_connector(canvas, (ox + w,
          oy + h / 2))
    elif self.direction == DIRECTION_RIGHT:
      self.top_connector = self._draw_connector(canvas, (ox + w / 2, oy))
      self.middle_connector = self._draw_connector(canvas, (ox + w,
          oy + h / 2))
      self.bottom_connector = self._draw_connector(canvas, (ox + w / 2,
          oy + h))
    elif self.direction == DIRECTION_DOWN:
      self.top_connector = self._draw_connector(canvas, (ox + w,
          oy + h / 2))
      self.middle_connector = self._draw_connector(canvas, (ox + w / 2,
          oy + h))
      self.bottom_connector = self._draw_connector(canvas, (ox, oy + h / 2))
    elif self.direction == DIRECTION_LEFT:
      self.top_connector = self._draw_connector(canvas, (ox + w / 2, oy + h))
      self.middle_connector = self._draw_connector(canvas, (ox, oy + h / 2))
      self.bottom_connector = self._draw_connector(canvas, (ox + w / 2, oy))
    else:
      # should never get here
      raise Exception('Invalid direction %s' % self.direction)
  def rotated(self):
    return Pot_Drawable(self.on_signal_file_changed, self.height, self.width,
        (self.direction + 1) % 4, self.signal_file)
  def serialize(self, offset):
    return 'Pot %s %d %d %d %s' % (self.signal_file, self.width, self.height,
        self.direction, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Pot (.+) %s %s %s %s' % (RE_INT, RE_INT, RE_INT, RE_INT_PAIR),
        item_str)
    if m:
      signal_file = m.group(1)
      if not isfile(signal_file):
        signal_file = None
      width, height, direction, ox, oy = map(int, m.groups()[1:])
      board.add_drawable(Pot_Drawable(lambda: board.set_changed(True), width,
          height, direction, signal_file), (ox, oy))
      return True
    return False

class N_Pin_Connector_Drawable(Drawable):
  """
  TODO(mikemeko)
  """
  def __init__(self, short_name, long_name, n, direction):
    """
    TODO(mikemeko)
    """
    assert isinstance(n, int) and n > 0, 'n must be a positive integer'
    width = N_PIN_CONNECTOR_TEXT_SIZE + N_PIN_CONNECTOR_PER_CONNECTOR
    height = (n + 1) * N_PIN_CONNECTOR_PER_CONNECTOR
    if direction in (DIRECTION_UP, DIRECTION_DOWN):
      width, height = height, width
    Drawable.__init__(self, width, height)
    self.short_name = short_name
    self.long_name = long_name
    self.n = n
    self.direction = direction
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    w, h = self.width, self.height
    self.parts.add(canvas.create_rectangle(ox, oy, ox + w, oy + h,
        fill=N_PIN_CONNECTOR_FILL, outline=N_PIN_CONNECTOR_OUTLINE))
    text = self.short_name if self.direction in (DIRECTION_LEFT,
        DIRECTION_RIGHT) else self.long_name
    text_dx = ((self.direction == DIRECTION_LEFT) - (self.direction ==
        DIRECTION_RIGHT)) * N_PIN_CONNECTOR_PER_CONNECTOR
    text_dy = ((self.direction == DIRECTION_UP) - (self.direction ==
        DIRECTION_DOWN)) * N_PIN_CONNECTOR_PER_CONNECTOR
    self.parts.add(canvas.create_text(ox + w / 2 + text_dx,
        oy + h / 2 + text_dy, text=text, justify=CENTER,
        width=N_PIN_CONNECTOR_TEXT_SIZE))
  def draw_connectors(self, canvas, offset=(0, 0)):
    ox, oy = offset
    text_delta = 9
    sx, sy, dx, dy, text_dx, text_dy = ox, oy, 0, 0, 0, 0
    if self.direction == DIRECTION_UP:
      sx += N_PIN_CONNECTOR_PER_CONNECTOR
      sy += N_PIN_CONNECTOR_PER_CONNECTOR
      dx = N_PIN_CONNECTOR_PER_CONNECTOR
      text_dy = text_delta
    elif self.direction == DIRECTION_RIGHT:
      sx += self.width - N_PIN_CONNECTOR_PER_CONNECTOR
      sy += N_PIN_CONNECTOR_PER_CONNECTOR
      dy = N_PIN_CONNECTOR_PER_CONNECTOR
      text_dx = -text_delta
    elif self.direction == DIRECTION_DOWN:
      sx += self.width - N_PIN_CONNECTOR_PER_CONNECTOR
      sy += self.height - N_PIN_CONNECTOR_PER_CONNECTOR
      dx = -N_PIN_CONNECTOR_PER_CONNECTOR
      text_dy = -text_delta
    elif self.direction == DIRECTION_LEFT:
      sx += N_PIN_CONNECTOR_PER_CONNECTOR
      sy += self.height - N_PIN_CONNECTOR_PER_CONNECTOR
      dy = -N_PIN_CONNECTOR_PER_CONNECTOR
      text_dx = text_delta
    else:
      # should never get here
      raise Exception ('Invalid direction %s' % self.direction)
    self.n_connectors = []
    for i in xrange(self.n):
      x, y = sx + i * dx, sy + i * dy
      self.n_connectors.append(self._draw_connector(canvas, (x, y)))
      self.parts.add(canvas.create_text(x + text_dx, y + text_dy,
          text=str(i + 1)))

class Motor_Connector_Drawable(N_Pin_Connector_Drawable):
  """
  TODO(mikemeko)
  """
  def __init__(self, direction=DIRECTION_RIGHT):
    N_Pin_Connector_Drawable.__init__(self, 'MC', 'Motor Connector', 6,
        direction)
  def rotated(self):
    return Motor_Connector_Drawable(direction=(self.direction + 1) % 4)
  def serialize(self, offset):
    return 'Motor connector %d %s' % (self.direction, str(offset))
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Motor connector %s %s' % (RE_INT, RE_INT_PAIR), item_str)
    if m:
      direction, ox, oy = map(int, m.groups())
      board.add_drawable(Motor_Connector_Drawable(direction), (ox, oy))
      return True
    return False

class Simulate_Run_Drawable(Run_Drawable):
  """
  Drawable to surve as a button to simulate circuit.
  """
  def __init__(self):
    Run_Drawable.__init__(self, SIMULATE)

class Proto_Board_Run_Drawable(Run_Drawable):
  """
  Drawable to surve as button to display proto board layout.
  """
  def __init__(self):
    Run_Drawable.__init__(self, PROTO_BOARD)
