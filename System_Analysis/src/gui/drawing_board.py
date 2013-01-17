"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import CONNECTOR_BOTTOM
from constants import CONNECTOR_COLOR
from constants import CONNECTOR_LEFT
from constants import CONNECTOR_RADIUS
from constants import CONNECTOR_RIGHT
from constants import CONNECTOR_TAG
from constants import CONNECTOR_TOP
from constants import DRAG_TAG
from constants import DRAWING_BOARD_BACKGROUND_COLOR
from constants import DRAWING_BOARD_HEIGHT
from constants import DRAWING_BOARD_MARKER_COLOR
from constants import DRAWING_BOARD_MARKER_SEPARATION
from constants import DRAWING_BOARD_MARKER_RADIUS
from constants import DRAWING_BOARD_WIDHT
from Tkinter import Canvas
from Tkinter import Frame
from Tkinter import Tk

class Drawn_Item:
  """
  TODO(mikemeko)
  """
  def __init__(self, bounding_box, connectors=0):
    """
    TODO(mikemeko)
    """
    # TODO(mikemeko): check coiditions
    self.bounding_box = bounding_box
    self.connectors = connectors
    self.connector_items = []
  @property
  def draw_on(self, canvas):
    """
    TODO(mikemeko)
    """
    raise NotImplementedError('subclasses should implement this')

class Drawing_Board(Frame):
  """
  TODO(mikemeko)
  """
  def __init__(self, parent, width=DRAWING_BOARD_WIDHT,
      height=DRAWING_BOARD_HEIGHT):
    """
    TODO(mikemeko)
    """
    Frame.__init__(self, parent)
    self.width = width
    self.height = height
    self.canvas = Canvas(self, width=width, height=height)
    self._setup_drawing_board()
    # dragging info
    self._drag_data = None
    self.canvas.tag_bind(DRAG_TAG, '<ButtonPress-1>', self._drag_press)
    self.canvas.tag_bind(DRAG_TAG, '<B1-Motion>', self._drag_move)
    self.canvas.tag_bind(DRAG_TAG, '<ButtonRelease-1>', self._drag_release)
    # TODO(mikemeko)
    self.id_to_drawn_item = {}
  def _setup_drawing_board(self):
    """
    TODO(mikemeko)
    """
    for x in xrange(0, self.width, DRAWING_BOARD_MARKER_SEPARATION):
      for y in xrange(0, self.height, DRAWING_BOARD_MARKER_SEPARATION):
        self.canvas.create_oval(x - DRAWING_BOARD_MARKER_RADIUS,
            y - DRAWING_BOARD_MARKER_RADIUS, x + DRAWING_BOARD_MARKER_RADIUS,
            y + DRAWING_BOARD_MARKER_RADIUS, fill=DRAWING_BOARD_MARKER_COLOR,
            outline=DRAWING_BOARD_MARKER_COLOR)
    self.canvas.configure(background=DRAWING_BOARD_BACKGROUND_COLOR)
    self.canvas.pack()
    self.configure(background=DRAWING_BOARD_BACKGROUND_COLOR)
    self.pack()
  def _drag_press(self, event):
    """
    TODO(mikemeko)
    """
    assert self._drag_data is None, 'already dragging an item'
    x, y = event.x, event.y
    self._drag_data = (x, y, self.canvas.find_closest(x, y)[0])
  def _drag_move(self, event):
    """
    TODO(mikemeko)
    """
    assert self._drag_data is not None, 'not dragging an item'
    x, y, item = self._drag_data
    dx, dy = event.x - x, event.y - y
    dx = (((dx + DRAWING_BOARD_MARKER_SEPARATION / 2) //
        DRAWING_BOARD_MARKER_SEPARATION) * DRAWING_BOARD_MARKER_SEPARATION)
    dy = (((dy + DRAWING_BOARD_MARKER_SEPARATION / 2) //
        DRAWING_BOARD_MARKER_SEPARATION) * DRAWING_BOARD_MARKER_SEPARATION)
    if dx == 0 and dy == 0:
      return
    self.canvas.move(item, dx, dy)
    self._drag_data = (x + dx, y + dy, item)
    for connector in self.id_to_drawn_item[item].connector_items:
      self.canvas.move(connector, dx, dy)
  def _drag_release(self, event):
    """
    TODO(mikemeko)
    """
    assert self._drag_data is not None, 'not dragging an item'
    self._drag_data = None
  def _draw_connector(self, drawn_item, x, y):
    """
    TODO(mikemeko)
    """
    drawn_item.connector_items.append(self.canvas.create_oval(
        x - CONNECTOR_RADIUS, y - CONNECTOR_RADIUS, x + CONNECTOR_RADIUS,
        y + CONNECTOR_RADIUS, fill=CONNECTOR_COLOR, tags=CONNECTOR_TAG))
  def add_item(self, item_to_draw):
    """
    TODO(mikemeko)
    """
    assert isinstance(item_to_draw, Drawn_Item), ('item_to_draw must be a '
        'Drawn_Item')
    item_to_draw.draw_on(self.canvas)
    self.id_to_drawn_item[self.canvas.find_all()[-1]] = item_to_draw
    # draw connectors
    x1, y1, x2, y2 = item_to_draw.bounding_box
    if item_to_draw.connectors & CONNECTOR_BOTTOM:
      self._draw_connector(item_to_draw, (x1 + x2) / 2, y2)
    if item_to_draw.connectors & CONNECTOR_LEFT:
      self._draw_connector(item_to_draw, x1, (y1 + y2) / 2)
    if item_to_draw.connectors & CONNECTOR_RIGHT:
      self._draw_connector(item_to_draw, x2, (y1 + y2) / 2)
    if item_to_draw.connectors & CONNECTOR_TOP:
      self._draw_connector(item_to_draw, (x1 + x2) / 2, y1)
  def show(self):
    """
    TODO(mikemeko)
    """
    self.mainloop()

# demo
class Circle(Drawn_Item):
  def __init__(self, x, y, radius, connectors, fill):
    Drawn_Item.__init__(self, (x - radius, y - radius, x + radius, y + radius),
        connectors)
    self.x = x
    self.y = y
    self.radius = radius
    self.fill = fill
  def draw_on(self, canvas):
    x1, y1, x2, y2 = self.bounding_box
    canvas.create_oval(x1, y1, x2, y2, fill=self.fill, tags=DRAG_TAG)

if __name__ == '__main__':
  root = Tk()
  root.resizable(0, 0)
  board = Drawing_Board(root)
  board.add_item(Circle(100, 100, 10, CONNECTOR_BOTTOM | CONNECTOR_TOP,
      'yellow'))
  board.add_item(Circle(200, 200, 20, CONNECTOR_RIGHT, 'red'))
  board.mainloop()
