"""
All the Drawables for the circuit simulator.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import GROUND
from constants import NEGATIVE_COLOR
from constants import PIN_HORIZONTAL_HEIGHT
from constants import PIN_HORIZONTAL_WIDTH
from constants import PIN_OUTLINE
from constants import PIN_RIGHT_CONNECTORS
from constants import PIN_TEXT_COLOR
from constants import POSITIVE_COLOR
from constants import POWER
from constants import PROBE_MINUS
from constants import PROBE_PLUS
from constants import PROBE_SIZE
from constants import RESISTOR_HORIZONTAL_CONNECTORS
from constants import RESISTOR_HORIZONTAL_HEIGHT
from constants import RESISTOR_HORIZONTAL_WIDTH
from constants import RESISTOR_NUM_ZIG_ZAGS
from constants import RESISTOR_TEXT_PADDING
from constants import SIMULATE
from core.gui.components import Drawable
from core.gui.components import Run_Drawable
from core.gui.util import create_editable_text
from core.gui.util import rotate_connector_flags
from Tkinter import CENTER

class Pin_Drawable(Drawable):
  """
  Drawable to represent pins: power and ground.
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
    Pin_Drawable.__init__(self, '+%d' % POWER, POSITIVE_COLOR, width, height,
        connectors)
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
  TODO(mikemeko)
  """
  def __init__(self, connectors=PIN_RIGHT_CONNECTORS):
    Pin_Drawable.__init__(self, PROBE_PLUS, POSITIVE_COLOR, PROBE_SIZE,
        PROBE_SIZE, connectors)
  def rotated(self):
    return Probe_Plus_Drawable(rotate_connector_flags(self.connector_flags))

class Probe_Minus_Drawable(Pin_Drawable):
  """
  TODO(mikemeko)
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
  def __init__(self, width=RESISTOR_HORIZONTAL_WIDTH,
      height=RESISTOR_HORIZONTAL_HEIGHT,
      connectors=RESISTOR_HORIZONTAL_CONNECTORS, init_resistance=1):
    """
    |init_resistance|: the initial resistance for this resistor.
    """
    Drawable.__init__(self, width, height, connectors)
    self.init_resistance = init_resistance
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    w, h = self.width, self.height
    # TODO(mikemeko): constants?
    self.parts.add(canvas.create_rectangle(ox, oy, ox + w, oy + h,
        fill='white', outline='grey'))
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
          oy - RESISTOR_TEXT_PADDING, text=self.init_resistance)
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
          text=self.init_resistance)
    self.parts.add(resistor_text)
    def get_resistance():
      """
      Returns a string representing this resistor's resistance.
      """
      return canvas.itemcget(resistor_text, 'text')
    self.get_resistance = get_resistance
  def rotated(self):
    return Resistor_Drawable(self.height, self.width,
        rotate_connector_flags(self.connector_flags), self.get_resistance())

class Simulate_Run_Drawable(Run_Drawable):
  """
  Drawable to surve as a button to simulate circuit.
  """
  def __init__(self):
    Run_Drawable.__init__(self, SIMULATE)
