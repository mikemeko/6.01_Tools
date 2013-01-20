"""
GUI tool on which several items may be drawn. Supports dragging the items
    around, connecting the items with wires, deleting items, and ...
    TODO(mikemeko).
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from components import Connector
from components import Drawable
from components import Wire
from constants import BOARD_BACKGROUND_COLOR
from constants import BOARD_HEIGHT
from constants import BOARD_MARKER_COLOR
from constants import BOARD_MARKER_SEPARATION
from constants import BOARD_MARKER_RADIUS
from constants import BOARD_WIDHT
from constants import CONNECTOR_BOTTOM
from constants import CONNECTOR_COLOR
from constants import CONNECTOR_LEFT
from constants import CONNECTOR_RADIUS
from constants import CONNECTOR_RIGHT
from constants import CONNECTOR_TAG
from constants import CONNECTOR_TOP
from constants import DRAG_TAG
from constants import WIRE_COLOR
from constants import WIRE_ILLEGAL_COLOR
from Tkinter import ALL
from Tkinter import Canvas
from Tkinter import Frame
from util import create_circle
from util import create_wire
from util import point_inside_bbox
from util import point_inside_circle

class Board(Frame):
  """
  Tkinter Frame that supports drawing and manipulating various items.
  """
  def __init__(self, parent, width=BOARD_WIDHT, height=BOARD_HEIGHT):
    Frame.__init__(self, parent)
    self.width = width
    self.height = height
    # canvas on which items are drawn
    self.canvas = Canvas(self, width=width, height=height)
    # the drawables on this board
    self.drawables = set()
    # state for dragging
    self._drag_item = None
    self._drag_last_x = None
    self._drag_last_y = None
    # state for drawing wires
    self._wire_id = None
    self._wire_start = None
    self._wire_end = None
    # setup ui
    self._setup_drawing_board()
    self._setup_bindings()
  def _setup_drawing_board(self):
    """
    Draws guide markings on the board.
    """
    for x in xrange(0, self.width, BOARD_MARKER_SEPARATION):
      for y in xrange(0, self.height, BOARD_MARKER_SEPARATION):
        create_circle(self.canvas, x, y, BOARD_MARKER_RADIUS, fill=
            BOARD_MARKER_COLOR, outline=BOARD_MARKER_COLOR)
    self.canvas.configure(background=BOARD_BACKGROUND_COLOR)
    self.canvas.pack()
    self.configure(background=BOARD_BACKGROUND_COLOR)
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
  def _snap(self, coord):
    """
    Returns |coord| snapped to the closest board marker location.
    """
    return (((coord + BOARD_MARKER_SEPARATION / 2) // BOARD_MARKER_SEPARATION)
        * BOARD_MARKER_SEPARATION)
  def _drawable_at(self, point):
    """
    |point|: a tuple of the form (x, y) indicating a location on the canvas.
    Returns the drawable located at canvas location |point|, or None if no such
        item exists.
    """
    for drawable in self.drawables:
      if point_inside_bbox(point, drawable.bounding_box):
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
          if wire.canvas_id == canvas_id:
            return wire
        for wire in connector.end_wires:
          if wire.canvas_id == canvas_id:
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
      dx = self._snap(event.x - self._drag_last_x)
      dy = self._snap(event.y - self._drag_last_y)
      self._drag_item.move(self.canvas, dx, dy)
      self._drag_last_x += dx
      self._drag_last_y += dy
  def _drag_release(self, event):
    """
    Callback for when a drawable item is released. Updates drag state.
    """
    # reset
    self._drag_item = None
    self._drag_last_x = None
    self._drag_last_y = None
  def _draw_current_wire(self):
    """
    Draws the wire currently being created.
    """
    if self._wire_id is not None:
      self.canvas.delete(self._wire_id)
    x1, y1 = self._wire_start
    x2, y2 = self._wire_end
    # indicate whether wire is legal or not
    fill = WIRE_COLOR
    if self._connector_at(self._wire_end) is None:
      fill = WIRE_ILLEGAL_COLOR
    self._wire_id = create_wire(self.canvas, x1, y1, x2, y2, fill=fill)
  def _wire_press(self, event):
    """
    Callback for when a connector is pressed to start creating a wire. Updates
        wire data.
    """
    self._wire_start = (self._snap(event.x), self._snap(event.y))
  def _wire_move(self, event):
    """
    Callback for when a wire is changed while being created. Updates wire data.
    """
    new_wire_end = (self._snap(event.x), self._snap(event.y))
    if self._wire_end != new_wire_end:
      # update wire end and redraw
      self._wire_end = new_wire_end
      self._draw_current_wire()
  def _wire_release(self, event):
    """
    Callback for when wire creation is complete.
    """
    if self._wire_id is not None:
      end_connector = self._connector_at(self._wire_end)
      if end_connector is None:
        self.canvas.delete(self._wire_id)
      else:
        start_connector = self._connector_at(self._wire_start)
        wire = Wire(self._wire_id, start_connector, end_connector)
        start_connector.start_wires.add(wire)
        end_connector.end_wires.add(wire)
    # reset
    self._wire_id = None
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
  def _draw_connector(self, drawable, point):
    """
    |drawable|: a Drawable item.
    |point|: a tuple of the form (x, y) indicating where the connecter should
        be drawn.
    Draws a connector for the given |drawable| at the indicated |point|.
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    x, y = map(self._snap, point)
    canvas_id = create_circle(self.canvas, x, y, CONNECTOR_RADIUS,
        fill=CONNECTOR_COLOR, activewidth=2, tags=CONNECTOR_TAG)
    drawable.connectors.add(Connector(canvas_id, (x, y), drawable))
  def add_drawable(self, drawable):
    """
    Adds the given |drawable| to this board.
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    # add it to the list of drawables on this board
    self.drawables.add(drawable)
    # draw it
    drawable.draw_on(self.canvas)
    # attach drag tag
    for part in drawable.parts:
      self.canvas.itemconfig(part, tags=DRAG_TAG)
    # draw its connectors
    x1, y1, x2, y2 = drawable.bounding_box
    if drawable.connector_flags & CONNECTOR_BOTTOM:
      self._draw_connector(drawable, ((x1 + x2) / 2, y2))
    if drawable.connector_flags & CONNECTOR_LEFT:
      self._draw_connector(drawable, (x1, (y1 + y2) / 2))
    if drawable.connector_flags & CONNECTOR_RIGHT:
      self._draw_connector(drawable, (x2, (y1 + y2) / 2))
    if drawable.connector_flags & CONNECTOR_TOP:
      self._draw_connector(drawable, ((x1 + x2) / 2, y1))
