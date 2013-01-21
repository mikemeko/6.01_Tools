"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from board import Board
from components import Drawable
from constants import PALETTE_BACKGROUND_COLOR
from constants import PALETTE_HEIGHT
from constants import PALETTE_PADDING
from constants import PALETTE_WIDTH
from Tkinter import Canvas
from Tkinter import Frame

class Palette(Frame):
  """
  TODO(mikemeko)
  """
  def __init__(self, parent, board, width=PALETTE_WIDTH,
      height=PALETTE_HEIGHT):
    """
    TODO(mikemeko)
    """
    assert isinstance(board, Board), 'board must be a Board'
    Frame.__init__(self, parent)
    self.board = board
    self.canvas = Canvas(self, width=width, height=height,
        highlightthickness=0)
    self.width = width
    self.height = height
    self.current_x = 0
    # setup ui
    self._setup_ui()
  def _setup_ui(self):
    """
    TODO(mikemeko)
    """
    self.canvas.configure(background=PALETTE_BACKGROUND_COLOR)
    self.canvas.pack()
    self.configure(background=PALETTE_BACKGROUND_COLOR)
    self.pack()
  def _bind(self, drawable_type, *args, **kwargs):
    """
    TODO(mikemeko)
    """
    def callback(event):
      new_drawable = drawable_type(*args, **kwargs)
      offset_x = PALETTE_PADDING
      offset_y = self.board.height - new_drawable.height - PALETTE_PADDING
      offset = (offset_x, offset_y)
      if not self.board.is_duplicate(new_drawable, offset):
        self.board.add_drawable(new_drawable, offset)
    return callback
  def add_drawable(self, drawable_type, *args, **kwargs):
    """
    TODO(mikemeko)
    """
    assert issubclass(drawable_type, Drawable), ('drawable must be a Drawable '
        'subclass')
    sample = drawable_type(*args, **kwargs)
    offset_x = self.current_x + PALETTE_PADDING
    offset_y = (self.height - sample.height) / 2
    offset = (offset_x, offset_y)
    self.current_x += PALETTE_PADDING + sample.width + PALETTE_PADDING
    sample.draw_on(self.canvas, offset)
    sample.draw_connectors(self.canvas, offset)
    for part in sample.parts:
      self.canvas.tag_bind(part, '<ButtonPress-1>', self._bind(
          drawable_type, *args, **kwargs))
