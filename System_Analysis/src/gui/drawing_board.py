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
from util import create_circle

class Drawable:
  """
  TODO(mikemeko)
  """
  def __init__(self, bounding_box, connector_flags=0):
    """
    TODO(mikemeko)
    """
    # TODO(mikemeko): check coiditions
    self.bounding_box = bounding_box
    self.connector_flags = connector_flags
    self.connector_ids = []
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
    self.canvas_id_to_drawable = {}
  def _setup_drawing_board(self):
    """
    TODO(mikemeko)
    """
    for x in xrange(0, self.width, DRAWING_BOARD_MARKER_SEPARATION):
      for y in xrange(0, self.height, DRAWING_BOARD_MARKER_SEPARATION):
        create_circle(self.canvas, x, y, DRAWING_BOARD_MARKER_RADIUS, fill=
            DRAWING_BOARD_MARKER_COLOR, outline=DRAWING_BOARD_MARKER_COLOR)
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
  def _snap(self, coord):
    """
    TODO(mikemeko)
    """
    return (((coord + DRAWING_BOARD_MARKER_SEPARATION / 2) //
        DRAWING_BOARD_MARKER_SEPARATION) * DRAWING_BOARD_MARKER_SEPARATION)
  def _drag_move(self, event):
    """
    TODO(mikemeko)
    """
    assert self._drag_data is not None, 'not dragging an item'
    x, y, canvas_id = self._drag_data
    dx, dy = self._snap(event.x - x), self._snap(event.y - y)
    if (dx, dy) != (0, 0):
      self.canvas.move(canvas_id, dx, dy)
      self._drag_data = (x + dx, y + dy, canvas_id)
      for connector_id in self.canvas_id_to_drawable[canvas_id].connector_ids:
        self.canvas.move(connector_id, dx, dy)
  def _drag_release(self, event):
    """
    TODO(mikemeko)
    """
    assert self._drag_data is not None, 'not dragging an item'
    self._drag_data = None
  def _draw_connector(self, drawable, x, y):
    """
    TODO(mikemeko)
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    drawable.connector_ids.append(create_circle(self.canvas, x, y,
        CONNECTOR_RADIUS, fill=CONNECTOR_COLOR, tags=CONNECTOR_TAG))
  def add_drawable(self, drawable):
    """
    TODO(mikemeko)
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    drawable.draw_on(self.canvas)
    self.canvas_id_to_drawable[self.canvas.find_all()[-1]] = drawable
    # draw connectors
    x1, y1, x2, y2 = drawable.bounding_box
    if drawable.connector_flags & CONNECTOR_BOTTOM:
      self._draw_connector(drawable, (x1 + x2) / 2, y2)
    if drawable.connector_flags & CONNECTOR_LEFT:
      self._draw_connector(drawable, x1, (y1 + y2) / 2)
    if drawable.connector_flags & CONNECTOR_RIGHT:
      self._draw_connector(drawable, x2, (y1 + y2) / 2)
    if drawable.connector_flags & CONNECTOR_TOP:
      self._draw_connector(drawable, (x1 + x2) / 2, y1)
  def show(self):
    """
    TODO(mikemeko)
    """
    self.mainloop()

# demo
class Circle(Drawable):
  def __init__(self, x, y, radius, connectors, fill):
    Drawable.__init__(self, (x - radius, y - radius, x + radius, y + radius),
        connectors)
    self.fill = fill
  def draw_on(self, canvas):
    x1, y1, x2, y2 = self.bounding_box
    canvas.create_oval(x1, y1, x2, y2, fill=self.fill, tags=DRAG_TAG)

if __name__ == '__main__':
  root = Tk()
  root.resizable(0, 0)
  board = Drawing_Board(root)
  board.add_drawable(Circle(100, 100, 10, CONNECTOR_BOTTOM | CONNECTOR_LEFT |
      CONNECTOR_RIGHT, 'yellow'))
  board.add_drawable(Circle(200, 200, 20, CONNECTOR_LEFT | CONNECTOR_RIGHT, 'red'))
  board.mainloop()
