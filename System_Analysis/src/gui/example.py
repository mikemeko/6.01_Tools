"""
Board example.
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

class Circle(Drawable):
  """
  Colorful circle.
  """
  def __init__(self, r, connectors, color1, color2, color3, color4):
    """
    TODO(mikemeko)
    |x|, |y|, |r|: center and radius for the circle.
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
    Draws this colorful circle on the |canvas|.
    """
    r = self.r
    x, y = offset
    x, y = x + r, y + r
    self.parts.add(canvas.create_arc(x - r, y - r, x + r, y + r,
        start=0, fill=self.color1))
    self.parts.add(canvas.create_arc(x - r, y - r, x + r, y + r,
        start=90, fill=self.color2))
    self.parts.add(canvas.create_arc(x - r, y - r, x + r, y + r,
        start=180, fill=self.color3))
    self.parts.add(canvas.create_arc(x - r, y - r, x + r, y + r,
        start=270, fill=self.color4))

class Triangle(Drawable):
  """
  Triangle.
  """
  def __init__(self, x2, y2, x3, y3, connectors, fill,
      outline='black'):
    """
    |x1|, |y1|, |x2|, |y2|, |x3|, |y3|: vertices of the triangle.
    |fill|: fill color for the triangle.
    |outline|: outline color for the triangle.
    TODO(mikemeko)
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
    Draws this triangle on the |canvas|.
    """
    ox, oy = offset
    self.parts.add(canvas.create_polygon(self.x1 + ox, self.y1 + oy,
        self.x2 + ox, self.y2 + oy, self.x3 + ox, self.y3 + oy,
        fill=self.fill, outline=self.outline))

class Rectangle(Drawable):
  """
  Rectangle.
  """
  def __init__(self, x2, y2, connectors, fill):
    """
    |x1|, |y1|, |x2|, |y2|: bounding box for the rectangle.
    |fill|: fill color for the rectangle.
    TODO(mikemeko)
    """
    Drawable.__init__(self, x2, y2, connectors)
    self.fill = fill
  def draw_on(self, canvas, offset=(0, 0)):
    """
    Draws this rectangle on the |canvas|.
    """
    self.parts.add(canvas.create_rectangle(self.bounding_box(offset),
        fill=self.fill))

if __name__ == '__main__':
  root = Tk()
  root.resizable(0, 0)
  # create board
  board = Board(root)
  # add items to the board
  # TODO(mikemeko)
  palette = Palette(root, board)
  palette.add_drawable(Circle, 20, CONNECTOR_TOP | CONNECTOR_BOTTOM |
      CONNECTOR_LEFT | CONNECTOR_RIGHT, 'red', 'yellow', 'cyan', 'orange')
  palette.add_drawable(Triangle, 0, 40, 30, 20, CONNECTOR_LEFT |
      CONNECTOR_RIGHT, 'green')
  palette.add_drawable(Rectangle, 40, 40, CONNECTOR_LEFT | CONNECTOR_RIGHT,
      'blue')
  root.mainloop()
