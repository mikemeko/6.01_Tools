"""
Pole-zero diagram.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import AXES_COLOR
from constants import BACKGROUND_COLOR
from constants import DEFAULT_WINDOW_SIZE
from constants import POLE_COLOR
from constants import POLE_ZERO_RADIUS
from constants import UNIT_CIRCLE_SPACE
from constants import ZERO_COLOR
from system import System
from system_function import System_Function
from Tkinter import Canvas
from Tkinter import Frame
from Tkinter import Tk
from util import empty
from util import in_bounds

class Pole_Zero_Diagram(Frame):
  """
  Frame for pole-zero diagram.
  """
  def __init__(self, parent, sys, window_size=DEFAULT_WINDOW_SIZE):
    """
    |parent|: container of this frame.
    |sys|: System or System_Function for which to draw a pole-zero diagram.
    |window_size|: side-length of pole-zero diagram square window.
    """
    if isinstance(sys, System):
      self.sf = sys.sf
    elif isinstance(sys, System_Function):
      self.sf = sys
    else:
      raise Exception('sys must be a System or System_Function')
    Frame.__init__(self, parent)
    parent.title(str(self.sf))
    self.window_size = window_size
    self._draw_poles_and_zeros()
  def _visible_poles(self):
    """
    Returns the visible poles of the underlying system.
    """
    visible_poles = self.sf.poles()
    for zero in self.sf.zeros():
      if zero in visible_poles:
        visible_poles.remove(zero)
    return map(complex, visible_poles)
  def _visible_zeros(self):
    """
    Returns the visible zeros of the underlying system.
    """
    visible_zeros = self.sf.zeros()
    for pole in self.sf.poles():
      if pole in visible_zeros:
        visible_zeros.remove(pole)
    return map(complex, visible_zeros)
  def _draw_circle(self, canvas, center, radius, fill=''):
    """
    Draws the circle centered at |center| and of the given |radius| on the
        given |canvas|. A fill color may be specified, no fill by default.
        Circle is expected to fit inside canvas.
    """
    assert all(in_bounds(coord + sgn * radius, 0, self.window_size)
        for coord in center for sgn in [-1,1]), 'circle must fit inside canvas'
    cx, cy = center
    canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
        fill=fill)
  def _draw_items(self, canvas, unit_radius, items, color):
    """
    Draws the given |items| (poles or zeros) on the diagram.
    """
    sorted_items = sorted(items, key=lambda c: abs(c))
    counts = dict(zip(sorted_items, [items.count(c) for c in sorted_items]))
    for c in items:
      self._draw_circle(canvas, (self.window_size / 2 + c.real * unit_radius,
          self.window_size / 2 + c.imag * unit_radius),
          POLE_ZERO_RADIUS * counts[c], color)
      counts[c] -= 1
  def _draw_poles_and_zeros(self):
    """
    Draws the poles and zeros of the underlying system on the diagram.
    """
    poles = self._visible_poles()
    zeros = self._visible_zeros()
    # maximum pole / zero magnitude, clipped from below at 1
    if empty(poles) and empty(zeros):
      max_magnitude = 1
    else:
      max_magnitude = max(abs(max(poles + zeros, key=lambda c: abs(c))), 1)
    # radius of unit circle
    unit_radius = (self.window_size / 2 * UNIT_CIRCLE_SPACE) / max_magnitude
    canvas = Canvas(self, width=self.window_size, height=self.window_size)
    # set background color
    canvas.configure(background=BACKGROUND_COLOR)
    # draw axes
    canvas.create_line(self.window_size / 2, 0, self.window_size / 2,
        self.window_size, fill=AXES_COLOR)
    canvas.create_line(0, self.window_size / 2, self.window_size,
        self.window_size / 2, fill=AXES_COLOR)
    # draw unit circle
    self._draw_circle(canvas, (self.window_size / 2, self.window_size / 2),
        unit_radius)
    # draw zeros
    self._draw_items(canvas, unit_radius, zeros, ZERO_COLOR)
    # draw poles
    self._draw_items(canvas, unit_radius, poles, POLE_COLOR)
    canvas.pack()
    self.configure(background=BACKGROUND_COLOR)
    self.pack()
  def show(self):
    """
    Displays the pole-zero diagram.
    """
    self.mainloop()

def plot_pole_zero_diagram(sys):
  """
  Plots the pole-zero diagram of the given system.
  """
  root = Tk()
  root.resizable(0, 0)
  Pole_Zero_Diagram(root, sys).show()
