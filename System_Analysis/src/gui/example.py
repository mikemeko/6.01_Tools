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
from Tkinter import Tk

class Circle(Drawable):
  """
  Colorful circle.
  """
  def __init__(self, x, y, r, connectors, color1, color2, color3, color4):
    """
    |x|, |y|, |r|: center and radius for the circle.
    |color1|, |color2|, |color3|, |color4|: colors to display on the circle.
    """
    Drawable.__init__(self, (x - r, y - r, x + r, y + r), connectors)
    self.x = x
    self.y = y
    self.r = r
    self.color1 = color1
    self.color2 = color2
    self.color3 = color3
    self.color4 = color4
  def draw_on(self, canvas):
    """
    Draws this colorful circle on the |canvas|.
    """
    x, y, r = self.x, self.y, self.r
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
  def __init__(self, x1, y1, x2, y2, x3, y3, connectors, fill,
      outline='black'):
    """
    |x1|, |y1|, |x2|, |y2|, |x3|, |y3|: vertices of the triangle.
    |fill|: fill color for the triangle.
    |outline|: outline color for the triangle.
    """
    Drawable.__init__(self, (min(x1, x2, x3), min(y1, y2, y3), max(x1, x2, x3),
        max(y1, y2, y3)), connectors)
    self.x1, self.y1 = x1, y1
    self.x2, self.y2 = x2, y2
    self.x3, self.y3 = x3, y3
    self.fill = fill
    self.outline = outline
  def draw_on(self, canvas):
    """
    Draws this triangle on the |canvas|.
    """
    self.parts.add(canvas.create_polygon(self.x1, self.y1, self.x2, self.y2,
        self.x3, self.y3, fill=self.fill, outline=self.outline))

class Rectangle(Drawable):
  """
  Rectangle.
  """
  def __init__(self, x1, y1, x2, y2, connectors, fill):
    """
    |x1|, |y1|, |x2|, |y2|: bounding box for the rectangle.
    |fill|: fill color for the rectangle.
    """
    Drawable.__init__(self, (x1, y1, x2, y2), connectors)
    self.fill = fill
  def draw_on(self, canvas):
    """
    Draws this rectangle on the |canvas|.
    """
    self.parts.add(canvas.create_rectangle(self.bounding_box, fill=self.fill))

if __name__ == '__main__':
  root = Tk()
  root.resizable(0, 0)
  # create board
  board = Board(root)
  # add items to the board
  board.add_drawable(Triangle(100, 100, 100, 200, 150, 150, CONNECTOR_LEFT |
      CONNECTOR_RIGHT, 'green'))
  board.add_drawable(Circle(300, 300, 20, CONNECTOR_TOP | CONNECTOR_BOTTOM |
      CONNECTOR_LEFT | CONNECTOR_RIGHT, 'yellow', 'red', 'orange', 'cyan'))
  board.add_drawable(Rectangle(10, 10, 70, 70, CONNECTOR_TOP |
      CONNECTOR_BOTTOM, 'blue'))
  board.mainloop()
