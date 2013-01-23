"""
GUI example.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from board import Board
from components import Drawable
from constants import CONNECTOR_BOTTOM
from constants import CONNECTOR_LEFT
from constants import CONNECTOR_RIGHT
from constants import CONNECTOR_TOP
from palette import Palette
from Tkinter import Tk

class Rectangle(Drawable):
  """
  Rectangle.
  """
  def __init__(self, width, height, connectors, fill):
    """
    |width|: the width of the rectangle.
    |height|: the height of the rectangle.
    |fill|: fill color for the rectangle.
    """
    Drawable.__init__(self, width, height, connectors)
    self.fill = fill
  def draw_on(self, canvas, offset=(0, 0)):
    """
    Draws this rectangle on the |canvas|.
    """
    self.parts.add(canvas.create_rectangle(self.bounding_box(offset),
        fill=self.fill))

class Circle(Drawable):
  """
  Colorful circle.
  """
  def __init__(self, r, connectors, color1, color2, color3, color4):
    """
    |r|: radius of the circle.
    |color1|, |color2|, |color3|, |color4|: colors to display on the circle.
    """
    Drawable.__init__(self, 2 * r, 2 * r, connectors)
    self.r = r
    self.color1 = color1
    self.color2 = color2
    self.color3 = color3
    self.color4 = color4
  def draw_on(self, canvas, offset=(0, 0)):
    """
    Draws this colorful circle on the |canvas| at the given |offset|.
    """
    x, y = offset
    d = 2 * self.r
    # this demonstrates multiple drawn parts for one drawable item
    self.parts.add(canvas.create_arc(x, y, x + d, y + d, start=0,
        fill=self.color1))
    self.parts.add(canvas.create_arc(x, y, x + d, y + d, start=90,
        fill=self.color2))
    self.parts.add(canvas.create_arc(x, y, x + d, y + d, start=180,
        fill=self.color3))
    self.parts.add(canvas.create_arc(x, y, x + d, y + d, start=270,
        fill=self.color4))

class Triangle(Drawable):
  """
  Triangle.
  """
  def __init__(self, x2, y2, x3, y3, connectors, fill, outline='black'):
    """
    (|x2|, |y2|), (|x3|, |y3|): vertices of the triangle, other than (0, 0).
    |fill|: fill color for the triangle.
    |outline|: outline color for the triangle.
    """
    min_x, max_x = [f(0, x2, x3) for f in min, max]
    min_y, max_y = [f(0, y2, y3) for f in min, max]
    Drawable.__init__(self, max_x - min_x, max_y - min_y, connectors)
    self.x1, self.y1 = 0, 0
    self.x2, self.y2 = x2, y2
    self.x3, self.y3 = x3, y3
    self.fill = fill
    self.outline = outline
  def draw_on(self, canvas, offset=(0, 0)):
    """
    Draws this triangle on the |canvas| at the given |offset|.
    """
    ox, oy = offset
    self.parts.add(canvas.create_polygon(self.x1 + ox, self.y1 + oy,
        self.x2 + ox, self.y2 + oy, self.x3 + ox, self.y3 + oy,
        fill=self.fill, outline=self.outline))

if __name__ == '__main__':
  root = Tk()
  root.resizable(0, 0)
  # create board
  board = Board(root)
  # create palette
  palette = Palette(root, board)
  # add displays to the palette
  palette.add_drawable_type(Circle, 20, CONNECTOR_TOP | CONNECTOR_BOTTOM |
      CONNECTOR_LEFT | CONNECTOR_RIGHT, 'red', 'yellow', 'cyan', 'orange')
  palette.add_drawable_type(Triangle, 0, 40, 30, 20, CONNECTOR_LEFT |
      CONNECTOR_RIGHT, 'green')
  palette.add_drawable_type(Rectangle, 40, 40, CONNECTOR_LEFT |
      CONNECTOR_RIGHT, 'blue')
  # run main loop
  root.mainloop()
