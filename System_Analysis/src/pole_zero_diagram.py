"""
Pole-zero diagram.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from poly import R_Polynomial
from system import System
from system_function import System_Function
from Tkinter import Canvas
from Tkinter import Frame
from Tkinter import Tk

# constants
DEFAULT_WINDOW_SIZE = 400
UNIT_CIRCLE_SPACE = 0.9
POLE_ZERO_RADIUS = 4
POLE_COLOR = 'red'
ZERO_COLOR = 'cyan'
BACKGROUND_COLOR = 'white'

class Pole_Zero_Diagram(Frame):
  """
  TODO(mikemeko)
  """
  def __init__(self, parent, sys, window_size=DEFAULT_WINDOW_SIZE):
    Frame.__init__(self, parent)
    if isinstance(sys, System):
      self.sf = sys.sf
    elif isinstance(sys, System_Function):
      self.sf = sys
    else:
      raise Exception('sys must be a System or System_Function')
    self.window_size = window_size
    parent.title(str(self.sf))
    self._draw_poles_and_zeros(self._visible_poles(), self._visible_zeros())
  def _visible_poles(self):
    """
    TODO(mikemeko)
    """
    visible_poles = self.sf.poles()
    for zero in self.sf.zeros():
      if zero in visible_poles:
        visible_poles.pop(zero)
    return map(complex, visible_poles)
  def _visible_zeros(self):
    """
    TODO(mikemeko)
    """
    visible_zeros = self.sf.zeros()
    for pole in self.sf.poles():
      if pole in visible_zeros:
        visible_zeros.pop(pole)
    return map(complex, visible_zeros)
  def _draw_circle(self, canvas, center, radius, fill='white'):
    """
    TODO(mikemeko)
    """
    assert all(x + dx * radius for x in center for dx in [-1,1]), (
        'circle must fit inside canvas')
    cx, cy = center
    canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
        fill=fill)
  def _draw_items(self, canvas, unit_radius, items, color):
    """
    TODO(mikemeko)
    """
    sorted_items = sorted(items, key=lambda c: abs(c))
    counts = dict(zip(sorted_items, [items.count(c) for c in sorted_items]))
    for c in items:
      self._draw_circle(canvas, (self.window_size / 2 + c.real * unit_radius,
          self.window_size / 2 + c.imag * unit_radius),
          POLE_ZERO_RADIUS * counts[c], color)
      counts[c] -= 1
  def _draw_poles_and_zeros(self, poles, zeros):
    """
    TODO(mikemeko)
    """
    # maximum pole / zero magnitude, clipped from below at 1
    max_magnitude = max(abs(max(poles + zeros, key=lambda c: abs(c))), 1)
    # radius of unit circle
    unit_radius = (self.window_size / 2 * UNIT_CIRCLE_SPACE) / max_magnitude
    canvas = Canvas(self, width=self.window_size, height=self.window_size)
    # draw unit circle
    self._draw_circle(canvas, (self.window_size / 2, self.window_size / 2),
        unit_radius)
    # draw zeros
    self._draw_items(canvas, unit_radius, zeros, ZERO_COLOR)
    # draw poles
    self._draw_items(canvas, unit_radius, poles, POLE_COLOR)
    # draw axes
    canvas.create_line(self.window_size / 2, 0, self.window_size / 2,
        self.window_size)
    canvas.create_line(0, self.window_size / 2, self.window_size,
        self.window_size / 2)
    canvas.configure(background=BACKGROUND_COLOR)
    canvas.pack()
    self.configure(background=BACKGROUND_COLOR)
    self.pack()

if __name__ == '__main__':
  root = Tk()
  root.resizable(0, 0)
  pz = Pole_Zero_Diagram(root, System_Function(R_Polynomial([1,1,1]),
      R_Polynomial([1,1,1,1])))
  root.mainloop()
