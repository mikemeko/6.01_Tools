"""
All the Drawables for the DT LTI system simulator.
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
from constants import GAIN_DOWN_VERTICES
from constants import GAIN_FILL
from constants import GAIN_HORIZONTAL_CONNECTORS
from constants import GAIN_LEFT_VERTICES
from constants import GAIN_OUTLINE
from constants import GAIN_RIGHT_VERTICES
from constants import GAIN_UP_VERTICES
from constants import GAIN_VERTICAL_CONNECTORS
from constants import IO_FILL
from constants import IO_OUTLINE
from constants import IO_SIZE
from constants import PZD
from constants import RUN_RECT_FILL
from constants import RUN_RECT_OUTLINE
from constants import RUN_RECT_SIZE
from constants import RUN_TEXT_ACTIVE_FILL
from constants import RUN_TEXT_FILL
from constants import USR
from constants import X_CONNECTORS
from constants import Y_CONNECTORS
from core.gui.components import Drawable
from core.gui.util import create_editable_text
from core.gui.util import rotate_connector_flags
from core.util.util import is_callable
from system_simulator.simulation.constants import X
from system_simulator.simulation.constants import Y

class Gain_Drawable(Drawable):
  """
  Abstract Drawable for LTI Gain components.
  """
  def __init__(self, on_gain_changed, vertices=GAIN_RIGHT_VERTICES):
    """
    |on_gain_changed|: function to be called when the gain is changed.
    |vertices|: the vertices of the triangle for this gain.
    """
    assert is_callable(on_gain_changed), 'on_gain_changed must be callable'
    assert vertices in (GAIN_RIGHT_VERTICES, GAIN_DOWN_VERTICES,
        GAIN_LEFT_VERTICES, GAIN_UP_VERTICES), 'invalide gain vertices'
    self.on_gain_changed = on_gain_changed
    self.vertices = vertices
    x1, y1, x2, y2, x3, y3 = vertices
    min_x, max_x = [f(x1, x2, x3) for f in min, max]
    min_y, max_y = [f(y1, y2, y3) for f in min, max]
    Drawable.__init__(self, max_x - min_x, max_y - min_y,
        self._get_connector_flags())
  def _get_connector_flags(self):
    """
    Returns the appropriate connector flags for this gain drawable using its
        vertices.
    """
    if self.vertices in (GAIN_RIGHT_VERTICES, GAIN_LEFT_VERTICES):
      return GAIN_HORIZONTAL_CONNECTORS
    else: # (GAIN_DOWN_VERTICES, GAIN_UP_VERTICES)
      return GAIN_VERTICAL_CONNECTORS
  def draw_on(self, canvas, offset=(0, 0)):
    x1, y1, x2, y2, x3, y3 = self.vertices
    ox, oy = offset
    x1, x2, x3 = x1 + ox, x2 + ox, x3 + ox
    y1, y2, y3 = y1 + oy, y2 + oy, y3 + oy
    self.parts.add(canvas.create_polygon(x1, y1, x2, y2, x3, y3,
        fill=GAIN_FILL, outline=GAIN_OUTLINE))
    gain_text = create_editable_text(canvas, (x1 + x2 + x3) / 3,
        (y1 + y2 + y3) / 3, on_text_changed=self.on_gain_changed)
    self.parts.add(gain_text)
    def get_K():
      """
      Returns a string representing this gain's constant.
      """
      return canvas.itemcget(gain_text, 'text')
    self.get_K = get_K
    def set_K(K):
      """
      Sets the constant for this gain. This is used for deserializing gain
          components (see main/filesave.py).
      """
      canvas.itemconfig(gain_text, text=K)
    self.set_K = set_K
  def rotated(self):
    if self.vertices == GAIN_RIGHT_VERTICES:
      return Gain_Drawable(self.on_gain_changed, GAIN_DOWN_VERTICES)
    elif self.vertices == GAIN_DOWN_VERTICES:
      return Gain_Drawable(self.on_gain_changed, GAIN_LEFT_VERTICES)
    elif self.vertices == GAIN_LEFT_VERTICES:
      return Gain_Drawable(self.on_gain_changed, GAIN_UP_VERTICES)
    elif self.vertices == GAIN_UP_VERTICES:
      return Gain_Drawable(self.on_gain_changed, GAIN_RIGHT_VERTICES)
    else:
      # should never get here
      raise Exception('Unexpected triangle vertices')

class Delay_Drawable(Drawable):
  """
  Drawable for LTI Delay component.
  """
  def __init__(self, connectors=DELAY_CONNECTORS):
    Drawable.__init__(self, DELAY_SIZE, DELAY_SIZE, connectors)
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    self.parts.add(canvas.create_rectangle((ox, oy, ox + DELAY_SIZE,
        oy + DELAY_SIZE), fill=DELAY_FILL, outline=DELAY_OUTLINE))
    self.parts.add(canvas.create_text((ox + DELAY_SIZE / 2,
        oy + DELAY_SIZE / 2), text=DELAY_TEXT))
  def rotated(self):
    return Delay_Drawable(rotate_connector_flags(self.connector_flags))

class Adder_Drawable(Drawable):
  """
  Drawable for LTI Adder component.
  """
  def __init__(self, connectors=ADDER_CONNECTORS):
    d = 2 * ADDER_RADIUS
    Drawable.__init__(self, d, d, connectors)
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
  def rotated(self):
    return Adder_Drawable(rotate_connector_flags(self.connector_flags))

class IO_Drawable(Drawable):
  """
  Drawable for input (X) and output (Y) signals.
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

class IO_X_Drawable(IO_Drawable):
  """
  Drawable for input (X) signal.
  """
  def __init__(self):
    IO_Drawable.__init__(self, X, X_CONNECTORS)

class IO_Y_Drawable(IO_Drawable):
  """
  Drawable for output (Y) signal.
  """
  def __init__(self):
    IO_Drawable.__init__(self, Y, Y_CONNECTORS)

class Run_Drawable(Drawable):
  """
  Abstract Drawable to serve as a "Run" button.
  """
  def __init__(self, text):
    Drawable.__init__(self, RUN_RECT_SIZE, RUN_RECT_SIZE)
    self.text = text
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    self.parts.add(canvas.create_rectangle((ox, oy, ox + RUN_RECT_SIZE,
        oy + RUN_RECT_SIZE), fill=RUN_RECT_FILL, outline=RUN_RECT_OUTLINE))
    self.parts.add(canvas.create_text(ox + RUN_RECT_SIZE / 2, oy +
        RUN_RECT_SIZE / 2, text=self.text, fill=RUN_TEXT_FILL,
        activefill=RUN_TEXT_ACTIVE_FILL))

class PZD_Run_Drawable(Run_Drawable):
  """
  Drawable to surve as a button to draw a pole-zero diagram.
  """
  def __init__(self):
    Run_Drawable.__init__(self, PZD)

class USR_Run_Drawable(Run_Drawable):
  """
  Drawable to serve as a button to draw a unit sample response.
  """
  def __init__(self):
    Run_Drawable.__init__(self, USR)