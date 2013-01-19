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
  def __init__(self, x, y, radius, connectors, fill):
    Drawable.__init__(self, (x - radius, y - radius, x + radius, y + radius),
        connectors)
    self.fill = fill
  def draw_on(self, canvas):
    x1, y1, x2, y2 = self.bounding_box
    self.parts.add(canvas.create_oval(x1, y1, x2, y2, fill=self.fill))

class Triangle(Drawable):
  def __init__(self, x1, y1, x2, y2, x3, y3, connectors, fill,
      outline='black'):
    Drawable.__init__(self, (min(x1, x2, x3), min(y1, y2, y3), max(x1, x2, x3),
        max(y1, y2, y3)), connectors)
    self.x1, self.y1, self.x2, self.y2, self.x3, self.y3 = (x1, y1, x2, y2, x3,
        y3)
    self.fill = fill
    self.outline = outline
  def draw_on(self, canvas):
    self.parts.add(canvas.create_polygon(self.x1, self.y1, self.x2, self.y2,
        self.x3, self.y3, fill=self.fill, outline=self.outline))

class Rectangle(Drawable):
  def __init__(self, x1, y1, x2, y2, connectors, fill):
    Drawable.__init__(self, (x1, y1, x2, y2), connectors)
    self.fill = fill
  def draw_on(self, canvas):
    self.parts.add(canvas.create_rectangle(self.bounding_box,
        fill=self.fill))

if __name__ == '__main__':
  root = Tk()
  root.resizable(0, 0)
  board = Board(root)
  board.add_drawable(Triangle(100, 100, 100, 200, 150, 150, CONNECTOR_LEFT |
      CONNECTOR_RIGHT, 'green'))
  board.add_drawable(Circle(300, 300, 20, CONNECTOR_TOP | CONNECTOR_BOTTOM,
      'yellow'))
  board.add_drawable(Rectangle(10, 10, 70, 70, CONNECTOR_LEFT | CONNECTOR_RIGHT |
      CONNECTOR_TOP | CONNECTOR_BOTTOM, 'blue'))
  board.mainloop()
