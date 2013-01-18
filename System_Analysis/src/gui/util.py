"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from Tkinter import Canvas

def create_circle(canvas, x, y, r, *args, **kwargs):
  """
  Creates a circle of radius |r| on the given |canvas| centered at (|x|, |y|).
  Returns the id assigned to the circle on the |canvas|.
  """
  assert isinstance(canvas, Canvas), 'canvas must be a Tkinter Canvas'
  assert isinstance(x, (float, int, long)), 'x must be a number'
  assert isinstance(y, (float, int, long)), 'y must be a number'
  assert isinstance(r, (float, int, long)), 'r must be a number'
  return canvas.create_oval(x - r, y - r, x + r, y + r, *args, **kwargs)
