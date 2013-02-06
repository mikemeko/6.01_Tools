"""
GUI tool to serve as a palette from which to pick items to add to a board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from board import Board
from components import Drawable
from constants import PALETTE_BACKGROUND_COLOR
from constants import PALETTE_HEIGHT
from constants import PALETTE_PADDING
from constants import PALETTE_WIDTH
from constants import RIGHT
from Tkinter import Canvas
from Tkinter import Frame

class Palette(Frame):
  """
  Tkinter Frame that displays all items that can be added to the board.
  """
  def __init__(self, parent, board, width=PALETTE_WIDTH,
      height=PALETTE_HEIGHT):
    """
    |board|: the board on to which items will be added from this palette.
    |width|: the width of this palette.
    |height|: the height of this palette.
    """
    assert isinstance(board, Board), 'board must be a Board'
    Frame.__init__(self, parent, background=PALETTE_BACKGROUND_COLOR)
    self.board = board
    # canvas on which items are displayed
    self.canvas = Canvas(self, width=width, height=height,
        highlightthickness=0, background=PALETTE_BACKGROUND_COLOR)
    self.width = width
    self.height = height
    # x-position of last item added on the LEFT side of this palette
    self.current_left_x = 0
    # x-position of last item added on the RIGHT side of this palette
    self.current_right_x = self.width
    # setup ui
    self.canvas.pack()
    self.pack()
  def _add_item_callback(self, drawable_type, *args, **kwargs):
    """
    Returns a callback method that, when called, adds an item of the given
        |drawable_type| to the board.
    """
    assert issubclass(drawable_type, Drawable), ('drawable must be a Drawable '
        'subclass')
    def callback(event):
      # create new drawable
      new_drawable = drawable_type(*args, **kwargs)
      # offset: bottom-left corner of board
      offset_x = PALETTE_PADDING
      offset_y = self.board.height - new_drawable.height - PALETTE_PADDING
      offset = (offset_x, offset_y)
      # make sure that there isn't already an identical drawable
      if not self.board.is_duplicate(new_drawable, offset):
        self.board.add_drawable(new_drawable, offset)
    return callback
  def add_drawable_type(self, drawable_type, side, callback, *args,
      **kwargs):
    """
    Adds a drawable type for display on this palette.
    |drawable_type|: a subclass of Drawable to display.
    |side|: the side of this palette on which to put the display (LEFT or
        RIGHT).
    |callback|: method to call when display item is clicked. If None, the
        default callback adds an item of the display type to the board.
    |*args, **kwargs|: extra arguments needed to initialize the drawable type.
    """
    assert issubclass(drawable_type, Drawable), ('drawable must be a Drawable '
        'subclass')
    # create a sample (display) drawable
    display = drawable_type(*args, **kwargs)
    # draw the display on the appropriate side of the palette
    if side == RIGHT:
      offset_x = self.current_right_x - PALETTE_PADDING - display.width
      self.current_right_x -= PALETTE_PADDING + display.width + PALETTE_PADDING
    else:
      # if given |side| is illegal, assume LEFT
      offset_x = self.current_left_x + PALETTE_PADDING
      self.current_left_x += PALETTE_PADDING + display.width + PALETTE_PADDING
    offset_y = (self.height - display.height) / 2
    offset = (offset_x, offset_y)
    display.draw_on(self.canvas, offset)
    display.draw_connectors(self.canvas, offset)
    # attach callback to drawn parts
    # default callback adds items of this drawable type to the board
    if callback is None:
      callback = self._add_item_callback(drawable_type, *args, **kwargs)
    for part in display.parts:
      self.canvas.tag_bind(part, '<ButtonPress-1>', callback)
    for connector in display.connectors:
      self.canvas.tag_bind(connector.canvas_id, '<ButtonPress-1>', callback)