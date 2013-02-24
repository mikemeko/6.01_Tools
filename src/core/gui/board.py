"""
GUI tool on which several items may be drawn. Supports dragging the items
    around, connecting the items with wires, deleting items, rotating items,
    and displaying messages.
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
from constants import CTRL_DOWN
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
from constants import SHIFT_DOWN
from constants import WARNING
from core.util.undo import Action
from core.util.undo import Action_History
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
      on_changed=None, on_exit=None, directed_wires=True):
    """
    |width|: the width of this board.
    |height|: the height of this board.
    |on_changed|: a function to call when changed status is reset.
    |on_exit|: a function to call on exit.
    |directed_wires|: if True, wires will be directed (i.e. have arrows).
    """
    Frame.__init__(self, parent, background=BOARD_BACKGROUND_COLOR)
    self.parent = parent
    self.width = width
    self.height = height
    self._on_changed = on_changed
    self._on_exit = on_exit
    self._directed_wires = directed_wires
    # canvas on which items are drawn
    self._canvas = Canvas(self, width=width, height=height,
        highlightthickness=0, background=BOARD_BACKGROUND_COLOR)
    # the drawables on this board, includes deleted drawables
    self._drawables = set()
    # undo / redo
    self._action_history = Action_History()
    # state for dragging
    self._drag_item = None
    self._drag_start_point = None
    self._drag_last_point = None
    # state for drawing wires
    self._wire_parts = None
    self._wire_start = None
    self._wire_end = None
    self._wire_labeler = 0 # used to uniquely label wires
    # state for key-press callbacks
    self._ctrl_pressed = False
    self._shift_pressed = False
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
    self.parent.protocol('WM_DELETE_WINDOW', self.quit)
  def _drawable_at(self, point):
    """
    |point|: a tuple of the form (x, y) indicating a location on the canvas.
    Returns the drawable located at canvas location |point|, or None if no such
        item exists.
    TODO(mikemeko): should return the topmost such drawable.
    """
    for drawable in self.get_drawables():
      if point_inside_bbox(point, drawable.bounding_box(drawable.offset)):
        return drawable
    return None
  def _connector_at(self, point):
    """
    |point|: a tuple of the form (x, y) indicating a location on the canvas.
    Returns the connector located at canvas location |point|, or None if no
        such connector exists.
    TODO(mikemeko): should return the topmost such connector.
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
      for wire in drawable.wires():
        if canvas_id in wire.parts:
          return wire
    return None
  def _update_drawable_offset(self, drawable, dx, dy):
    """
    TODO(mikemeko)
    """
    assert drawable in self._drawables, 'drawable not on board'
    x, y = drawable.offset
    drawable.offset = x + dx, y + dy
  def _move_drawable(self, drawable, dx, dy):
    """
    TODO(mikemeko)
    """
    # mark the board changed if so
    if dx or dy:
      self.set_changed(True)
      # move the item being dragged
      drawable.move(self._canvas, dx, dy)
      # update offset of item being dragged
      self._update_drawable_offset(drawable, dx, dy)
  def _drag_press(self, event):
    """
    Callback for when a drawable item is clicked. Updates drag state.
    """
    self._drag_item = self._drawable_at((event.x, event.y))
    if self._drag_item:
      self._drag_start_point = self._drag_last_point = (event.x, event.y)
  def _drag_move(self, event):
    """
    Callback for when a drawable item is being moved. Updates drag state.
    """
    assert self._drag_item, 'No item being dragged'
    last_x, last_y = self._drag_last_point
    dx = snap(event.x - last_x)
    dy = snap(event.y - last_y)
    self._move_drawable(self._drag_item, dx, dy)
    # update drag state
    self._drag_last_point = (last_x + dx, last_y + dy)
  def _drag_release(self, event):
    """
    Callback for when a drawable item is released. Updates drag state.
    """
    # TODO(mikemeko): comment
    drawable = self._drag_item
    start_x, start_y = self._drag_start_point
    end_x, end_y = self._drag_last_point
    dx = end_x - start_x
    dy = end_y - start_y
    if dx or dy:
      self._action_history.record_action(Action(
          lambda: self._move_drawable(drawable, dx, dy),
          lambda: self._move_drawable(drawable, -dx, -dy),
          'move'))
    # reset
    self._drag_item = None
    self._drag_start_point = None
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
    self._wire_parts = create_wire(self._canvas, x1, y1, x2, y2,
        self._directed_wires)
  def _add_wire(self, wire_parts, start_connector, end_connector, label):
    """
    Creates a Wire object using the given parameters. This method assumes that
        |start_connector| and |end_connector| are connectors on this board and
        that the wire has been drawn on the board with the given |wire_parts|.
        The wire will have the given |label|.
    """
    wire = Wire(wire_parts, start_connector, end_connector, label,
        self._directed_wires)
    wire.redraw(self._canvas)
    start_connector.start_wires.add(wire)
    start_connector.redraw(self._canvas)
    end_connector.end_wires.add(wire)
    end_connector.redraw(self._canvas)
  def _new_wire_label(self):
    """
    Returns a new wire label that has not yet been used.
    """
    label = str(self._wire_labeler)
    self._wire_labeler += 1
    return label
  def _update_labels(self, connector, label):
    """
    If |connector| is a wire connector, this method updates the labels on
        it and on all wires and wire connectors that are connected to it.
    """
    if isinstance(connector.drawable, Wire_Connector_Drawable) and (
        connector.drawable.label is not label):
      connector.drawable.label = label
      for wire in connector.wires():
        if wire.label is not label:
          wire.label = label
          wire.redraw(self._canvas)
          self._update_labels(wire.other_connector(connector), label)
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
        label = self._new_wire_label()
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
        self._update_labels(end_connector, label)
      # create wire
      self._add_wire(self._wire_parts, start_connector, end_connector,
          label)
      # mark the board changed
      self.set_changed(True)
    # reset
    self._wire_parts = None
    self._wire_start = None
    self._wire_end = None
  def add_wire(self, x1, y1, x2, y2, label):
    """
    Adds a wire to this board going from (|x1|, |y1|) to (|x2|, |y2|) and with
        the given |label|. This method assumes that there are connectors on
        this board at the given start and end locations of the wire.
    """
    start_connector = self._connector_at((x1, y1))
    assert start_connector, 'There must be a connector at (x1, y1)'
    end_connector = self._connector_at((x2, y2))
    assert end_connector, 'There must be a connector at (x2, y2)'
    self._add_wire(create_wire(self._canvas, x1, y1, x2, y2,
        self._directed_wires), start_connector, end_connector, label)
    # TODO(mikemeko): this is a temporary bug fix - if externally added wire
    #     (from a saved file) has a higher label, this board should not create
    #     wires that match externally added wire
    if int(label) >= self._wire_labeler:
      self._wire_labeler = int(label) + 1
  def _delete(self, event):
    """
    Callback for deleting an item on the board. Mark the board changed if
        any item is deleted.
    """
    # delete a drawable item?
    drawable_to_delete = self._drawable_at((event.x, event.y))
    if not drawable_to_delete:
      connector_to_delete = self._connector_at((event.x, event.y))
      if connector_to_delete:
        # delete the drawable containing the connector
        drawable_to_delete = connector_to_delete.drawable
    if drawable_to_delete:
      if drawable_to_delete.deletable():
        drawable_to_delete.delete_from(self._canvas)
        self.set_changed(True)
      else:
        self.display_message('Item cannot be deleted', WARNING)
      return
    # delete a wire?
    canvas_id = self._canvas.find_closest(event.x, event.y)[0]
    wire_to_delete = self._wire_with_id(canvas_id)
    if wire_to_delete:
      wire_to_delete.delete_from(self._canvas)
      # may need to relabel the wires, arbitrarily choose start connector
      self._update_labels(wire_to_delete.start_connector,
          self._new_wire_label())
      self.set_changed(True)
  def add_key_binding(self, key, callback, flags=0):
    """
    Adds a key-binding so that whenever |key| is pressed, |callback| is called.
    """
    self._key_press_callbacks[key.lower()] = (callback, flags)
  def _key_press(self, event):
    """
    Callback for when a key is pressed.
    """
    if event.keysym in ('Control_L', 'Control_R'):
      self._ctrl_pressed = True
      self.configure(cursor='pirate')
    elif event.keysym in ('Shift_L', 'Shift_R'):
      self._shift_pressed = True
      self.configure(cursor='exchange')
    elif event.keysym.lower() in self._key_press_callbacks:
      callback, flags = self._key_press_callbacks[event.keysym.lower()]
      if (self._ctrl_pressed or not flags & CTRL_DOWN) and (
          self._shift_pressed or not flags & SHIFT_DOWN):
        callback()
  def _key_release(self, event):
    """
    Callback for when a key is released.
    """
    if event.keysym in ('Control_L', 'Control_R'):
      self.configure(cursor='arrow')
      self._ctrl_pressed = False
    elif event.keysym in ('Shift_L', 'Shift_R'):
      self.configure(cursor='arrow')
      self._shift_pressed = False
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
        offset = drawable_to_rotate.offset
        def switch(remove, add):
          """
          TODO(mikemeko)
          """
          remove.delete_from(self._canvas)
          self._add_drawable(add, offset)
        switch(drawable_to_rotate, rotated_drawable)
        self._action_history.record_action(Action(
            lambda: switch(drawable_to_rotate, rotated_drawable),
            lambda: switch(rotated_drawable, drawable_to_rotate),
            'rotate'))
  def quit(self):
    """
    Callback on exit.
    """
    self._cancel_message_remove_timer()
    if self._on_exit:
      self._on_exit()
    Frame.quit(self)
  def is_duplicate(self, drawable, offset=(0, 0), disregard_location=False):
    """
    Returns True if the exact |drawable| at the given |offset| is already on
        the board, False otherwise. If |disregard_location| is True, |drawable|
        will be considered duplicate if its type is anywhere on the board.
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    bbox = drawable.bounding_box(offset)
    for other in self.get_drawables():
      if (drawable.__class__ == other.__class__ and
          (disregard_location or bbox == other.bounding_box(other.offset))):
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
  def display_message(self, message, message_type=INFO, auto_remove=True):
    """
    Displays the given |message| on the board. |message_type| should be one of
        INFO, WARNING, or ERROR. If |auto_remove| is True, the message is
        automatically removed after a few seconds (duration depends on type of
        message).
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
    if auto_remove:
      self._message_remove_timer = Timer(duration, self.remove_message)
      self._message_remove_timer.start()
  def changed(self):
    """
    Returns True if this board has been changed since the last time the changed
        flag was reset to False.
    """
    return self._changed
  def set_changed(self, changed):
    """
    Sets the changed status of this board.
    """
    assert isinstance(changed, bool), 'changed must be a bool'
    self.remove_message()
    self._changed = changed
    if self._on_changed:
      self._on_changed(changed)
  def _add_drawable(self, drawable, offset):
    """
    TODO(mikemeko)
    """
    # add it to the list of drawables on this board
    self._drawables.add(drawable)
    # TODO(mikemeko)
    drawable.offset = offset
    # draw it
    drawable.draw_on(self._canvas, offset)
    # draw its connectors
    drawable.draw_connectors(self._canvas, offset)
    # attach drag tag
    for part in drawable.parts:
      self._canvas.itemconfig(part, tags=(DRAG_TAG, ROTATE_TAG))
    # mark this board changed
    self.set_changed(True)
    # TODO(mikemeko)
    drawable.set_live()
  def add_drawable(self, drawable, offset=(0, 0)):
    """
    Adds the given |drawable| to this board at the given |offset|.
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    self._add_drawable(drawable, offset)
    # TODO(mikemeko)
    self._action_history.record_action(Action(
        lambda: self._add_drawable(drawable, offset),
        lambda: drawable.delete_from(self._canvas),
        'add_drawable'))
  def get_drawables(self):
    """
    Returns the live drawables on this board.
    """
    for drawable in self._drawables:
      if drawable.is_live():
        yield drawable
  def get_drawable_offset(self, drawable):
    """
    Returns the offset with which the given |drawable| is drawn. Assumes that
        the |drawable| is on this board.
    """
    assert drawable in self._drawables, 'drawable must be on this board'
    return drawable.offset
  def clear(self):
    """
    Removes all drawables from this board.
    """
    for drawable in self.get_drawables():
      drawable.delete_from(self._canvas)
    self._drawables.clear()
  def undo(self):
    """
    TODO(mikemeko)
    """
    self._action_history.undo()
  def redo(self):
    """
    TODO(mikemeko)
    """
    self._action_history.redo()
  def clear_action_history(self):
    """
    TODO(mikemeko)
    """
    self._action_history.clear()
