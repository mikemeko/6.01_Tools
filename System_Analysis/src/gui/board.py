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
    self.parent = parent
    self.width = width
    self.height = height
    # canvas on which items are drawn
    self.canvas = Canvas(self, width=width, height=height,
        highlightthickness=0, background=BOARD_BACKGROUND_COLOR)
    # the drawables on this board
    self.drawables = set()
    # TODO(mikemeko): consider making offset a Drawable attribute
    self.drawable_offsets = dict()
    # state for dragging
    self._drag_item = None
    self._drag_last_point = None
    # state for drawing wires
    self._wire_parts = None
    self._wire_start = None
    self._wire_end = None
    self._wire_labeler = 0 # used to uniquely label wires
    # state for key-press callbacks
    self._key_press_callbacks = {}
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
    # wire drawing bindings
    self.canvas.tag_bind(CONNECTOR_TAG, '<ButtonPress-1>', self._wire_press)
    self.canvas.tag_bind(CONNECTOR_TAG, '<B1-Motion>', self._wire_move)
    self.canvas.tag_bind(CONNECTOR_TAG, '<ButtonRelease-1>',
        self._wire_release)
    # delete binding
    self.canvas.tag_bind(ALL, '<ButtonPress-3>', self._delete)
    # key-press binding
    self.parent.bind('<Key>', self._handle_key_press)
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
        cx, cy = connector.center
        if point_inside_circle(point, (cx, cy, CONNECTOR_RADIUS)):
          return connector
    return None
  def _wire_with_id(self, canvas_id):
    """
    Returns the wire with id |canvas_id|, or None if no such wire exists.
    """
    for drawable in self.drawables:
      for connector in drawable.connectors:
        for wire in connector.wires():
          if canvas_id in wire.parts:
            return wire
    return None
  def _drag_press(self, event):
    """
    Callback for when a drawable item is clicked. Updates drag state.
    """
    self._drag_item = self._drawable_at((event.x, event.y))
    assert self._drag_item, 'No item being dragged'
    self._drag_last_point = (event.x, event.y)
  def _drag_move(self, event):
    """
    Callback for when a drawable item is being moved. Updates drag state.
    """
    assert self._drag_item, 'No item being dragged'
    last_x, last_y = self._drag_last_point
    dx = snap(event.x - last_x)
    dy = snap(event.y - last_y)
    # move the item being dragged
    self._drag_item.move(self.canvas, dx, dy)
    # update drag state
    self._drag_last_point = (last_x + dx, last_y + dy)
    # update offset of item being dragged
    x, y = self.drawable_offsets[self._drag_item]
    self.drawable_offsets[self._drag_item] = x + dx, y + dy
  def _drag_release(self, event):
    """
    Callback for when a drawable item is released. Updates drag state.
    """
    # reset
    self._drag_item = None
    self._drag_last_point = None
  def _straighten_wire(self):
    """
    Ensures that the wire currently being drawn is horizontal or vertical.
    """
    assert self._wire_start and self._wire_end, 'No wire ends'
    x1, y1 = self._wire_start
    x2, y2 = self._wire_end
    if abs(x2 - x1) > abs(y2 - y1):
      self._wire_end = (x2, y1)
    else:
      self._wire_end = (x1, y2)
  def _erase_previous_wire(self):
    """
    Erases the previous version (if any) of the wire currently being drawn.
    """
    if self._wire_parts:
      for part in self._wire_parts:
        self.canvas.delete(part)
  def _draw_current_wire(self):
    """
    Draws the wire currently being created.
    """
    assert self._wire_start and self._wire_end, 'No wire ends'
    self._erase_previous_wire()
    x1, y1 = self._wire_start
    x2, y2 = self._wire_end
    self._wire_parts = create_wire(self.canvas, x1, y1, x2, y2)
  def _wire_press(self, event):
    """
    Callback for when a connector is pressed to start creating a wire. Updates
        wire data.
    """
    self._wire_start = (snap(event.x), snap(event.y))
    # if there isn't a connector at wire start, don't allow drawing wire
    if not self._connector_at(self._wire_start):
      self._wire_start = None
      self._erase_previous_wire()
  def _wire_move(self, event):
    """
    Callback for when a wire is changed while being created. Updates wire data.
    """
    if self._wire_start:
      self._wire_end = (snap(event.x), snap(event.y))
      self._straighten_wire()
      self._draw_current_wire()
  def _wire_release(self, event):
    """
    Callback for when wire creation is complete. Updates wire data.
    Appropriately updates wire labels.
    """
    if self._wire_parts:
      start_connector = self._connector_at(self._wire_start)
      # find a label for the new wire
      if isinstance(start_connector.drawable, Wire_Connector_Drawable):
        # if drawing off of a wire connector, use its label for the new wire
        label = start_connector.drawable.label
      else:
        # if drawing off of an item, assign a new label to the new wire
        label = str(self._wire_labeler)
        self._wire_labeler += 1
      end_connector = self._connector_at(self._wire_end)
      if not end_connector:
        # if no end connector is found when wire drawing is complete, then
        # create a wire connector at the end of the new wire
        wire_connector_drawable = Wire_Connector_Drawable(label)
        # setup offset in an intuitive place based on how the wire was drawn
        self.add_drawable(wire_connector_drawable, self._wire_end)
        end_connector = self._connector_at(self._wire_end)
      elif isinstance(end_connector.drawable, Wire_Connector_Drawable):
        # if an end connector is found, and it is a wire connector, we need to
        # update the labels of all wires and wire connectors attached to it
        def update_labels(connector):
          """
          If |connector| is a wire connector, this method updates the labels on
          it, the wires that start at it, and all following wire connectors.
          """
          if isinstance(connector.drawable, Wire_Connector_Drawable):
            connector.drawable.label = label
            for wire in connector.start_wires:
              wire.label = label
              update_labels(wire.end_connector)
        update_labels(end_connector)
      # create wire
      wire = Wire(self._wire_parts, start_connector, end_connector, label)
      start_connector.start_wires.add(wire)
      start_connector.lift(self.canvas)
      end_connector.end_wires.add(wire)
      end_connector.lift(self.canvas)
    # reset
    self._wire_parts = None
    self._wire_start = None
    self._wire_end = None
  def _delete_drawable(self, drawable):
    """
    Deletes the given |drawable| from the board.
    """
    drawable.delete_from(self.canvas)
    self.drawables.remove(drawable)
    del self.drawable_offsets[drawable]
  def _maybe_delete_empty_wire_connector(self, connector):
    """
    Deletes |connector| if it is a wire connector and it is not connected to
        any wires.
    """
    if connector.num_wires() is 0 and isinstance(connector.drawable,
        Wire_Connector_Drawable):
      self._delete_drawable(connector.drawable)
  def _delete(self, event):
    """
    Callback for deleting an item on the board.
    """
    # delete a drawable item?
    drawable_to_delete = self._drawable_at((event.x, event.y))
    if drawable_to_delete:
      self._delete_drawable(drawable_to_delete)
      return
    # delete a connector?
    connector_to_delete = self._connector_at((event.x, event.y))
    if connector_to_delete:
      # delete the drawable containing the connector
      self._delete_drawable(connector_to_delete.drawable)
      return
    # delete a wire?
    canvas_id = self.canvas.find_closest(event.x, event.y)[0]
    wire_to_delete = self._wire_with_id(canvas_id)
    if wire_to_delete:
      wire_to_delete.delete_from(self.canvas)
      # if the wire's start and end connectors are wire connectors, maybe
      # delete them
      self._maybe_delete_empty_wire_connector(wire_to_delete.start_connector)
      self._maybe_delete_empty_wire_connector(wire_to_delete.end_connector)
  def add_key_binding(self, key, callback):
    """
    TODO(mikemeko)
    """
    # TODO(mikemeko): check conditions on key
    self._key_press_callbacks[key] = callback
  def _handle_key_press(self, event):
    """
    TODO(mikemeko)
    """
    # Consider logging stuff
    if event.char in self._key_press_callbacks:
      self._key_press_callbacks[event.char]()
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
