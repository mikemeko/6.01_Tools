"""
All the Drawables for the circuit simulator.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import GROUND
from constants import NEGATIVE_COLOR
from constants import OP_AMP_CONNECTOR_PADDING
from constants import OP_AMP_DOWN_VERTICES
from constants import OP_AMP_FILL
from constants import OP_AMP_LEFT_VERTICES
from constants import OP_AMP_OUTLINE
from constants import OP_AMP_RIGHT_VERTICES
from constants import OP_AMP_SIGN_PADDING
from constants import OP_AMP_UP_VERTICES
from constants import PIN_HORIZONTAL_HEIGHT
from constants import PIN_HORIZONTAL_WIDTH
from constants import PIN_OUTLINE
from constants import PIN_RIGHT_CONNECTORS
from constants import PIN_TEXT_COLOR
from constants import POSITIVE_COLOR
from constants import POWER_VOLTS
from constants import PROBE_MINUS
from constants import PROBE_PLUS
from constants import PROBE_SIZE
from constants import RESISTOR_FILL
from constants import RESISTOR_HORIZONTAL_CONNECTORS
from constants import RESISTOR_HORIZONTAL_HEIGHT
from constants import RESISTOR_HORIZONTAL_WIDTH
from constants import RESISTOR_NUM_ZIG_ZAGS
from constants import RESISTOR_OUTLINE
from constants import RESISTOR_TEXT_PADDING
from constants import SIMULATE
from core.gui.components import Drawable
from core.gui.components import Run_Drawable
from core.gui.util import create_editable_text
from core.gui.util import rotate_connector_flags
from core.util.util import is_callable
from Tkinter import CENTER

class Pin_Drawable(Drawable):
  """
  Drawable to represent pins: power, ground, and probes.
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

class Probe_Plus_Drawable(Pin_Drawable):
  """
  +probe pin.
  """
  def __init__(self, connectors=PIN_RIGHT_CONNECTORS):
    Pin_Drawable.__init__(self, PROBE_PLUS, POSITIVE_COLOR, PROBE_SIZE,
        PROBE_SIZE, connectors)
  def rotated(self):
    return Probe_Plus_Drawable(rotate_connector_flags(self.connector_flags))

class Probe_Minus_Drawable(Pin_Drawable):
  """
  -probe pin.
  """
  def __init__(self, connectors=PIN_RIGHT_CONNECTORS):
    Pin_Drawable.__init__(self, PROBE_MINUS, NEGATIVE_COLOR, PROBE_SIZE,
        PROBE_SIZE, connectors)
  def rotated(self):
    return Probe_Minus_Drawable(rotate_connector_flags(self.connector_flags))

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
    self.parts.add(canvas.create_rectangle(ox, oy, ox + w, oy + h,
        fill=RESISTOR_FILL, outline=RESISTOR_OUTLINE))
    if w > h: # horizontal
      s = w / (2 * RESISTOR_NUM_ZIG_ZAGS)
      self.parts.add(canvas.create_line(ox, oy + h / 2, ox + s, oy))
      for i in xrange(1, RESISTOR_NUM_ZIG_ZAGS):
        self.parts.add(canvas.create_line(ox + (2 * i - 1) * s, oy,
            ox + 2 * i * s, oy + h))
        self.parts.add(canvas.create_line(ox + (2 * i + 1) * s, oy,
            ox + 2 * i * s, oy + h))
      self.parts.add(canvas.create_line(ox + w, oy  + h / 2, ox + w - s, oy))
      resistor_text = create_editable_text(canvas, ox + w / 2,
          oy - RESISTOR_TEXT_PADDING, text=self.init_resistance,
          on_text_changed=self.on_resistance_changed)
    else: # vertical
      s = h / (2 * RESISTOR_NUM_ZIG_ZAGS)
      self.parts.add(canvas.create_line(ox + w / 2, oy, ox + w, oy + s))
      for i in xrange(1, RESISTOR_NUM_ZIG_ZAGS):
        self.parts.add(canvas.create_line(ox, oy + 2 * i * s, ox + w,
            oy + (2 * i - 1) * s))
        self.parts.add(canvas.create_line(ox, oy + 2 * i * s, ox + w,
            oy + (2 * i + 1) * s))
      self.parts.add(canvas.create_line(ox + w / 2, oy + h, ox + w,
          oy + h - s))
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

class Simulate_Run_Drawable(Run_Drawable):
  """
  Drawable to surve as a button to simulate circuit.
  """
  def __init__(self):
    Run_Drawable.__init__(self, SIMULATE)
