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

class Pole_Zero_Diagram(Frame):
  """
  TODO(mikemeko)
  """
  def __init__(self, parent, sys):
    Frame.__init__(self, parent)
    if isinstance(sys, System):
      self.sf = sys.sf
    elif isinstance(sys, System_Function):
      self.sf = sys
    else:
      raise Exception('sys must be a System or a System_Function')
    self.poles = self._visible_poles(self.sf)
    self.zeros = self._visible_zeros(self.sf)
    self._set_up()
  def _visible_poles(self, sf):
    """
    TODO(mikemeko)
    """
    visible_poles = sf.poles()
    for zero in sf.zeros():
      if zero in visible_poles:
        visible_poles.pop(zero)
    return map(complex, visible_poles)
  def _visible_zeros(self, sf):
    """
    TODO(mikemeko)
    """
    visible_zeros = sf.zeros()
    for pole in sf.poles():
      if pole in visible_zeros:
        visible_zeros.pop(pole)
    return map(complex, visible_zeros)
  def _draw_oval(self, canvas, center, radius, fill='white'):
    # TODO: don't go out of bound
    cx, cy = center
    canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
        fill=fill)
  def _set_up(self):
    """
    TODO(mikemeko)
    """
    max_radius = abs(max(self.poles + self.zeros, key=lambda c: abs(c)))
    max_radius = max(max_radius, 1)
    unit_radius = 80. / max_radius
    canvas = Canvas(self, width=200, height=200)
    self._draw_oval(canvas, (100, 100), unit_radius)
    print self.poles, self.zeros
    for p in self.poles:
      self._draw_oval(canvas, (100 + p.real * unit_radius,
          100 + p.imag * unit_radius), 4, 'red')
    for z in self.zeros:
      self._draw_oval(canvas, (100 + z.real * unit_radius,
          100 + z.imag * unit_radius), 4, 'blue')
    canvas.create_line(100, 0, 100, 200)
    canvas.create_line(0, 100, 200, 100)
    canvas.configure(background='white')
    canvas.pack()
    self.configure(background='white')
    self.pack()

if __name__ == '__main__':
  sys = System_Function(R_Polynomial([-1,1]), R_Polynomial([2,2,1]))
  root = Tk()
  root.resizable(0, 0)
  pz = Pole_Zero_Diagram(root, sys)
  root.mainloop()
