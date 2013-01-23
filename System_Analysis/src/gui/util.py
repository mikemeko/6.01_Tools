"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BOARD_MARKER_SEPARATION
from constants import WIRE_COLOR
from constants import WIRE_WIDTH
from math import sqrt
from Tkinter import Canvas
from Tkinter import CURRENT
from Tkinter import END
from Tkinter import INSERT
from Tkinter import SEL_FIRST
from Tkinter import SEL_LAST

def create_editable_text(canvas, x, y, text='?'):
  """
  TODO(mikemeko)
  don't forget to give credit to http://effbot.org/zone/editing-canvas-text-items.htm
  """
  text_box = canvas.create_text(x, y, text=text)
  def set_focus(event):
    canvas.focus_set()
    canvas.focus(text_box)
    canvas.select_from(CURRENT, 0)
    canvas.select_to(CURRENT, END)
  canvas.tag_bind(text_box, '<Double-Button-1>', set_focus)
  def handle_key(event):
    insert = canvas.index(text_box, INSERT)
    if event.char >= ' ':
      if canvas.select_item():
        canvas.dchars(text_box, SEL_FIRST, SEL_LAST)
        canvas.select_clear()
      canvas.insert(text_box, 'insert', event.char)
    elif event.keysym == 'BackSpace':
      if canvas.select_item():
        canvas.dchars(text_box, SEL_FIRST, SEL_LAST)
        canvas.select_clear()
      else:
        if insert > 0:
          canvas.dchars(text_box, insert - 1, insert)
    elif event.keysym == 'Right':
      canvas.icursor(text_box, insert + 1)
      canvas.select_clear()
    elif event.keysym == 'Left':
      canvas.icursor(text_box, insert - 1)
      canvas.select_clear()
  canvas.tag_bind(text_box, '<Key>', handle_key)
  def release_focus(event):
    canvas.focus('')
  canvas.tag_bind(text_box, '<Return>', release_focus)
  return text_box

def create_circle(canvas, x, y, r, *args, **kwargs):
  """
  Draws a circle of radius |r| centered at (|x|, |y|) on the |canvas|.
  Returns the canvas id of the circle.
  """
  assert isinstance(canvas, Canvas), 'canvas must be a Canvas'
  return canvas.create_oval(x - r, y - r, x + r, y + r, *args, **kwargs)

def create_wire(canvas, x1, y1, x2, y2, fill=WIRE_COLOR):
  """
  Draws a wire on the |canvas| from (|x1|, |y1|) to (|x2|, |y2|).
  Returns the canvas id of the wire.
  """
  assert isinstance(canvas, Canvas), 'canvas must be a Canvas'
  return canvas.create_line(x1, y1, x2, y2, fill=fill, width=WIRE_WIDTH)

def point_inside_bbox(point, bbox):
  """
  |point|: a tuple of the form (x, y) indicating a point.
  |bbox|: a tuple of the form (x1, y1, x2, y2) indicating a bounding box.
  Returns True if |point| is inside the |bbox|, False otherwise.
  """
  x, y = point
  x1, y1, x2, y2 = bbox
  return x1 <= x <= x2 and y1 <= y <= y2

def dist(point1, point2):
  """
  |point1|, |point2|: tuples of the form (x, y) indicating points.
  Returns the distance between the two points.
  """
  x1, y1 = point1
  x2, y2 = point2
  return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def point_inside_circle(point, circle):
  """
  |point|: a tuple of the form (x, y) indicating a point.
  |circle|: a tuple of the form (x, y, r) where (x, y) is the center of the
      circle, and r is its radius.
  Returns True if the point is inside the circle, False otherwise.
  """
  cx, cy, r = circle
  return dist(point, (cx, cy)) <= r

def snap(coord):
  """
  Returns |coord| snapped to the closest board marker location.
  """
  return (((coord + BOARD_MARKER_SEPARATION / 2) // BOARD_MARKER_SEPARATION)
      * BOARD_MARKER_SEPARATION)
