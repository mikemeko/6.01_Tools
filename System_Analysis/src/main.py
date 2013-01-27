"""
Main.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import ADDER_CONNECTORS
from constants import ADDER_FILL
from constants import ADDER_OUTLINE
from constants import ADDER_RADIUS
from constants import ADDER_SEGMENT_SIZE
from constants import APP_NAME
from constants import DELAY_CONNECTORS
from constants import DELAY_FILL
from constants import DELAY_OUTLINE
from constants import DELAY_SIZE
from constants import DELAY_TEXT
from constants import DEV_STAGE
from constants import GAIN_CONNECTORS
from constants import GAIN_FILL
from constants import GAIN_OUTLINE
from constants import GAIN_LEFT_VERTICES
from constants import GAIN_RIGHT_VERTICES
from constants import IO_FILL
from constants import IO_OUTLINE
from constants import IO_PADDING
from constants import IO_SIZE
from constants import RUN_OUTLINE
from constants import RUN_RECT_FILL
from constants import RUN_RECT_SIZE
from constants import RUN_TRIANGLE_FILL
from constants import RUN_TRIANGLE_VERTICES
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
from core.util import empty
from gui.board import Board
from gui.components import Drawable
from gui.components import Wire_Connector_Drawable
from gui.palette import Palette
from gui.util import create_editable_text
from Tkinter import Tk

class Gain_Drawable(Drawable):
  """
  TODO(mikemeko)
  """
  def __init__(self, vertices):
    """
    TODO(mikemeko)
    """
    x1, y1, x2, y2, x3, y3 = vertices
    min_x, max_x = [f(x1, x2, x3) for f in min, max]
    min_y, max_y = [f(y1, y2, y3) for f in min, max]
    Drawable.__init__(self, max_x - min_x, max_y - min_y, GAIN_CONNECTORS)
    self.vertices = vertices
  def draw_on(self, canvas, offset=(0, 0)):
    # TODO(mikemeko): this is a hack :(
    self.canvas = canvas
    x1, y1, x2, y2, x3, y3 = self.vertices
    ox, oy = offset
    x1, x2, x3 = x1 + ox, x2 + ox, x3 + ox
    y1, y2, y3 = y1 + oy, y2 + oy, y3 + oy
    self.parts.add(canvas.create_polygon(x1, y1, x2, y2, x3, y3,
        fill=GAIN_FILL, outline=GAIN_OUTLINE))
    self.gain_text = create_editable_text(canvas, (x1 + x2 + x3) / 3,
        oy + self.height / 2)
    self.parts.add(self.gain_text)
  def get_K(self):
    try:
      # TODO(mikemeko)
      return float(self.canvas.itemcget(self.gain_text, 'text'))
    except:
      # TODO(mikemeko)
      raise Exception('could not get gain')
class Gain_Right_Drawable(Gain_Drawable):
  """
  Drawable for rightward facing LTI Gain component.
  """
  def __init__(self):
    Gain_Drawable.__init__(self, GAIN_RIGHT_VERTICES)

class Gain_Left_Drawable(Gain_Drawable):
  """
  Drawable for leftward facing LTI Gain component.
  """
  def __init__(self):
    Gain_Drawable.__init__(self, GAIN_LEFT_VERTICES)

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

class Run_Drawable(Drawable):
  """
  Drawable to serve as a "Run" button.
  """
  def __init__(self):
    Drawable.__init__(self, RUN_RECT_SIZE, RUN_RECT_SIZE)
  def draw_on(self, canvas, offset=(0, 0)):
    # TODO(mikemeko): make prettier run button
    x1, y1, x2, y2, x3, y3 = RUN_TRIANGLE_VERTICES
    ox, oy = offset
    x1, x2, x3 = x1 + ox, x2 + ox, x3 + ox
    y1, y2, y3 = y1 + oy, y2 + oy, y3 + oy
    self.parts.add(canvas.create_rectangle((ox, oy, ox + RUN_RECT_SIZE,
        oy + RUN_RECT_SIZE), fill=RUN_RECT_FILL, outline=RUN_OUTLINE))
    self.parts.add(canvas.create_polygon(x1, y1, x2, y2, x3, y3,
        fill=RUN_TRIANGLE_FILL, outline=RUN_OUTLINE))

if __name__ == '__main__':
  # create board and palette
  root = Tk()
  root.resizable(0, 0)
  root.title('%s (%s)' % (APP_NAME, DEV_STAGE))
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
  def callback(event):
    """
    TODO(mikemeko): comment; look over below code
    """
    system_components = []
    X_label, Y_label = None, None
    for drawable in board.drawables:
      inp, out = [], []
      for connector in drawable.connectors:
        inp.extend(wire.label for wire in connector.end_wires)
        out.extend(wire.label for wire in connector.start_wires)
      if isinstance(drawable, Gain_Right_Drawable) or isinstance(drawable,
          Gain_Left_Drawable):
        assert len(inp) == 1
        assert len(out) == 1
        system_components.append(Gain(inp[0], out[0], drawable.get_K()))
      elif isinstance(drawable, Delay_Drawable):
        assert len(inp) == 1
        assert len(out) == 1
        system_components.append(Delay(inp[0], out[0]))
      elif isinstance(drawable, Adder_Drawable):
        assert len(inp) >= 1
        assert len(out) == 1
        system_components.append(Adder(inp, out[0]))
      elif isinstance(drawable, IO_Drawable):
        assert len(drawable.connectors) == 1
        connector = iter(drawable.connectors).next()
        if drawable.signal == X:
          assert empty(connector.end_wires)
          # TODO(mikemeko): below assert not needed?
          #assert len(connector.start_wires) == 1
          assert X_label is None
          X_label = iter(connector.start_wires).next().label
        else:
          assert empty(connector.start_wires)
          assert len(connector.end_wires) == 1
          assert Y_label is None
          Y_label = iter(connector.end_wires).next().label
      elif isinstance(drawable, Wire_Connector_Drawable):
        # nothing to do
        pass
      else:
        raise Exception('Illegal drawable')
    assert X_label is not None
    assert Y_label is not None
    sys = System(system_components, X=X_label, Y=Y_label)
    plot_pole_zero_diagram(sys)
  palette.add_drawable_type(Run_Drawable, on_left=False, callback=callback)
  # run main loop
  root.mainloop()
