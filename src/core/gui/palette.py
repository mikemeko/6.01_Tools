"""
GUI tool to serve as a palette from which to pick items to add to a board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from board import Board
from components import Drawable
from constants import BOARD_GRID_SEPARATION
from constants import PALETTE_BACKGROUND_COLOR
from constants import PALETTE_HEIGHT
from constants import PALETTE_PADDING
from constants import PALETTE_SEPARATION_LINE_COLOR
from constants import PALETTE_WIDTH
from constants import RIGHT
from constants import WARNING
from random import randint
from time import time
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
    # line to separate left and right sides of palette
    self.left_right_separation_line_id = None
    # setup ui
    self.canvas.pack()
    self.pack()
  def _add_item_callback(self, drawable_type, offset_x, disregard_location,
      **kwargs):
    """
    Returns a callback method that, when called, adds an item of the given
        |drawable_type| to the board, at the given |offset_x|. Does not allow
        adding duplicated items to the board. If |disregard_location| is True,
        location is disregarded on duplicate test.
    """
    assert issubclass(drawable_type, Drawable), ('drawable must be a Drawable '
        'subclass')
    def callback(event):
      # clear current message on the board, if any
      self.board.remove_message()
      # create new drawable
      new_drawable = drawable_type(**kwargs)
      offset_y = self.board.height - new_drawable.height - PALETTE_PADDING
      offset = (offset_x, offset_y)
      # make sure that there isn't already an identical drawable
      if self.board.is_duplicate(new_drawable, offset, disregard_location):
        self.board.display_message('Item is already on the board', WARNING)
        return
      self.board.add_drawable(new_drawable, offset)
      return new_drawable
    return callback
  def _spawn_types_callback(self, types_to_add, offset_x):
    """
    Returns a callback method that, when called, adds the items given in
        |types_to_add| to the board, starting at the given |offset_x|.
    """
    assert isinstance(types_to_add, list), 'types_to_add must be a list'
    def callback(event):
      dx = 0
      # assign the same color and group_id to the types being spawned
      color = '#%02X%02X%02X' % (randint(0, 200), randint(0, 200),
          randint(0, 200))
      group_id = int(round(time() * 1000))
      # TODO(mikemeko): add jointly for correct undo redo
      for add_type, add_disregard_location, add_kwargs in types_to_add:
        add_kwargs['color'] = color
        add_kwargs['group_id'] = group_id
        new_drawable = self._add_item_callback(add_type, offset_x + dx,
            add_disregard_location, **add_kwargs)(event)
        if new_drawable:
          dx += new_drawable.width + BOARD_GRID_SEPARATION
    return callback
  def add_drawable_type(self, drawable_type, side, callback,
      disregard_location=False, types_to_add=None, **kwargs):
    """
    Adds a drawable type for display on this palette.
    |drawable_type|: a subclass of Drawable to display.
    |side|: the side of this palette on which to put the display (LEFT or
        RIGHT).
    |callback|: method to call when display item is clicked. If None, the
        default callback adds an item of the display type to the board.
    |disregard_location|: when checking for duplicates on the board, if this
        flag is set, the locations of drawables will be disregarded.
    |types_to_add|: a list of Drawables to add to the board when this item is
        clicked on the palette, or None if such a callback is not desired.
    |**kwargs|: extra arguments needed to initialize the drawable type.
    """
    assert issubclass(drawable_type, Drawable), ('drawable must be a Drawable '
        'subclass')
    # create a sample (display) drawable
    display = drawable_type(**kwargs)
    # draw the display on the appropriate side of the palette
    if side == RIGHT:
      offset_x = self.current_right_x - PALETTE_PADDING - display.width
      self.current_right_x -= PALETTE_PADDING + display.width + PALETTE_PADDING
      # update left-right separation line
      if self.left_right_separation_line_id:
        self.canvas.delete(self.left_right_separation_line_id)
      separation_x = self.current_right_x - PALETTE_PADDING
      self.left_right_separation_line_id = self.canvas.create_line(
          separation_x, 0, separation_x, self.height,
          fill=PALETTE_SEPARATION_LINE_COLOR)
    else:
      # if given |side| is illegal, assume LEFT
      offset_x = self.current_left_x + PALETTE_PADDING
      self.current_left_x += PALETTE_PADDING + display.width + PALETTE_PADDING
    offset_y = (self.height - display.height) / 2
    if offset_y % BOARD_GRID_SEPARATION:
      offset_y = (offset_y / BOARD_GRID_SEPARATION) * BOARD_GRID_SEPARATION
    offset = (offset_x, offset_y)
    display.draw_on(self.canvas, offset)
    display.draw_connectors(self.canvas, offset)
    # attach callback to drawn parts
    # default callback adds items of this drawable type to the board
    if callback is None:
      callback = self._add_item_callback(drawable_type, offset_x,
          disregard_location, **kwargs) if types_to_add is None else (
          self._spawn_types_callback(types_to_add, offset_x))
    else:
      assert types_to_add is None, ('if callback is provided, types_to_add '
          'will not be used')
    # bind callback
    for part in display.parts:
      self.canvas.tag_bind(part, '<ButtonPress-1>', callback)
    for connector in display.connectors:
      self.canvas.tag_bind(connector.canvas_id, '<ButtonPress-1>', callback)
