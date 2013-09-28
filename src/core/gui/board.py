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
from constants import CONNECTOR_WIDTH
from constants import CTRL_CURSOR
from constants import CTRL_DOWN
from constants import DEBUG_CONNECTOR_CENTER_TOOLTIP
from constants import DEBUG_DISPLAY_WIRE_LABELS
from constants import ERROR
from constants import GUIDE_LINE_COLOR
from constants import INFO
from constants import KEYCODE_LOOKUP
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
from constants import SHIFT_CURSOR
from constants import SHIFT_DOWN
from constants import TOOLTIP_DRAWABLE_LABEL_BACKGROUND
from constants import WARNING
from core.undo.undo import Action
from core.undo.undo import Action_History
from core.undo.undo import Multi_Action
from core.util.util import is_callable
from core.util.util import rects_overlap
from find_wire_path_simple import find_wire_path
from sys import platform
from threading import Timer
from time import time
from Tkinter import ALL
from Tkinter import Canvas
from Tkinter import Frame
from tooltip_helper import Tooltip_Helper
from util import create_circle
from util import create_wire
from util import point_inside_bbox
from util import point_inside_circle
from util import snap
from wire_labeling import label_wires

class Board(Frame):
  """
  Tkinter Frame that supports drawing and manipulating various items.
  """
  def __init__(self, parent, width=BOARD_WIDTH, height=BOARD_HEIGHT,
      on_changed=None, on_exit=None, directed_wires=True,
      label_tooltips_enabled=False):
    """
    |width|: the width of this board.
    |height|: the height of this board.
    |on_changed|: a function to call when changed status is reset.
    |on_exit|: a function to call on exit.
    |directed_wires|: if True, wires will be directed (i.e. have arrows).
    |label_tooltips_enabled|: if True, tooltips will show wire and drawable
        labels.
    """
    Frame.__init__(self, parent, background=BOARD_BACKGROUND_COLOR)
    self.parent = parent
    self.width = width
    self.height = height
    self._on_changed = on_changed
    self._on_exit = on_exit
    self._directed_wires = directed_wires
    self._label_tooltips_enabled = label_tooltips_enabled
    # canvas on which items are drawn
    self._canvas = Canvas(self, width=width, height=height,
        highlightthickness=0, background=BOARD_BACKGROUND_COLOR)
    # the drawables on this board, includes deleted drawables
    self._drawables = {}
    # undo / redo
    self._action_history = Action_History()
    # state for button click: dragging or selection or wire drawing
    self._current_button_action = None
    # state for dragging
    self._drag_start_point = None
    self._drag_last_point = None
    # state for selection
    self._selected_drawables = set()
    self._selection_start_point = None
    self._selection_end_point = None
    self._selection_outline_canvas_id = None
    # state for drawing wires
    self._wire_start = None
    self._wire_end = None
    self._wire_parts = []
    # state for key-press callbacks
    self._ctrl_pressed = False
    self._shift_pressed = False
    self._key_press_callbacks = {}
    # state for message display
    self._message_parts = []
    self._message_remove_timer = None
    # state for guide lines
    self._guide_line_parts = []
    # state for grid lines
    self._grid_line_parts = []
    # state to track whether this board has been changed
    self._changed = False
    # state for wire label tooltips
    self._tooltip_helper = Tooltip_Helper(self._canvas)
    if self._label_tooltips_enabled:
      self._show_label_tooltips = False
    # setup ui
    self._setup_drawing_board()
    self._setup_bindings()
  def _setup_drawing_board(self):
    """
    Draws grid lines on the board.
    """
    for dim in xrange(0, self.width, BOARD_GRID_SEPARATION):
      self._grid_line_parts.append(self._canvas.create_line((0, dim,
          self.width, dim), fill=BOARD_MARKER_LINE_COLOR))
      self._grid_line_parts.append(self._canvas.create_line((dim, 0, dim,
          self.height), fill=BOARD_MARKER_LINE_COLOR))
    self._canvas.pack()
    self.pack()
  def _setup_bindings(self):
    """
    Makes all necessary event bindings.
    """
    # drag, selection, and wire drawing bindings
    self._canvas.bind('<ButtonPress-1>', self._canvas_button_press)
    self._canvas.bind('<B1-Motion>', self._canvas_button_move)
    self._canvas.bind('<ButtonRelease-1>', self._canvas_button_release)
    # delete binding
    self._canvas.tag_bind(ALL, '<Control-Button-1>', self._delete)
    # key-press and key-release bindings
    self.parent.bind('<KeyPress>', self._key_press)
    self.parent.bind('<KeyRelease>', self._key_release)
    # rotate binding
    self._canvas.tag_bind(ROTATE_TAG, '<Shift-Button-1>', self._rotate)
    # tooltip binding
    self._canvas.bind('<Motion>', self._maybe_show_tooltip)
    # on quit
    self.parent.protocol('WM_DELETE_WINDOW', self.quit)
  def _drawable_at(self, point):
    """
    |point|: a tuple of the form (x, y) indicating a location on the canvas.
    Returns the drawable located at canvas location |point|, or None if no such
        item exists.
    """
    for drawable in self._get_drawables():
      if point_inside_bbox(point, drawable.bounding_box(drawable.offset)):
        return drawable
    return None
  def _connector_at(self, point):
    """
    |point|: a tuple of the form (x, y) indicating a location on the canvas.
    Returns the connector located at canvas location |point|, or None if no
        such connector exists.
    """
    for drawable in self._get_drawables():
      for connector in drawable.connectors:
        cx, cy = connector.center
        if point_inside_circle(point, (cx, cy, CONNECTOR_RADIUS +
            CONNECTOR_WIDTH + 2)):
          return connector
    return None
  def _wire_with_id(self, canvas_id):
    """
    Returns the wire with id |canvas_id|, or None if no such wire exists.
    """
    for drawable in self._get_drawables():
      for wire in drawable.wires():
        if canvas_id in wire.parts:
          return wire
    return None
  def _update_drawable_offset(self, drawable, dx, dy):
    """
    Updates the offset of the given |drawable| by (|dx|, |dy|). Assumes that
        |drawable| is on this board.
    """
    assert drawable in self._drawables, 'drawable is not on board'
    x, y = drawable.offset
    drawable.offset = x + dx, y + dy
  def _draw_guide_lines(self, points):
    """
    Draws two drawing guide lines (vertical and horizontal) crossing at the
        each of the given |points|.
    """
    # remove previously drawn guide lines
    self._remove_guide_lines()
    # draw new guide lines
    for x, y in points:
      self._guide_line_parts.extend([self._canvas.create_line(x, 0, x,
          self.height, fill=GUIDE_LINE_COLOR), self._canvas.create_line(0, y,
          self.width, y, fill=GUIDE_LINE_COLOR)])
    # lower lines below drawables on the board
    for part in self._guide_line_parts:
      self._canvas.tag_lower(part)
    # lower the grid lines so that they don't mask the guide lines
    for part in self._grid_line_parts:
      self._canvas.tag_lower(part)
  def _remove_guide_lines(self):
    """
    Removes the currently drawn guide lines, if any.
    """
    for part in self._guide_line_parts:
      self._canvas.delete(part)
    self._guide_line_parts = []
  def _move_drawable(self, drawable, dx, dy):
    """
    Moves the given |drawable| by (|dx|, |dy|). Assumes that |drawable| is on
        this board.
    """
    assert drawable in self._drawables, 'drawable is not on board'
    if dx or dy:
      # mark the board changed
      self.set_changed(True)
      # move the drawable on the canvas
      drawable.move(self._canvas, dx, dy)
      # update the drawable's offset
      self._update_drawable_offset(drawable, dx, dy)
  def _empty_current_drawable_selection(self):
    """
    Voids the current selection of drawables, if any.
    """
    if self._selected_drawables:
      # hide all bounding box outlines
      for drawable in self._selected_drawables:
        drawable.hide_selected_highlight(self._canvas)
      self._selected_drawables.clear()
  def _remove_current_selection_outline(self):
    """
    Removes the currently drawn rectangle that shows drawable selection.
    """
    if self._selection_outline_canvas_id is not None:
      self._canvas.delete(self._selection_outline_canvas_id)
      self._selection_outline_canvas_id = None
  def _redraw_selection_outline(self):
    """
    Redraws the rectangle that shows drawable selection.
    """
    assert (self._selection_start_point is not None and
        self._selection_end_point is not None)
    self._remove_current_selection_outline()
    self._selection_outline_canvas_id = self._canvas.create_rectangle(
        self._selection_start_point, self._selection_end_point, fill='',
        outline='red', dash=(3,))
  def _select(self, drawable):
    """
    Selects the given |drawable| by adding it to the set of selected items and
        outlining it to indicate selection.
    """
    drawable.show_selected_highlight(self._canvas)
    self._selected_drawables.add(drawable)
  def _deselect(self, drawable):
    """
    Deselects the given |drawable|, if it had been selected, by removing it from
        the set of selected items and removing the selection outline.
    """
    if drawable in self._selected_drawables:
      self._selected_drawables.remove(drawable)
      drawable.hide_selected_highlight(self._canvas)
  def _drawable_within_board_bounds(self, drawable, offset):
    """
    Returns True if the |drawable| with the given |offset| is completely within
        the bounds of the board (with 1 grid padding), False otherwise.
    """
    x1, y1, x2, y2 = drawable.bounding_box(offset)
    return all(BOARD_GRID_SEPARATION <= x <= self.width - BOARD_GRID_SEPARATION
        for x in (x1, x2)) and all(BOARD_GRID_SEPARATION <= y <= self.height -
        BOARD_GRID_SEPARATION for y in (y1, y2))
  def _move_good_for_selected_drawables(self, dx, dy):
    """
    Returns True if moving the currently selected drawables by (|dx|, |dy|)
        keeps all of the selected drawables within the bounds of the board and
        results in no overlapping drawables, False otherwise.
    """
    unselected_drawables = set(self._get_drawables()) - self._selected_drawables
    for drawable in self._selected_drawables:
      ox, oy = self.get_drawable_offset(drawable)
      new_offset = (ox + dx, oy + dy)
      # check that this drawable is within the board bounds
      if not self._drawable_within_board_bounds(drawable, new_offset):
        return False
      # check that this drawable does not overlap other drawables
      new_bbox = drawable.bounding_box(new_offset)
      for other_drawable in unselected_drawables:
        if rects_overlap(new_bbox, other_drawable.bounding_box(
            self.get_drawable_offset(other_drawable))):
          return False
    return True
  def _drag_press(self, event):
    """
    Callback for button press for dragging.
    """
    selected_drawable = self._drawable_at((event.x, event.y))
    assert selected_drawable
    # if this drawable is not one of the currently selected drawables, clear
    #     current selection
    if selected_drawable not in self._selected_drawables:
      self._empty_current_drawable_selection()
    # select this drawable
    self._select(selected_drawable)
    # record drag state
    self._drag_start_point = self._drag_last_point = (event.x, event.y)
  def _drag_move(self, event):
    """
    Callback for button move for dragging.
    """
    # there better be drawables to drag on call to this callback
    assert self._selected_drawables and self._drag_last_point is not None
    # if there's only one drawable being dragged, show guide lines
    if len(self._selected_drawables) == 1:
      drawable = iter(self._selected_drawables).next()
      x1, y1, x2, y2 = drawable.bounding_box(self.get_drawable_offset(drawable))
      self._draw_guide_lines([(x1, y1), (x2, y2)])
    last_x, last_y = self._drag_last_point
    # drag movement amount
    dx = snap(event.x - last_x)
    dy = snap(event.y - last_y)
    if self._move_good_for_selected_drawables(dx, dy):
      # move each of the selected drawables
      for drawable in self._selected_drawables:
        self._move_drawable(drawable, dx, dy)
      # update drag last point
      self._drag_last_point = (last_x + dx, last_y + dy)
  def _drag_release(self, event):
    """
    Callback for button release for dragging.
    """
    assert (self._drag_start_point is not None and self._drag_last_point is not
        None)
    sx, sy = self._drag_start_point
    ex, ey = self._drag_last_point
    dx, dy = ex - sx, ey - sy
    if dx or dy:
      # record movement action for undo / redo
      self._action_history.record_action(Multi_Action(map(lambda drawable:
          Action(lambda: self._move_drawable(drawable, dx, dy),
          lambda: self._move_drawable(drawable, -dx, -dy), 'move'),
          self._selected_drawables), 'moves'))
    # remove guide lines if shown
    self._remove_guide_lines()
    # reset
    self._drag_start_point = None
    self._drag_last_point = None
  def _select_press(self, event):
    """
    Callback for button press for selection.
    """
    # empty current selection
    self._empty_current_drawable_selection()
    # record selection start point
    self._selection_start_point = (snap(event.x), snap(event.y))
  def _select_move(self, event):
    """
    Callback for button move for selection.
    """
    assert self._selection_start_point
    # redraw selection rectangle
    self._selection_end_point = (snap(event.x), snap(event.y))
    self._redraw_selection_outline()
    # outline each of the overlapping drawables
    sx, sy = self._selection_start_point
    ex, ey = self._selection_end_point
    selection_bbox = (min(sx, ex), min(sy, ey), max(sx, ex), max(sy, ey))
    for drawable in self._get_drawables():
      if rects_overlap(drawable.bounding_box(self.get_drawable_offset(
          drawable)), selection_bbox):
        self._select(drawable)
      else:
        self._deselect(drawable)
  def _select_release(self, event):
    """
    Callback for button release for selection.
    """
    # remove selection rectangle
    self._remove_current_selection_outline()
    # reset
    self._selection_start_point = None
    self._selection_end_point = None
  def _erase_previous_wire_path(self):
    """
    Erases the previous version (if any) of the wire path currently being drawn.
    """
    for start, end, parts in self._wire_parts:
      for part in parts:
        self._canvas.delete(part)
    self._wire_parts = []
  def _draw_wire(self, start, end):
    """
    Draws a wire from |start| to |end|. Updates wire data. Does nothing if the
        |start| and |end| are identical.
    """
    if start != end:
      x1, y1 = start
      x2, y2 = end
      self._wire_parts.append([start, end, create_wire(self._canvas, x1, y1, x2,
          y2, self._directed_wires)])
  def _add_wire(self, wire_parts, start_connector, end_connector):
    """
    Creates a Wire object using the given parameters. This method assumes that
        |start_connector| and |end_connector| are connectors on this board and
        that the wire has been drawn on the board with the given |wire_parts|.
    """
    wire = Wire(wire_parts, start_connector, end_connector,
        self._directed_wires)
    def add_wire():
      """
      Adds the wire to the board.
      """
      start_connector.start_wires.add(wire)
      start_connector.redraw(self._canvas)
      # in case the end_connector was created for the purpose of this wire,
      # set it live since it will have been deleted on undo
      # see self._wire_release
      if isinstance(end_connector.drawable, Wire_Connector_Drawable):
        end_connector.drawable.set_live()
      end_connector.end_wires.add(wire)
      end_connector.redraw(self._canvas)
    # do add wire
    add_wire()
    self._action_history.record_action(Action(add_wire,
        lambda: wire.delete_from(self._canvas), 'wire'))
  def _wire_press(self, event):
    """
    Callback for when a connector is pressed to start creating a wire.
    """
    self._empty_current_drawable_selection()
    self._wire_start = (snap(event.x), snap(event.y))
    # if there isn't a connector at wire start, or if that connector is
    #     disabled, don't allow drawing wire
    start_connector = self._connector_at(self._wire_start)
    if not start_connector or not start_connector.enabled:
      self._wire_start = None
  def _wire_move(self, event):
    """
    Callback for when a wire is changed while being created.
    """
    if self._wire_start:
      wire_end = (snap(event.x), snap(event.y))
      if wire_end != self._wire_end:
        self._wire_end = wire_end
        # erase previous wire path
        self._erase_previous_wire_path()
        # find new wire path
        wire_path = find_wire_path(self, self._wire_start, wire_end)
        # draw wires
        for i in xrange(len(wire_path) - 1):
          self._draw_wire(wire_path[i], wire_path[i + 1])
  def _wire_release(self, event):
    """
    Callback for when wire creation is complete.
    """
    if self._wire_parts:
      for start, end, parts in self._wire_parts:
        for point in (start, end):
          if not self._connector_at(point):
            self._add_drawable(Wire_Connector_Drawable(), point)
        start_connector = self._connector_at(start)
        end_connector = self._connector_at(end)
        # create wire
        self._add_wire(parts, start_connector, end_connector)
      if len(self._wire_parts) > 1:
        self._action_history.combine_last_n(len(self._wire_parts))
      # mark the board changed
      self.set_changed(True)
    # reset
    self._wire_start = None
    self._wire_end = None
    self._wire_parts = []
  def _canvas_button_press(self, event):
    """
    Callback for button press.
    """
    assert self._current_button_action is None
    connector = self._connector_at((event.x, event.y))
    drawable = self._drawable_at((event.x, event.y))
    if connector or (drawable and isinstance(drawable,
        Wire_Connector_Drawable)):
      if DEBUG_CONNECTOR_CENTER_TOOLTIP:
        if not connector:
          connector = iter(drawable.connectors).next()
        x, y = connector.center
        self._tooltip_helper.show_tooltip(x, y, str(connector.center))
      self._current_button_action = 'wire'
      self._wire_press(event)
    elif drawable:
      self._current_button_action = 'drag'
      self._drag_press(event)
    else:
      self._current_button_action = 'select'
      self._select_press(event)
  def _canvas_button_move(self, event):
    """
    Callback for button move.
    """
    assert self._current_button_action
    if self._current_button_action == 'wire':
      self._wire_move(event)
    elif self._current_button_action == 'drag':
      self._drag_move(event)
    elif self._current_button_action == 'select':
      self._select_move(event)
    else:
      # should never get here
      raise Exception('Unexpected current button action')
  def _canvas_button_release(self, event):
    """
    Callback for button release.
    """
    assert self._current_button_action
    if self._current_button_action == 'wire':
      self._tooltip_helper.hide_tooltip()
      self._wire_release(event)
    elif self._current_button_action == 'drag':
      self._drag_release(event)
    elif self._current_button_action == 'select':
      self._select_release(event)
    else:
      # should never get here
      raise Exception('Unexpected current button action')
    self._current_button_action = None
  def add_wire(self, x1, y1, x2, y2):
    """
    Adds a wire to this board going from (|x1|, |y1|) to (|x2|, |y2|). This
        method assumes that there are enabled connectors on this board at the
        given start and end locations of the wire.
    """
    start_connector = self._connector_at((x1, y1))
    assert start_connector and start_connector.enabled, ('There must be an '
        'enabled connector at (%d, %d)' % (x1, y1))
    end_connector = self._connector_at((x2, y2))
    assert end_connector and end_connector.enabled, ('There must be an enabled'
        ' connector at (%d, %d)' % (x2, y2))
    self._add_wire(create_wire(self._canvas, x1, y1, x2, y2,
        self._directed_wires), start_connector, end_connector)
  def _delete(self, event):
    """
    Callback for deleting an item on the board. Marks the board changed if
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
        self._action_history.record_action(drawable_to_delete.delete_from(
            self._canvas))
        self.set_changed(True)
      else:
        self.display_message('Item cannot be deleted', WARNING)
      return
    # delete a wire?
    canvas_id = self._canvas.find_closest(event.x, event.y)[0]
    wire_to_delete = self._wire_with_id(canvas_id)
    if wire_to_delete:
      self._action_history.record_action(wire_to_delete.delete_from(
          self._canvas))
      self.set_changed(True)
  def add_key_binding(self, key, callback, flags=0):
    """
    Adds a key-binding so that whenever |key| is pressed, |callback| is called.
    """
    assert is_callable(callback), 'callback must be callable'
    self._key_press_callbacks[(key.lower(), flags)] = callback
  def _move_selected_items(self, dx, dy):
    """
    Moves the currently selected items by |dx| in the x-direction and |dy| in
        the y-direction.
    """
    if self._selected_drawables and (dx or dy) and (
        self._move_good_for_selected_drawables(dx, dy)):
      for drawable in self._selected_drawables:
        self._move_drawable(drawable, dx, dy)
      self._action_history.record_action(Multi_Action(map(lambda drawable:
          Action(lambda: self._move_drawable(drawable, dx, dy),
          lambda: self._move_drawable(drawable, -dx, -dy), 'move'),
          self._selected_drawables), 'move selected'))
      self.set_changed(True)
  def _delete_selected_items(self):
    """
    Deletes the currently selected items.
    """
    if self._selected_drawables:
      if all([drawable.deletable() for drawable in self._selected_drawables]):
        self._action_history.record_action(Multi_Action([drawable.delete_from(
            self._canvas) for drawable in self._selected_drawables if
            drawable.is_live()], 'delete selected'))
        self.set_changed(True)
      else:
        self.display_message('At least one of the selected items cannot be '
            'deleted', WARNING)
  def _get_keysym(self, event):
    """
    Returns the appropriate keysym for the given |event|, making the appropriate
        lookup for macs.
    """
    if event.keysym_num == 0 and platform == 'darwin' and (event.keycode in
        KEYCODE_LOOKUP):
      return KEYCODE_LOOKUP[event.keycode]
    else:
      return event.keysym
  def _key_press(self, event):
    """
    Callback for when a key is pressed.
    """
    keysym = self._get_keysym(event)
    if keysym in ('Control_L', 'Control_R'):
      self._ctrl_pressed = True
      self._canvas.configure(cursor=CTRL_CURSOR)
    elif keysym in ('Shift_L', 'Shift_R'):
      self._shift_pressed = True
      self._canvas.configure(cursor=SHIFT_CURSOR)
    elif keysym == 'Down':
      self._move_selected_items(0, BOARD_GRID_SEPARATION)
    elif keysym == 'Left':
      self._move_selected_items(-BOARD_GRID_SEPARATION, 0)
    elif keysym == 'Right':
      self._move_selected_items(BOARD_GRID_SEPARATION, 0)
    elif keysym == 'Up':
      self._move_selected_items(0, -BOARD_GRID_SEPARATION)
    elif keysym in ('BackSpace', 'Delete'):
      # delete selected items as long there is not text edit in progress
      if not self._canvas.focus():
        self._delete_selected_items()
    else:
      current_key = event.keysym.lower()
      current_flags = (CTRL_DOWN * self._ctrl_pressed) | (SHIFT_DOWN &
          self._shift_pressed)
      if (current_key, current_flags) in self._key_press_callbacks:
        self._key_press_callbacks[(current_key, current_flags)]()
  def _key_release(self, event):
    """
    Callback for when a key is released.
    """
    keysym = self._get_keysym(event)
    if keysym in ('Control_L', 'Control_R'):
      self._ctrl_pressed = False
      self._canvas.configure(cursor='arrow')
    elif keysym in ('Shift_L', 'Shift_R'):
      self._shift_pressed = False
      self._canvas.configure(cursor='arrow')
  def _rotate(self, event):
    """
    Callback for item rotation. Marks the board changed if any item is rotated.
    """
    drawable_to_rotate = self._drawable_at((event.x, event.y))
    if drawable_to_rotate:
      # make sure that it is not connected to other drawables
      if any(drawable_to_rotate.wires()):
        self.display_message('Cannot rotate a connected item', WARNING)
        return
      # remove current drawable and add rotated version
      rotated_drawable = drawable_to_rotate.rotated()
      if rotated_drawable is drawable_to_rotate:
        self.display_message('Item cannot be rotated', WARNING)
      else:
        # save offset for undo / redo
        offset = drawable_to_rotate.offset
        def switch(remove, add):
          """
          Removes |remove| and adds |add|.
          """
          remove.delete_from(self._canvas)
          self._add_drawable(add, offset)
        # do rotation
        switch(drawable_to_rotate, rotated_drawable)
        self._action_history.record_action(Action(
            lambda: switch(drawable_to_rotate, rotated_drawable),
            lambda: switch(rotated_drawable, drawable_to_rotate), 'rotate'))
  def _maybe_show_tooltip(self, event):
    """
    If the cursor is on a wire or wire connector, and we are showing wire
        labels, displays a tooltip of the wire label close to the cursor.
        If the cursor is on a drawable, displays a tooltip of the drawable
        label.
    """
    if self._label_tooltips_enabled and self._show_label_tooltips:
      # check if the cursor is on a wire connector
      connector = self._connector_at((event.x, event.y))
      if connector:
        if isinstance(connector.drawable, Wire_Connector_Drawable):
          wires = list(connector.wires())
          if wires:
            self._tooltip_helper.show_tooltip(event.x, event.y, wires[0].label)
        return
      drawable = self._drawable_at((event.x, event.y))
      if drawable:
        if not isinstance(drawable, Wire_Connector_Drawable):
          self._tooltip_helper.show_tooltip(event.x, event.y, drawable.label,
              background=TOOLTIP_DRAWABLE_LABEL_BACKGROUND)
        return
      # check if the cursor is on a wire
      canvas_id = self._canvas.find_closest(event.x, event.y)[0]
      wire = self._wire_with_id(canvas_id)
      if wire:
        self._tooltip_helper.show_tooltip(event.x, event.y, wire.label)
      else:
        self._tooltip_helper.hide_tooltip()
  def quit(self):
    """
    Callback on exit.
    """
    self._cancel_message_remove_timer()
    if self._on_exit:
      self._on_exit()
    Frame.quit(self)
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
    # message container
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
  def set_changed(self, changed, action=None):
    """
    Sets the changed status of this board, and records an |action| if given.
    """
    assert isinstance(changed, bool), 'changed must be a bool'
    self._changed = changed
    if action:
      self._action_history.record_action(action)
    if self._on_changed:
      self._on_changed(changed)
    # remove message since an action has resulted in a board change
    self.remove_message()
    # once the board is changed, don't show wire label tooltips
    self.hide_label_tooltips()
  def _add_drawable(self, drawable, offset):
    """
    Adds the given |drawable| at the given |offset|.
    """
    if drawable in self._drawables:
      # if this drawable had been on the board, it must have been deleted
      assert not drawable.is_live()
      # set it back alive
      drawable.set_live()
      # redraw it on the canvas
      drawable.redraw(self._canvas)
      # mark this board changed
      self.set_changed(True)
    else:
      # add it to the set of drawables on this board
      self._drawables[drawable] = time()
      # set drawable offset (hacky, but convenient storage)
      drawable.offset = offset
      # draw it
      drawable.draw_on(self._canvas, offset)
      # draw its connectors
      drawable.draw_connectors(self._canvas, offset)
      # attach drag tag
      drawable.attach_tags(self._canvas)
      # mark this board changed
      self.set_changed(True)
  def _offset_good_for_new_drawable(self, new_drawable, offset):
    """
    Returns True if the given |new_drawable| at the given |offset| is completely
        within the bounds of the baord, and does not overlap with any of the
        drawables currently on the board, False otherwise.
    """
    # check that the drawable fits inside the board
    if not self._drawable_within_board_bounds(new_drawable, offset):
      return False
    # check that the drawable does not overlap with the current drawables
    bbox = new_drawable.bounding_box(offset)
    for other_drawable in self._get_drawables():
      if rects_overlap(bbox, other_drawable.bounding_box(
          self.get_drawable_offset(other_drawable))):
        return False
    return True
  def add_drawable(self, drawable, desired_offset=(0, 0)):
    """
    Adds the given |drawable| to this board at the closest offset to the given
        |desired_offset| so that this new |drawable| does not overlap with any
        other drawables already on the board. Records the action in the action
        history.
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    # get rid of current drawable selection
    self._empty_current_drawable_selection()
    # find a good offset as close to |desired_offset| as possible
    offset = None
    if self._offset_good_for_new_drawable(drawable, desired_offset):
      offset = desired_offset
    else:
      ox, oy = desired_offset
      def closest_offset():
        for d in xrange(BOARD_GRID_SEPARATION, max(ox, self.width - ox) + max(
              oy, self.height - oy) + 1, BOARD_GRID_SEPARATION):
          for i in xrange(0, d + 1, BOARD_GRID_SEPARATION):
            for dx, dy in set([(i, d - i), (i, i - d), (-i, d - i),
                  (-i, i - d)]):
              test_offset = (ox + dx, oy + dy)
              if self._offset_good_for_new_drawable(drawable, test_offset):
                return test_offset
      offset = closest_offset()
    # if we found a good offset, add the drawable at that offset and select it,
    #     otherwise show an error message
    if offset is not None:
      self._add_drawable(drawable, offset)
      self._select(drawable)
      self._action_history.record_action(Action(
          lambda: drawable.redraw(self._canvas),
          lambda: drawable.delete_from(self._canvas), 'add_drawable'))
    else:
      self.display_message('There\'s no more space :(', ERROR)
  def _label_drawables(self):
    """
    Labels the drawables (other than Wire_Connector_Drawables) on the board in
        the order in which they were added to the board.
    """
    for i, drawable in enumerate(sorted(filter(lambda drawable:
        drawable.is_live() and not isinstance(drawable,
        Wire_Connector_Drawable), self._drawables), key=lambda drawable:
        self._drawables[drawable])):
      drawable.label = str(i)
  def _get_drawables(self):
    """
    Returns a generator of the live drawables on this board in the reverse
        order in which they were put on the board, newest drawable first.
    """
    for drawable in sorted(self._drawables, key=lambda drawable:
        -self._drawables[drawable]):
      if drawable.is_live():
        yield drawable
  def get_drawables(self):
    """
    Labels the wires and drawables and then returns a generator of the live
        drawables on this board, with the newest drawables put first.
    """
    label_wires(self._get_drawables())
    self._label_drawables()
    return self._get_drawables()
  def show_label_tooltips(self):
    """
    Starts showing label tooltips. Tooltips will be hidden on call to
        self.hide_label_tooltips or if the board is changed.
    Label tooltips must be enabled for this board.
    """
    assert self._label_tooltips_enabled, 'label tooltips are not enabled'
    self._show_label_tooltips = True
  def hide_label_tooltips(self):
    """
    Stops showing label tooltips.
    """
    if self._label_tooltips_enabled:
      self._tooltip_helper.hide_tooltip()
      self._show_label_tooltips = False
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
    for drawable in self._get_drawables():
      drawable.delete_from(self._canvas)
    self._drawables.clear()
  def undo(self):
    """
    Undoes the last action that was done, where an action is one of: adding a
        drawable, deleting a drawable, moving a drawable, rotating a drawable,
        and deleting a wire.
    """
    if self._action_history.undo():
      self.set_changed(True)
  def redo(self):
    """
    Does the last action that was undone
    """
    if self._action_history.redo():
      self.set_changed(True)
  def clear_action_history(self):
    """
    Clears the action history.
    """
    self._action_history.clear()
  def reset_cursor_state(self):
    """
    Clears any recorded key press state and returns to original cursor look.
    """
    self._ctrl_pressed = False
    self._shift_pressed = False
    self.configure(cursor='arrow')
  def reset(self):
    """
    Resets this board by clearing the action history, setting the board to be
        unchanged, and clearing any recorded key press state.
    """
    # clear board undo / redo history
    self.clear_action_history()
    # mark the board unchanged
    self.set_changed(False)
    # return cursor to normal state
    self.reset_cursor_state()
