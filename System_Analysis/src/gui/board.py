"""
GUI tool on which several items may be drawn. Supports dragging the items
    around, connecting the items with wires, deleting items, and ...
    TODO(mikemeko).
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from components import Connector
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
from constants import WIRE_WIDTH
from Tkinter import ALL
from Tkinter import Canvas
from Tkinter import Frame
from util import create_circle
from util import point_inside_bbox
from util import point_inside_circle

class Board(Frame):
  def __init__(self, parent, width=BOARD_WIDHT, height=BOARD_HEIGHT):
    Frame.__init__(self, parent)
    self.width = width
    self.height = height
    self.canvas = Canvas(self, width=width, height=height)
    self._setup_drawing_board()
    self.drawables = []
    # dragging info
    self._drag_data = None
    self.canvas.tag_bind(DRAG_TAG, '<ButtonPress-1>', self._drag_press)
    self.canvas.tag_bind(DRAG_TAG, '<B1-Motion>', self._drag_move)
    self.canvas.tag_bind(DRAG_TAG, '<ButtonRelease-1>', self._drag_release)
    # TODO(mikemeko)
    self._wire_id = None
    self._wire_start = None
    self._wire_end = None
    self.canvas.tag_bind(CONNECTOR_TAG, '<ButtonPress-1>', self._wire_press)
    self.canvas.tag_bind(CONNECTOR_TAG, '<B1-Motion>', self._wire_move)
    self.canvas.tag_bind(CONNECTOR_TAG, '<ButtonRelease-1>',
        self._wire_release)
    self.canvas.tag_bind(ALL, '<ButtonPress-3>', self._delete)
  def _setup_drawing_board(self):
    for x in xrange(0, self.width, BOARD_MARKER_SEPARATION):
      for y in xrange(0, self.height, BOARD_MARKER_SEPARATION):
        create_circle(self.canvas, x, y, BOARD_MARKER_RADIUS, fill=
            BOARD_MARKER_COLOR, outline=BOARD_MARKER_COLOR)
    self.canvas.configure(background=BOARD_BACKGROUND_COLOR)
    self.canvas.pack()
    self.configure(background=BOARD_BACKGROUND_COLOR)
    self.pack()
  def _snap(self, coord):
    return (((coord + BOARD_MARKER_SEPARATION / 2) // BOARD_MARKER_SEPARATION)
        * BOARD_MARKER_SEPARATION)
  def _drawable_at(self, (x, y)):
    for drawable in self.drawables:
      if point_inside_bbox((x,y), drawable.bounding_box):
        return drawable
    return None
  def _connector_at(self, (x, y)):
    for drawable in self.drawables:
      for connector in drawable.connectors:
        cx, cy = connector.center
        if point_inside_circle((x, y), (cx, cy, CONNECTOR_RADIUS)):
          return connector
    return None
  def _wire_with_id(self, canvas_id):
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
    drawable_to_move = self._drawable_at((event.x, event.y))
    if drawable_to_move is not None:
      self._drag_data = (event.x, event.y, drawable_to_move)
  def _drag_move(self, event):
    x, y, drawable_to_move = self._drag_data
    dx, dy = self._snap(event.x - x), self._snap(event.y - y)
    drawable_to_move.move(self.canvas, dx, dy)
    self._drag_data = (x + dx, y + dy, drawable_to_move)
  def _drag_release(self, event):
    self._drag_data = None
  def _draw_current_wire(self):
    if self._wire_id is not None:
      self.canvas.delete(self._wire_id)
    x1, y1 = self._wire_start
    x2, y2 = self._wire_end
    fill = (WIRE_COLOR if self._connector_at(self._wire_end) is not None else
        WIRE_ILLEGAL_COLOR)
    self._wire_id = self.canvas.create_line(x1, y1, x2, y2, fill=fill,
        width=WIRE_WIDTH)
  def _wire_press(self, event):
    self._wire_start = (self._snap(event.x), self._snap(event.y))
  def _wire_move(self, event):
    new_wire_end = (self._snap(event.x), self._snap(event.y))
    if self._wire_end != new_wire_end:
      self._wire_end = new_wire_end
      self._draw_current_wire()
  def _wire_release(self, event):
    if self._wire_id is not None:
      start_connector = self._connector_at(self._wire_start)
      end_connector = self._connector_at(self._wire_end)
      if end_connector is None:
        self.canvas.delete(self._wire_id)
      else:
        wire = Wire(self._wire_id, start_connector, end_connector)
        start_connector.start_wires.add(wire)
        end_connector.end_wires.add(wire)
    self._wire_id = None
    self._wire_start = None
    self._wire_end = None
  def _delete(self, event):
    drawable_to_delete = self._drawable_at((event.x, event.y))
    if drawable_to_delete is not None:
      drawable_to_delete.delete_from(self.canvas)
      return
    connector_to_delete = self._connector_at((event.x, event.y))
    if connector_to_delete is not None:
      connector_to_delete.drawable.delete_from(self.canvas)
      return
    canvas_id = self.canvas.find_closest(event.x, event.y)[0]
    wire_to_delete = self._wire_with_id(canvas_id)
    if wire_to_delete is not None:
      wire_to_delete.delete_from(self.canvas)
  def _draw_connector(self, drawable, x, y):
    canvas_id = create_circle(self.canvas, x, y, CONNECTOR_RADIUS,
        fill=CONNECTOR_COLOR, activewidth=2, tags=CONNECTOR_TAG)
    connector = Connector(canvas_id, (x, y), drawable)
    drawable.connectors.add(connector)
  def add_drawable(self, drawable):
    self.drawables.append(drawable)
    drawable.draw_on(self.canvas)
    for part in drawable.parts:
      self.canvas.itemconfig(part, tags=DRAG_TAG)
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
    self.mainloop()
