"""
Main.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import ADDER_CONNECTORS
from constants import ADDER_FILL
from constants import ADDER_OUTLINE
from constants import ADDER_RADIUS
from constants import ADDER_TEXT
from constants import DELAY_BBOX
from constants import DELAY_CONNECTORS
from constants import DELAY_FILL
from constants import DELAY_OUTLINE
from constants import DELAY_TEXT
from constants import GAIN_CONNECTORS
from constants import GAIN_FILL
from constants import GAIN_OUTLINE
from constants import GAIN_VERTICES
from constants import IO_BBOX
from constants import IO_FILL
from constants import IO_OUTLINE
from constants import IO_PADDING
from constants import WIRE_CONNECTOR_CONNECTORS
from constants import WIRE_CONNECTOR_FILL
from constants import WIRE_CONNECTOR_OUTLINE
from constants import WIRE_CONNECTOR_RADIUS
from constants import X_CONNECTORS
from constants import Y_CONNECTORS
from core.constants import X
from core.constants import Y
from core.pole_zero_diagram import plot_pole_zero_diagram
from core.system import Adder
from core.system import Delay
from core.system import Gain
from core.system import System
from core.unit_sample_response import plot_unit_sample_response
from gui.board import Board
from gui.components import Drawable
from gui.constants import CONNECTOR_BOTTOM
from gui.constants import CONNECTOR_LEFT
from gui.constants import CONNECTOR_RIGHT
from gui.constants import CONNECTOR_TOP
from gui.palette import Palette
from gui.util import create_editable_text
from Tkinter import Tk

class Gain_Drawable(Drawable):
  """
  TODO(mikemeko)
  """
  def __init__(self):
    x1, y1, x2, y2, x3, y3 = GAIN_VERTICES
    min_x, max_x = [f(x1, x2, x3) for f in min, max]
    min_y, max_y = [f(y1, y2, y3) for f in min, max]
    Drawable.__init__(self, max_x - min_x, max_y - min_y, GAIN_CONNECTORS)
  def draw_on(self, canvas, offset=(0, 0)):
    """
    TODO(mikemeko)
    """
    x1, y1, x2, y2, x3, y3 = GAIN_VERTICES
    ox, oy = offset
    self.parts.add(canvas.create_polygon(x1 + ox, y1 + oy, x2 + ox, y2 + oy,
        x3 + ox, y3 + oy, fill=GAIN_FILL, outline=GAIN_OUTLINE))
    self.gain_text = create_editable_text(canvas,
        (ox + x1 + ox + x2 + ox + x3) / 3, oy + y3)
    self.parts.add(self.gain_text)

class Delay_Drawable(Drawable):
  """
  TODO(mikemeko)
  """
  def __init__(self):
    x1, y1, x2, y2 = DELAY_BBOX
    Drawable.__init__(self, x2 - x1, y2 - y1, DELAY_CONNECTORS)
  def draw_on(self, canvas, offset=(0, 0)):
    """
    TODO(mikemeko)
    """
    x1, y1, x2, y2 = DELAY_BBOX
    ox, oy = offset
    self.parts.add(canvas.create_rectangle((x1 + ox, y1 + oy, x2 + ox,
        y2 + oy), fill=DELAY_FILL, outline=DELAY_OUTLINE))
    self.parts.add(canvas.create_text(((ox + x1 + ox + x2) / 2,
        (oy + y1 + oy + y2) / 2), text=DELAY_TEXT))

class Adder_Drawable(Drawable):
  """
  TODO(mikemeko)
  """
  def __init__(self):
    d = 2 * ADDER_RADIUS
    Drawable.__init__(self, d, d, ADDER_CONNECTORS)
  def draw_on(self, canvas, offset=(0, 0)):
    """
    TODO(mikemeko)
    """
    d = 2 * ADDER_RADIUS
    ox, oy = offset
    self.parts.add(canvas.create_oval(ox, oy, ox + d, oy + d, fill=ADDER_FILL,
        outline=ADDER_OUTLINE))
    self.parts.add(canvas.create_text((ox + ADDER_RADIUS, oy + ADDER_RADIUS),
        text=ADDER_TEXT))

class Wire_Connector_Drawable(Drawable):
  """
  TODO(mikemeko)
  """
  def __init__(self):
    d = 2 * WIRE_CONNECTOR_RADIUS
    Drawable.__init__(self, d, d, WIRE_CONNECTOR_CONNECTORS)
  def draw_on(self, canvas, offset=(0, 0)):
    """
    TODO(mikemeko)
    """
    d = 2 * WIRE_CONNECTOR_RADIUS
    ox, oy = offset
    self.parts.add(canvas.create_oval(ox, oy, ox + d, oy + d,
        fill=WIRE_CONNECTOR_FILL, outline=WIRE_CONNECTOR_OUTLINE))

class IO_Drawable(Drawable):
  """
  TODO(mikemeko)
  """
  def __init__(self, signal, connectors):
    """
    TODO(mikemeko)
    """
    x1, y1, x2, y2 = IO_BBOX
    Drawable.__init__(self, x2 - x1, y2 - y1, connectors)
    self.signal = signal
  def draw_on(self, canvas, offset=(0, 0)):
    """
    TODO(mikemeko)
    """
    x1, y1, x2, y2 = IO_BBOX
    ox, oy = offset
    self.parts.add(canvas.create_rectangle((x1 + ox, y1 + oy, x2 + ox,
        y2 + oy), fill=IO_FILL, outline=IO_OUTLINE))
    self.parts.add(canvas.create_text(((ox + x1 + ox + x2) / 2,
        (oy + y1 + oy + y2) / 2), text=self.signal))

if __name__ == '__main__':
  # TODO(mikemeko): comment
  root = Tk()
  root.resizable(0, 0)
  board = Board(root)
  palette = Palette(root, board)
  # TODO(mikemeko)
  inp = IO_Drawable(X, X_CONNECTORS)
  inp_offset_x = IO_PADDING
  inp_offset_y = board.height / 2 - inp.height / 2
  board.add_drawable(inp, (inp_offset_x, inp_offset_y))
  out= IO_Drawable(Y, Y_CONNECTORS)
  out_offset_x = board.width - out.width - IO_PADDING
  out_offset_y = inp_offset_y
  board.add_drawable(out, (out_offset_x, out_offset_y))
  # TODO(mikemeko)
  palette.add_drawable_type(Gain_Drawable)
  palette.add_drawable_type(Delay_Drawable)
  palette.add_drawable_type(Adder_Drawable)
  palette.add_drawable_type(Wire_Connector_Drawable)
  root.mainloop()
