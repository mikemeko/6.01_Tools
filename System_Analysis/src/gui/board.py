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
from constants import ERROR
from constants import INFO
from constants import MESSAGE_ERROR_COLOR
from constants import MESSAGE_ERROR_DURATION
from constants import MESSAGE_HEIGHT
from constants import MESSAGE_INFO_COLOR
from constants import MESSAGE_INFO_DURATION
from constants import MESSAGE_PADDING
from constants import MESSAGE_TEXT_WIDTH
from constants import MESSAGE_WARNING_COLOR
from constants import MESSAGE_WARNING_DURATION
from constants import MESSAGE_WIDTH
from constants import ROTATE_TAG
from constants import WARNING
from threading import Timer
from Tkinter import ALL
from Tkinter import Canvas
from Tkinter import Frame
from util import create_circle
from util import create_wire
from util import point_inside_bbox
from util import point_inside_circle
from util import snap

class Board(Frame):
  """
  Tkinter Frame that supports drawing and manipulating various items.
  """
  def __init__(self, parent, width=BOARD_WIDTH, height=BOARD_HEIGHT,
      on_exit=None):
    """
    |width|: the width of this board.
    |height|: the height of this board.
    |on_exit|: a function call on exit.
    """
    Frame.__init__(self, parent, background=BOARD_BACKGROUND_COLOR)
    self.parent = parent
    self.width = width
    self.height = height
    self._on_exit = on_exit
    # canvas on which items are drawn
    self._canvas = Canvas(self, width=width, height=height,
        highlightthickness=0, background=BOARD_BACKGROUND_COLOR)
    # the drawables on this board, includes deleted drawables
    self._drawables = set()
    # TODO(mikemeko): consider making offset a Drawable attribute
    self._drawable_offsets = dict()
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
    # state for message display
    self._message_parts = []
    self._message_remove_timer = None
    # state to track whether this board has been changed
    self._changed = False
    # setup ui
    self._setup_drawing_board()
    self._setup_bindings()
  def _setup_drawing_board(self):
    """
    Draws grid lines on the board.
    """
    for dim in xrange(0, self.width, BOARD_GRID_SEPARATION):
      self._canvas.create_line((0, dim, self.width, dim),
          fill=BOARD_MARKER_LINE_COLOR)
      self._canvas.create_line((dim, 0, dim, self.height),
          fill=BOARD_MARKER_LINE_COLOR)
    self._canvas.pack()
    self.pack()
  def _setup_bindings(self):
    """
    Makes all necessary event bindings.
    """
    # drag bindings
    self._canvas.tag_bind(DRAG_TAG, '<ButtonPress-1>', self._drag_press)
    self._canvas.tag_bind(DRAG_TAG, '<B1-Motion>', self._drag_move)
    self._canvas.tag_bind(DRAG_TAG, '<ButtonRelease-1>', self._drag_release)
    # wire drawing bindings
    self._canvas.tag_bind(CONNECTOR_TAG, '<ButtonPress-1>', self._wire_press)
    self._canvas.tag_bind(CONNECTOR_TAG, '<B1-Motion>', self._wire_move)
    self._canvas.tag_bind(CONNECTOR_TAG, '<ButtonRelease-1>',
        self._wire_release)
    # delete binding
    self._canvas.tag_bind(ALL, '<Control-Button-1>', self._delete)
    # key-press and key-release bindings
    self.parent.bind('<KeyPress>', self._key_press)
    self.parent.bind('<KeyRelease>', self._key_release)
    # rotate binding
    self._canvas.tag_bind(ROTATE_TAG, '<Shift-Button-1>', self._rotate)
    # on quit
    self.parent.protocol('WM_DELETE_WINDOW', self._quit)
  def _drawable_at(self, point):
    """
    |point|: a tuple of the form (x, y) indicating a location on the canvas.
    Returns the drawable located at canvas location |point|, or None if no such
        item exists.
    """
    for drawable in self.get_drawables():
      if point_inside_bbox(point, drawable.bounding_box(
          self._drawable_offsets[drawable])):
        return drawable
    return None
  def _connector_at(self, point):
    """
    |point|: a tuple of the form (x, y) indicating a location on the canvas.
    Returns the connector located at canvas location |point|, or None if no
        such connector exists.
    """
    for drawable in self.get_drawables():
      for connector in drawable.connectors:
        cx, cy = connector.center
        if point_inside_circle(point, (cx, cy, CONNECTOR_RADIUS)):
          return connector
    return None
  def _wire_with_id(self, canvas_id):
    """
    Returns the wire with id |canvas_id|, or None if no such wire exists.
    """
    for drawable in self.get_drawables():
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
    if self._drag_item:
      self._drag_last_point = (event.x, event.y)
  def _drag_move(self, event):
    """
    Callback for when a drawable item is being moved. Updates drag state.
    """
    assert self._drag_item, 'No item being dragged'
    last_x, last_y = self._drag_last_point
    dx = snap(event.x - last_x)
    dy = snap(event.y - last_y)
    # mark the board changed if so
    if dx or dy:
      self._set_changed()
    # move the item being dragged
    self._drag_item.move(self._canvas, dx, dy)
    # update drag state
    self._drag_last_point = (last_x + dx, last_y + dy)
    # update offset of item being dragged
    x, y = self._drawable_offsets[self._drag_item]
    self._drawable_offsets[self._drag_item] = x + dx, y + dy
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
        self._canvas.delete(part)
  def _draw_current_wire(self):
    """
    Draws the wire currently being created.
    """
    assert self._wire_start and self._wire_end, 'No wire ends'
    self._erase_previous_wire()
    x1, y1 = self._wire_start
    x2, y2 = self._wire_end
    self._wire_parts = create_wire(self._canvas, x1, y1, x2, y2)
  def _add_wire(self, wire_parts, start_connector, end_connector, label):
    """
    TODO(mikemeko)
    """
    wire = Wire(wire_parts, start_connector, end_connector, label)
    start_connector.start_wires.add(wire)
    start_connector.lift(self._canvas)
    end_connector.end_wires.add(wire)
    end_connector.lift(self._canvas)
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
      self._add_wire(self._wire_parts, start_connector, end_connector,
          label)
      # mark the board changed
      self._set_changed()
    # reset
    self._wire_parts = None
    self._wire_start = None
    self._wire_end = None
  def add_wire(self, x1, y1, x2, y2, label):
    """
    TODO(mikemeko)
    """
    start_connector = self._connector_at((x1, y1))
    assert start_connector, 'There must be a connector at (x1, y1)'
    end_connector = self._connector_at((x2, y2))
    assert end_connector, 'There must be a connector at (x2, y2)'
    self._add_wire(create_wire(self._canvas, x1, y1, x2, y2),
        start_connector, end_connector, label)
  def _delete(self, event):
    """
    Callback for deleting an item on the board. Mark the board changed if
        any item is deleted.
    """
    # delete a drawable item?
    drawable_to_delete = self._drawable_at((event.x, event.y))
    if drawable_to_delete:
      drawable_to_delete.delete_from(self._canvas)
      self._set_changed()
      return
    # delete a connector?
    connector_to_delete = self._connector_at((event.x, event.y))
    if connector_to_delete:
      # delete the drawable containing the connector
      connector_to_delete.drawable.delete_from(self._canvas)
      self._set_changed()
      return
    # delete a wire?
    canvas_id = self._canvas.find_closest(event.x, event.y)[0]
    wire_to_delete = self._wire_with_id(canvas_id)
    if wire_to_delete:
      wire_to_delete.delete_from(self._canvas)
      self._set_changed()
  def add_key_binding(self, key, callback):
    """
    Adds a key-binding so that whenever |key| is pressed, |callback| is called.
    """
    self._key_press_callbacks[key] = callback
  def _key_press(self, event):
    """
    Callback for when a key is pressed.
    """
    if event.keysym in ('Control_L', 'Control_R'):
      self.configure(cursor='pirate')
    elif event.keysym in ('Shift_L', 'Shift_R'):
      self.configure(cursor='exchange')
    elif event.char in self._key_press_callbacks:
      self._key_press_callbacks[event.char]()
  def _key_release(self, event):
    """
    Callback for when a key is released.
    """
    if event.keysym in ('Control_L', 'Control_R', 'Shift_L', 'Shift_R'):
      self.configure(cursor='arrow')
  def _rotate(self, event):
    """
    Callback for item rotation. Marks the board changed if any item is rotated.
    """
    drawable_to_rotate = self._drawable_at((event.x, event.y))
    if drawable_to_rotate:
      # make sure that it is not connected to other drawables
      if any(drawable_to_rotate.wires()):
        self.display_message('Cannot rotate a connected item', ERROR)
        return
      # remove current drawable and add rotated version
      rotated_drawable = drawable_to_rotate.rotated()
      if rotated_drawable is not drawable_to_rotate:
        offset = self._drawable_offsets[drawable_to_rotate]
        drawable_to_rotate.delete_from(self._canvas)
        self.add_drawable(rotated_drawable, offset)
        self._set_changed()
  def _quit(self):
    """
    Callback on exit.
    """
    self._cancel_message_remove_timer()
    if self._on_exit:
      self._on_exit()
    self.parent.quit()
  def is_duplicate(self, drawable, offset=(0, 0)):
    """
    Returns True if the exact |drawable| at the given |offset| is already on
        the board, False otherwise.
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    bbox = drawable.bounding_box(offset)
    for other in self.get_drawables():
      if (drawable.__class__ == other.__class__ and
          bbox == other.bounding_box(self._drawable_offsets[other])):
        return True
    return False
  def _cancel_message_remove_timer(self):
    """
    Cancles timer that has been set to remove current message (if any).
    """
    if self._message_remove_timer:
      self._message_remove_timer.cancel()
      self._message_remove_timer = None
  def remove_message(self):
    """
    Removes the current message on the board, if any.
    """
    self._cancel_message_remove_timer()
    for part in self._message_parts:
      self._canvas.delete(part)
    # clear out message parts list
    self._message_parts = []
  def display_message(self, message, message_type=INFO):
    """
    Displays the given |message| on the board. |message_type| should be one of
        INFO, WARNING, or ERROR.
    """
    # remove current message, if any
    self.remove_message()
    # cancel message remove timer
    self._cancel_message_remove_timer()
    # message container
    if message_type is WARNING:
      fill = MESSAGE_WARNING_COLOR
      duration = MESSAGE_WARNING_DURATION
    elif message_type is ERROR:
      fill = MESSAGE_ERROR_COLOR
      duration = MESSAGE_ERROR_DURATION
    else:
      # default is info
      fill = MESSAGE_INFO_COLOR
      duration = MESSAGE_INFO_DURATION
    self._message_parts.append(self._canvas.create_rectangle((self.width -
        MESSAGE_WIDTH - MESSAGE_PADDING, self.height - MESSAGE_HEIGHT -
        MESSAGE_PADDING, self.width -  MESSAGE_PADDING, self.height -
        MESSAGE_PADDING), fill=fill))
    # message
    self._message_parts.append(self._canvas.create_text(self.width -
        MESSAGE_WIDTH / 2 - MESSAGE_PADDING, self.height - MESSAGE_HEIGHT / 2 -
        MESSAGE_PADDING, text=message, width=MESSAGE_TEXT_WIDTH))
    # close button
    cx, cy = (self.width - MESSAGE_PADDING - 10, self.height -
        MESSAGE_HEIGHT - MESSAGE_PADDING + 10)
    circle = create_circle(self._canvas, cx, cy, 5, fill='white')
    x_1 = self._canvas.create_line(cx - 4, cy - 4, cx + 4, cy + 4)
    x_2 = self._canvas.create_line(cx + 4, cy - 4, cx - 4, cy + 4)
    for close_part in (circle, x_1, x_2):
      self._message_parts.append(close_part)
      self._canvas.tag_bind(close_part, '<Button-1>', lambda event:
          self.remove_message())
    # automatically remove messages after a little while
    self._message_remove_timer = Timer(duration, self.remove_message)
    self._message_remove_timer.start()
  def changed(self):
    """
    Returns True if this board has been changed since the last call to
        reset_changed (or initialization if no such call has been made), False
        otherwise.
    """
    return self._changed
  def reset_changed(self):
    """
    Marks this board unchanged.
    """
    self._set_unchanged()
  def _set_changed(self):
    """
    Sets the changed flag to True.
    """
    self._changed = True
  def _set_unchanged(self):
    """
    Sets the changed flag to False.
    """
    self._changed = False
  def add_drawable(self, drawable, offset=(0, 0)):
    """
    Adds the given |drawable| to this board at the given |offset|.
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    # add it to the list of drawables on this board
    self._drawables.add(drawable)
    self._drawable_offsets[drawable] = offset
    # draw it
    drawable.draw_on(self._canvas, offset)
    # draw its connectors
    drawable.draw_connectors(self._canvas, offset)
    # attach drag tag
    for part in drawable.parts:
      self._canvas.itemconfig(part, tags=(DRAG_TAG, ROTATE_TAG))
    # mark this board changed
    self._set_changed()
  def get_drawables(self):
    """
    Returns the live drawables on this board.
    """
    for drawable in self._drawables:
      if drawable.live():
        yield drawable
  def get_drawable_offset(self, drawable):
    """
    TODO(mikemeko)
    """
    assert drawable in self._drawable_offsets, 'drawable must be on this board'
    return self._drawable_offsets[drawable]
  def clear(self):
    """
    TODO(mikemeko)
    """
    for drawable in self.get_drawables():
      drawable.delete_from(self._canvas)
    self._drawables.clear()
    self._drawable_offsets.clear()
