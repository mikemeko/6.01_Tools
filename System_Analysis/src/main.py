"""
Main.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import ADDER_CONNECTORS
from constants import ADDER_FILL
from constants import ADDER_OUTLINE
from constants import ADDER_RADIUS
from constants import ADDER_SEGMENT_SIZE
from constants import DELAY_CONNECTORS
from constants import DELAY_FILL
from constants import DELAY_OUTLINE
from constants import DELAY_SIZE
from constants import DELAY_TEXT
from constants import GAIN_CONNECTORS
from constants import GAIN_FILL
from constants import GAIN_OUTLINE
from constants import GAIN_LEFT_VERTICES
from constants import GAIN_RIGHT_VERTICES
from constants import IO_FILL
from constants import IO_OUTLINE
from constants import IO_PADDING
from constants import IO_SIZE
from constants import X_CONNECTORS
from constants import Y_CONNECTORS
from core.constants import X
from core.constants import Y
from gui.board import Board
from gui.components import Drawable
from gui.palette import Palette
from gui.util import create_editable_text
from Tkinter import Tk

class Gain_Right_Drawable(Drawable):
  """
  Drawable for rightward facing LTI Gain component.
  """
  def __init__(self):
    x1, y1, x2, y2, x3, y3 = GAIN_RIGHT_VERTICES
    min_x, max_x = [f(x1, x2, x3) for f in min, max]
    min_y, max_y = [f(y1, y2, y3) for f in min, max]
    Drawable.__init__(self, max_x - min_x, max_y - min_y, GAIN_CONNECTORS)
  def draw_on(self, canvas, offset=(0, 0)):
    x1, y1, x2, y2, x3, y3 = GAIN_RIGHT_VERTICES
    ox, oy = offset
    x1, x2, x3 = x1 + ox, x2 + ox, x3 + ox
    y1, y2, y3 = y1 + oy, y2 + oy, y3 + oy
    self.parts.add(canvas.create_polygon(x1, y1, x2, y2, x3, y3,
        fill=GAIN_FILL, outline=GAIN_OUTLINE))
    self.gain_text = create_editable_text(canvas, (x1 + x2 + x3) / 3, y3)
    self.parts.add(self.gain_text)

class Gain_Left_Drawable(Drawable):
  """
  Drawable for leftward facing LTI Gain component.
  """
  def __init__(self):
    x1, y1, x2, y2, x3, y3 = GAIN_LEFT_VERTICES
    min_x, max_x = [f(x1, x2, x3) for f in min, max]
    min_y, max_y = [f(y1, y2, y3) for f in min, max]
    Drawable.__init__(self, max_x - min_x, max_y - min_y, GAIN_CONNECTORS)
  def draw_on(self, canvas, offset=(0, 0)):
    x1, y1, x2, y2, x3, y3 = GAIN_LEFT_VERTICES
    ox, oy = offset
    x1, x2, x3 = x1 + ox, x2 + ox, x3 + ox
    y1, y2, y3 = y1 + oy, y2 + oy, y3 + oy
    self.parts.add(canvas.create_polygon(x1, y1, x2, y2, x3, y3,
        fill=GAIN_FILL, outline=GAIN_OUTLINE))
    self.gain_text = create_editable_text(canvas, (x1 + x2 + x3) / 3, y1)
    self.parts.add(self.gain_text)

class Delay_Drawable(Drawable):
  """
  Drawable for LTI Delay component.
  """
  def __init__(self):
    Drawable.__init__(self, DELAY_SIZE, DELAY_SIZE, DELAY_CONNECTORS)
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    self.parts.add(canvas.create_rectangle((ox, oy, ox + DELAY_SIZE,
        oy + DELAY_SIZE), fill=DELAY_FILL, outline=DELAY_OUTLINE))
    self.parts.add(canvas.create_text((ox + DELAY_SIZE / 2,
        oy + DELAY_SIZE / 2), text=DELAY_TEXT))

class Adder_Drawable(Drawable):
  """
  Drawable for LTI Adder component.
  """
  def __init__(self):
    d = 2 * ADDER_RADIUS
    Drawable.__init__(self, d, d, ADDER_CONNECTORS)
  def draw_on(self, canvas, offset=(0, 0)):
    r = ADDER_RADIUS
    d = 2 * r
    ox, oy = offset
    self.parts.add(canvas.create_oval(ox, oy, ox + d, oy + d, fill=ADDER_FILL,
        outline=ADDER_OUTLINE))
    self.parts.add(canvas.create_line(ox + r, oy + r - ADDER_SEGMENT_SIZE / 2,
        ox + r, oy + r + ADDER_SEGMENT_SIZE / 2))
    self.parts.add(canvas.create_line(ox + r - ADDER_SEGMENT_SIZE / 2, oy + r,
        ox + r + ADDER_SEGMENT_SIZE / 2, oy + r))

class IO_Drawable(Drawable):
  """
  Drawable for input and output signals.
  """
  def __init__(self, signal, connectors):
    """
    |signal|: sginal name.
    """
    Drawable.__init__(self, IO_SIZE, IO_SIZE, connectors)
    self.signal = signal
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    self.parts.add(canvas.create_rectangle((ox, oy, ox + IO_SIZE,
        oy + IO_SIZE), fill=IO_FILL, outline=IO_OUTLINE))
    self.parts.add(canvas.create_text((ox + IO_SIZE / 2, oy + IO_SIZE / 2),
        text=self.signal))

if __name__ == '__main__':
  # create board and palette
  root = Tk()
  root.resizable(0, 0)
  board = Board(root)
  palette = Palette(root, board)
  # create input and output boxes (added to board automatically)
  inp = IO_Drawable(X, X_CONNECTORS)
  inp_offset_x = IO_PADDING
  inp_offset_y = board.height / 2 - inp.height / 2
  board.add_drawable(inp, (inp_offset_x, inp_offset_y))
  out= IO_Drawable(Y, Y_CONNECTORS)
  out_offset_x = board.width - out.width - IO_PADDING
  out_offset_y = inp_offset_y
  board.add_drawable(out, (out_offset_x, out_offset_y))
  # add LTI system components to palette
  palette.add_drawable_type(Gain_Right_Drawable)
  palette.add_drawable_type(Gain_Left_Drawable)
  palette.add_drawable_type(Delay_Drawable)
  palette.add_drawable_type(Adder_Drawable)
  # run main loop
  root.mainloop()
