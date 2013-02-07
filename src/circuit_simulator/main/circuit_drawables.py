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
from core.gui.components import Drawable
from core.gui.util import rotate_connector_flags
from Tkinter import CENTER

class Pin(Drawable):
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

class Power(Pin):
  """
  Power pin.
  """
  def __init__(self, width=PIN_HORIZONTAL_WIDTH, height=PIN_HORIZONTAL_HEIGHT,
      connectors=PIN_RIGHT_CONNECTORS):
    Pin.__init__(self, '+%d' % POWER, POSITIVE_COLOR, width, height,
        connectors)
  def rotated(self):
    return Power(self.height, self.width,
        rotate_connector_flags(self.connector_flags))

class Ground(Pin):
  """
  Ground pin.
  """
  def __init__(self, width=PIN_HORIZONTAL_WIDTH, height=PIN_HORIZONTAL_HEIGHT,
      connectors=PIN_RIGHT_CONNECTORS):
    Pin.__init__(self, GROUND, NEGATIVE_COLOR, width, height, connectors)
  def rotated(self):
    return Ground(self.height, self.width,
        rotate_connector_flags(self.connector_flags))
