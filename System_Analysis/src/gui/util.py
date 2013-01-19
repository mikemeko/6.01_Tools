"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import WIRE_COLOR
from constants import WIRE_WIDTH
from math import sqrt
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

def point_inside_bbox(point, bbox):
  """
  TODO(mikemeko)
  """
  x, y = point
  x1, y1, x2, y2 = bbox
  return x1 <= x <= x2 and y1 <= y <= y2

def dist(point1, point2):
  """
  TODO(mikemeko)
  """
  x1, y1 = point1
  x2, y2 = point2
  return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def point_inside_circle(point, circle):
  """
  TODO(mikemeko)
  """
  cx, cy, r = circle
  return dist(point, (cx, cy)) <= r

def draw_wire(canvas, x1, y1, x2, y2):
  """
  Draws a wire on the |canvas| from (|x1|, |y1|) to (|x2|, |y2|).
  Returns the canvas id of the wire.
  """
  return canvas.create_line(x1, y1, x2, y2, fill=WIRE_COLOR, width=WIRE_WIDTH)
