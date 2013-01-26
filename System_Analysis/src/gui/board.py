"""
GUI tool on which several items may be drawn. Supports dragging the items
    around, connecting the items with wires, deleting items, and ...
    TODO(mikemeko).
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from components import Drawable
from components import Wire
from components import Wire_Connector_Drawable
from constants import BOARD_BACKGROUND_COLOR
from constants import BOARD_HEIGHT
from constants import BOARD_MARKER_LINE_COLOR
from constants import BOARD_GRID_SEPARATION
from constants import BOARD_WIDTH
from constants import CONNECTOR_RADIUS
from constants import CONNECTOR_TAG
from constants import DRAG_TAG
from constants import WIRE_CONNECTOR_SIZE
from math import atan2
from math import pi
from Tkinter import ALL
from Tkinter import Canvas
from Tkinter import Frame
from util import create_wire
from util import point_inside_bbox
from util import point_inside_circle
from util import snap

class Board(Frame):
  """
  Tkinter Frame that supports drawing and manipulating various items.
  """
  def __init__(self, parent, width=BOARD_WIDTH, height=BOARD_HEIGHT):
    """
    |width|: the width of this board.
    |height|: the height of this board.
    """
    Frame.__init__(self, parent, background=BOARD_BACKGROUND_COLOR)
    self.width = width
    self.height = height
    # canvas on which items are drawn
    self.canvas = Canvas(self, width=width, height=height,
        highlightthickness=0, background=BOARD_BACKGROUND_COLOR)
    # the drawables on this board
    self.drawables = set()
    self.drawable_offsets = dict()
    # state for dragging
    self._drag_item = None
    self._drag_last_x = None
    self._drag_last_y = None
    # state for drawing wires
    self._wire_parts = None
    self._wire_start = None
    self._wire_end = None
    # setup ui
    self._setup_drawing_board()
    self._setup_bindings()
  def _setup_drawing_board(self):
    """
    Draws grid lines on the board.
    """
    for dim in xrange(0, self.width, BOARD_GRID_SEPARATION):
      self.canvas.create_line((0, dim, self.width, dim),
          fill=BOARD_MARKER_LINE_COLOR)
      self.canvas.create_line((dim, 0, dim, self.height),
          fill=BOARD_MARKER_LINE_COLOR)
    self.canvas.pack()
    self.pack()
  def _setup_bindings(self):
    """
    Makes all necessary event bindings.
    """
    # drag bindings
    self.canvas.tag_bind(DRAG_TAG, '<ButtonPress-1>', self._drag_press)
    self.canvas.tag_bind(DRAG_TAG, '<B1-Motion>', self._drag_move)
    self.canvas.tag_bind(DRAG_TAG, '<ButtonRelease-1>', self._drag_release)
    # wire bindings
    self.canvas.tag_bind(CONNECTOR_TAG, '<ButtonPress-1>', self._wire_press)
    self.canvas.tag_bind(CONNECTOR_TAG, '<B1-Motion>', self._wire_move)
    self.canvas.tag_bind(CONNECTOR_TAG, '<ButtonRelease-1>',
        self._wire_release)
    # delete binding
    self.canvas.tag_bind(ALL, '<ButtonPress-3>', self._delete)
  def _drawable_at(self, point):
    """
    |point|: a tuple of the form (x, y) indicating a location on the canvas.
    Returns the drawable located at canvas location |point|, or None if no such
        item exists.
    """
    for drawable in self.drawables:
      if point_inside_bbox(point, drawable.bounding_box(
          self.drawable_offsets[drawable])):
        return drawable
    return None
  def _connector_at(self, point):
    """
    |point|: a tuple of the form (x, y) indicating a location on the canvas.
    Returns the connector located at canvas location |point|, or None if no
        such connector exists.
    """
    for drawable in self.drawables:
      for connector in drawable.connectors:
        x, y = connector.center
        if point_inside_circle(point, (x, y, CONNECTOR_RADIUS)):
          return connector
    return None
  def _wire_with_id(self, canvas_id):
    """
    Returns the wire with id |canvas_id|, or None if no such wire exists.
    """
    for drawable in self.drawables:
      for connector in drawable.connectors:
        for wire in connector.start_wires:
          if canvas_id in wire.parts:
            return wire
        for wire in connector.end_wires:
          if canvas_id in wire.parts:
            return wire
    return None
  def _drag_press(self, event):
    """
    Callback for when a drawable item is clicked. Updates drag state.
    """
    drag_item = self._drawable_at((event.x, event.y))
    if drag_item is not None:
      self._drag_item = drag_item
      self._drag_last_x = event.x
      self._drag_last_y = event.y
  def _drag_move(self, event):
    """
    Callback for when a drawable item is being moved. Updates drag state.
    """
    if self._drag_item is not None:
      dx = snap(event.x - self._drag_last_x)
      dy = snap(event.y - self._drag_last_y)
      # move the item being dragged
      self._drag_item.move(self.canvas, dx, dy)
      # update drag state
      self._drag_last_x += dx
      self._drag_last_y += dy
      # update offset of item being dragged
      x, y = self.drawable_offsets[self._drag_item]
      self.drawable_offsets[self._drag_item] = x + dx, y + dy
  def _drag_release(self, event):
    """
    Callback for when a drawable item is released. Updates drag state.
    """
    # reset
    self._drag_item = None
    self._drag_last_x = None
    self._drag_last_y = None
  def _straighten_wire(self):
    """
    Ensures that the wire currently being drawn is horizontal or vertical.
    """
    if self._wire_start is not None and self._wire_end is not None:
      x1, y1 = self._wire_start
      x2, y2 = self._wire_end
      if abs(x2 - x1) > abs(y2 - y1):
        self._wire_end = (x2, y1)
      else:
        self._wire_end = (x1, y2)
  def _draw_current_wire(self):
    """
    Draws the wire currently being created.
    """
    if self._wire_parts is not None:
      for part in self._wire_parts:
        self.canvas.delete(part)
    self._straighten_wire()
    x1, y1 = self._wire_start
    x2, y2 = self._wire_end
    self._wire_parts = create_wire(self.canvas, x1, y1, x2, y2)
  def _wire_press(self, event):
    """
    Callback for when a connector is pressed to start creating a wire. Updates
        wire data.
    """
    self._wire_start = (snap(event.x), snap(event.y))
  def _wire_move(self, event):
    """
    Callback for when a wire is changed while being created. Updates wire data.
    """
    new_wire_end = (snap(event.x), snap(event.y))
    if self._wire_end != new_wire_end:
      # update wire end and redraw
      self._wire_end = new_wire_end
      self._draw_current_wire()
  def _wire_release(self, event):
    """
    Callback for when wire creation is complete.
    """
    if self._wire_parts is not None:
      start_connector = self._connector_at(self._wire_start)
      end_connector = self._connector_at(self._wire_end)
      # if no end connector is found when wire drawing is complete, then create
      # a Wire_Connector_Drawable at the end of the wire
      if end_connector is None:
        wire_connector_drawable = Wire_Connector_Drawable()
        # setup offset in an intuitive place based on how the wire was drawn
        ox, oy = map(snap, self._wire_end)
        sx, sy = self._wire_start
        ex, ey = self._wire_end
        angle = atan2(ey - sy, ex - sx)
        if abs(angle) <= pi / 4:
          # east
          ox, oy = ox, oy - WIRE_CONNECTOR_SIZE / 2
        elif abs(angle) >= 3 * pi / 4:
          # west
          ox, oy = ox - WIRE_CONNECTOR_SIZE, oy - WIRE_CONNECTOR_SIZE / 2
        elif angle > 0:
          # south
          ox, oy = ox - WIRE_CONNECTOR_SIZE / 2, oy
        else:
          # north
          ox, oy = ox - WIRE_CONNECTOR_SIZE / 2, oy - WIRE_CONNECTOR_SIZE
        self.add_drawable(wire_connector_drawable, (ox, oy))
        end_connector = self._connector_at(self._wire_end)
      # create wire
      wire = Wire(self._wire_parts, start_connector, end_connector)
      start_connector.start_wires.add(wire)
      end_connector.end_wires.add(wire)
    # reset
    self._wire_parts = None
    self._wire_start = None
    self._wire_end = None
  def _delete(self, event):
    """
    Callback for deleting an item on the board.
    """
    # delete a drawable item?
    drawable_to_delete = self._drawable_at((event.x, event.y))
    if drawable_to_delete is not None:
      drawable_to_delete.delete_from(self.canvas)
      return
    # delete a connector?
    connector_to_delete = self._connector_at((event.x, event.y))
    if connector_to_delete is not None:
      # delete the drawable containing the connector
      connector_to_delete.drawable.delete_from(self.canvas)
      return
    # delete a wire?
    canvas_id = self.canvas.find_closest(event.x, event.y)[0]
    wire_to_delete = self._wire_with_id(canvas_id)
    if wire_to_delete is not None:
      wire_to_delete.delete_from(self.canvas)
  def is_duplicate(self, drawable, offset=(0, 0)):
    """
    Returns True if the exact |drawable| at the given |offset| is already on
        the board, False otherwise.
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    bbox = drawable.bounding_box(offset)
    for other in self.drawables:
      if (drawable.__class__ == other.__class__ and
          bbox == other.bounding_box(self.drawable_offsets[other])):
        return True
    return False
  def add_drawable(self, drawable, offset=(0, 0)):
    """
    Adds the given |drawable| to this board at the given |offset|.
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    # add it to the list of drawables on this board
    self.drawables.add(drawable)
    self.drawable_offsets[drawable] = offset
    # draw it
    drawable.draw_on(self.canvas, offset)
    # draw its connectors
    drawable.draw_connectors(self.canvas, offset)
    # attach drag tag
    for part in drawable.parts:
      self.canvas.itemconfig(part, tags=DRAG_TAG)
