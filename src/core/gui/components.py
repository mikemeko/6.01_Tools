"""
The things that may exist on a board: drawable items, connectors, and wires.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import CONNECTOR_BOTTOM
from constants import CONNECTOR_CENTER
from constants import CONNECTOR_COLOR
from constants import CONNECTOR_EMPTY_COLOR
from constants import CONNECTOR_LEFT
from constants import CONNECTOR_RADIUS
from constants import CONNECTOR_RIGHT
from constants import CONNECTOR_TOP
from constants import DISPLAY_WIRE_LABELS
from constants import DRAG_TAG
from constants import ROTATE_TAG
from constants import RUN_RECT_FILL
from constants import RUN_RECT_OUTLINE
from constants import RUN_RECT_SIZE
from constants import RUN_TEXT_ACTIVE_FILL
from constants import RUN_TEXT_FILL
from core.save.constants import RE_INT_PAIR
from core.undo.undo import Action
from core.undo.undo import Multi_Action
from re import match
from util import create_connector
from util import create_wire
from util import snap

class Drawable:
  """
  An abstract class to represent an item that is drawn on the board. All
      subclasses should impement the draw_on method with appropriate look for
      the drawable, and the serialize and deserialize methods for file saving.
  """
  def __init__(self, width, height, connector_flags=0):
    """
    |width|: the width of this item.
    |height|: the height of this item.
    |connector_flags|: an indicator for the places where this item should have
        connectors. For example: CONNECTOR_TOP | CONNECTOR_RIGHT.
    """
    self.width = width
    self.height = height
    self.connector_flags = connector_flags
    # canvas ids for the parts on this item, should updated by draw_on
    self.parts = set()
    # connectors on this item, updated by board
    self.connectors = set()
    # flag for whether this drawable is on the board / deleted
    self._live = True
  @property
  def draw_on(self, canvas, offset):
    """
    Draws the parts of this item on the |canvas| at the given |offset|. Should
        add the canvas ids of all drawn objects to self.parts.
    All subclasses should implement this.
    """
    raise NotImplementedError('subclasses should implement this')
  def rotated(self):
    """
    Returns a rotated version of this drawable. On a board, Shift-click will
        result in this rotation. The default implementation is no rotation.
    """
    return self
  @property
  def serialize(self, offset):
    """
    Should return a string representation of this drawable at the given
        |offset|. Will typically contain a special marker for the specific type
        of Drawable.
    All subclasses should implement this.
    """
    raise NotImplementedError('subclasses should implement this')
  @property
  @staticmethod
  def deserialize(item_str, board):
    """
    If possible, deserializes |item_str| and adds the appropriate Drawable to
        the given |board|. Should return True on success and False on failure.
    All subclasses should implement this.
    """
    raise NotImplementedError('subclasses should implement this')
  def is_live(self):
    """
    Returns True if this drawable is still on the board, or False if it has
        been deleted.
    """
    return self._live
  def set_live(self):
    """
    Sets (or resets) this drawable to be live. This is usefull for undo / redo.
    """
    self._live = True
  def deletable(self):
    """
    Returns True if user is allowed to delete this drawable, False otherwise.
    Default is True.
    """
    return True
  def bounding_box(self, offset=(0, 0)):
    """
    Returns the bounding box of this Drawable, when drawn with the given
        |offset|.
    """
    x1, y1 = offset
    x2, y2 = x1 + self.width, y1 + self.height
    return x1, y1, x2, y2
  def _draw_connector(self, canvas, point):
    """
    |point|: a tuple of the form (x, y) indicating where the connecter should
        be drawn.
    Draws and returns a connector for this Drawable at the indicated |point|.
    """
    x, y = map(snap, point)
    connector = Connector(create_connector(canvas, x, y), (x, y), self)
    self.connectors.add(connector)
    return connector
  def draw_connectors(self, canvas, offset=(0, 0)):
    """
    Draws the connectors for this Drawable on the given |canvas|, with the
        Drawable drawn with the given |offset|. For specially located
        connectors, subclasses may override this method.
    """
    x1, y1, x2, y2 = self.bounding_box(offset)
    if self.connector_flags & CONNECTOR_BOTTOM:
      self._draw_connector(canvas, ((x1 + x2) / 2, y2))
    if self.connector_flags & CONNECTOR_CENTER:
      self._draw_connector(canvas, ((x1 + x2) / 2, (y1 + y2) / 2))
    if self.connector_flags & CONNECTOR_LEFT:
      self._draw_connector(canvas, (x1, (y1 + y2) / 2))
    if self.connector_flags & CONNECTOR_RIGHT:
      self._draw_connector(canvas, (x2, (y1 + y2) / 2))
    if self.connector_flags & CONNECTOR_TOP:
      self._draw_connector(canvas, ((x1 + x2) / 2, y1))
  def attach_tags(self, canvas, tags=(DRAG_TAG, ROTATE_TAG)):
    """
    |tags|: a tuple of the tags to attach.
    Attaches the given |tags| to every part of this drawable on the canvas.
    """
    for part in self.parts:
      canvas.itemconfig(part, tags=tags)
  def redraw(self, canvas):
    """
    Redraws this drawable on the given |canvas|. If the drawable was previously
        deleted, this method sets it live.
    """
    self.draw_on(canvas, self.offset)
    self.attach_tags(canvas)
    for connector in self.connectors:
      connector.redraw(canvas)
    self.set_live()
  def _delete_from(self, canvas):
    """
    Deletes the parts of this drawable from the given |canvas|.
    Returns an Action corresponding to the delete.
    """
    def delete():
      """
      Deletes the drawable.
      """
      for part in self.parts:
        canvas.delete(part)
      self.parts.clear()
      # mark this drawable deleted
      self._live = False
    # do delete
    delete()
    return Action(delete, lambda: self.redraw(canvas), 'delete drawable parts')
  def delete_from(self, canvas):
    """
    Deletes all parts of this drawable as well as all connectors and wires
        attached to it from the |canvas|.
    Returns an Action corresponding to the collective delete.
    """
    assert self._live, 'this drawable has already been deleted'
    # track delete actions
    delete_actions = []
    # first delete all the connectors for this drawable
    for connector in self.connectors:
      delete_actions.append(connector.delete_from(canvas))
    # then delete all the parts of this drawable
    delete_actions.append(self._delete_from(canvas))
    return Multi_Action(delete_actions, 'delete drawable')
  def move(self, canvas, dx, dy):
    """
    Moves this item by |dx| in the x direction and |dy| in the y direction on
        the given |canvas|.
    """
    if dx or dy:
      # move all parts of this item
      for part in self.parts:
        canvas.move(part, dx, dy)
      # move all connectors for this item
      for connector in self.connectors:
        connector.move(canvas, dx, dy)
  def wires(self):
    """
    Returns the wires for this drawable.
    """
    for connector in self.connectors:
      for wire in connector.wires():
        yield wire

class Connector:
  """
  Pieces used to connect drawables using wires.
  """
  def __init__(self, canvas_id, center, drawable):
    """
    |canvas_id|: the canvas id of the circle used to draw this connector.
    |center|: a tuple of the form (x, y) indicating the center of this
        connector.
    |drawable|: the Drawable to which this connector belongs.
    """
    assert isinstance(drawable, Drawable), 'drawable must be a Drawable'
    self.canvas_id = canvas_id
    self.center = center
    self.drawable = drawable
    # wires that start at this connector
    self.start_wires = set()
    # wires that end at this connector
    self.end_wires = set()
  def _delete_from(self, canvas):
    """
    Deletes this connector from the canvas.
    Returns an Action corresponding to the delete.
    """
    def delete():
      """
      Deletes the connector circle from the canvas.
      """
      canvas.delete(self.canvas_id)
    # do delete
    delete()
    return Action(delete, lambda: self.redraw(canvas),
        'delete connector parts')
  def delete_from(self, canvas):
    """
    Deletes this connector as well as all the wires attached to it from the
        |canvas|.
    Returns an Action corresponding to the collective delete.
    """
    # track delete actions
    delete_actions = []
    # first delete all the wires attached to the connector
    for wire in list(self.wires()):
      delete_actions.append(wire.delete_from(canvas))
    # then delete the connector circle
    delete_actions.append(self._delete_from(canvas))
    return Multi_Action(delete_actions, 'delete connector')
  def lift(self, canvas):
    """
    Lifts (raises) this connector above the wires that are attached to it so
        that it is easy to draw more wires.
    """
    canvas.tag_raise(self.canvas_id)
  def _redraw_wires(self, canvas):
    """
    Redraws the wires for this connector.
    """
    # ensure that all wires that start at this connector start at its center
    for wire in self.start_wires:
      wire.redraw(canvas)
    # ensure that all wires that end at this connector end at its center
    for wire in self.end_wires:
      wire.redraw(canvas)
    self.lift(canvas)
  def move(self, canvas, dx, dy):
    """
    Moves this connector by |dx| in the x direction and |dy| in the y
        direction.
    """
    if dx or dy:
      x, y = self.center
      self.center = (x + dx, y + dy)
      canvas.move(self.canvas_id, dx, dy)
      self._redraw_wires(canvas)
  def redraw(self, canvas):
    """
    Redraws this connector, most importantly to mark/color it connected or not
        connected.
    """
    canvas.delete(self.canvas_id)
    x, y = self.center
    # appropriately choose fill color
    fill = CONNECTOR_COLOR if self.num_wires() else CONNECTOR_EMPTY_COLOR
    self.canvas_id = create_connector(canvas, x, y, fill=fill)
  def wires(self):
    """
    Returns a generator of the wires attached to this connector.
    """
    for wire in self.start_wires:
      yield wire
    for wire in self.end_wires:
      yield wire
  def num_wires(self):
    """
    Returns the number of wires attached to this connector.
    """
    return len(self.start_wires) + len(self.end_wires)

class Wire:
  """
  Representation for a wire connecting Drawables via Connectors.
  """
  def __init__(self, parts, start_connector, end_connector, directed):
    """
    |parts|: a list of the canvas ids of the lines the wire is composed of.
    |start_connector|: the start Connector for this wire.
    |end_connector|: the end Connector for this wire.
    |directed|: True if this wire is directed, False otherwise.
    """
    assert isinstance(start_connector, Connector), ('start_connector must be a'
        ' Connector')
    assert isinstance(end_connector, Connector), ('end_connector must be a '
        'Connector')
    self.parts = parts
    self.start_connector = start_connector
    self.end_connector = end_connector
    self.directed = directed
    # wire starts unlabeld, but may be labeld by board when necessary
    # wire labels are useful for applications
    # see board._label_wires for details on wire labeling convention
    self.label = None
  def connectors(self):
    """
    Returns a generator for the two connectors of this wire.
    """
    yield self.start_connector
    yield self.end_connector
  def other_connector(self, connector):
    """
    Returns the connector on this wire on the opposite end of the given
        |connector|, which must be one of the two connectors for this wire.
    """
    if connector is self.start_connector:
      return self.end_connector
    elif connector is self.end_connector:
      return self.start_connector
    else:
      raise Exception('Unexpected connector for this wire')
  def _delete_from(self, canvas):
    """
    Deletes the lines this wire is composed of from the |canvas|.
    Returns an Action corresponding to the delete.
    """
    def delete():
      """
      Deletes the wire.
      """
      for part in self.parts:
        canvas.delete(part)
      self.parts = []
    # do delete
    delete()
    return Action(delete, lambda: self.redraw(canvas), 'delete wire parts')
  def _remove_from_connectors(self, canvas):
    """
    Removes this wire from its connectors.
    Returns an Action corresponding to the removal.
    """
    def remove():
      """
      Removes the wire from its connectors.
      """
      self.start_connector.start_wires.remove(self)
      self.start_connector.redraw(canvas)
      self.end_connector.end_wires.remove(self)
      self.end_connector.redraw(canvas)
    def unremove():
      """
      Adds this wire back to its connectors.
      """
      self.start_connector.start_wires.add(self)
      self.start_connector.redraw(canvas)
      self.end_connector.end_wires.add(self)
      self.end_connector.redraw(canvas)
    # do remove
    remove()
    return Action(remove, unremove, 'remove wire from connectors')
  def _maybe_delete_empty_wire_connector(self, canvas, connector):
    """
    Deletes |connector| if it is a wire connector and it is not connected to
        any wires. If the connector is deleted, returns an Action corresponding
        to the delete. Returns None otherwise.
    """
    if not connector.num_wires() and isinstance(connector.drawable,
        Wire_Connector_Drawable) and connector.drawable.is_live():
      return connector.drawable.delete_from(canvas)
  def delete_from(self, canvas):
    """
    Deletes this wire from the |canvas|. If any of its connectors ends up
        being an empty wire connector, it gets deleted. Returns an Action
        corresponding to the collective delete.
    """
    # track delete actions
    delete_actions = []
    # first delete wire parts
    delete_actions.append(self._delete_from(canvas))
    # then remove wire from connectors
    delete_actions.append(self._remove_from_connectors(canvas))
    # then delete connectors if they end up being empty wire connectors
    for connector in self.connectors():
      delete_connector_action = self._maybe_delete_empty_wire_connector(canvas,
          connector)
      if delete_connector_action:
        delete_actions.append(delete_connector_action)
    return Multi_Action(delete_actions, 'delete wire')
  def _draw_label(self, canvas):
    """
    Draws the label of this wire at the middle of the wire.
    """
    x1, y1 = self.start_connector.center
    x2, y2 = self.end_connector.center
    self.parts.append(canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
        text=self.label))
  def redraw(self, canvas):
    """
    Redraws this wire.
    """
    # delete the lines the wire is composed of
    for part in self.parts:
      canvas.delete(part)
    # redraw the wire
    x1, y1 = self.start_connector.center
    x2, y2 = self.end_connector.center
    self.parts = create_wire(canvas, x1, y1, x2, y2, self.directed)
    # redraw label
    if DISPLAY_WIRE_LABELS:
      self._draw_label(canvas)
    # lift connectors to make it easy to draw other wires
    for connector in self.connectors():
      connector.redraw(canvas)
  def serialize(self):
    """
    Returns a string representing this wire at it's current location.
    """
    return 'Wire %s %s' % (str(self.start_connector.center),
      str(self.end_connector.center))
  @staticmethod
  def deserialize(item_str, board):
    """
    If possible, deserializes |item_str| and adds the appropriate wire to the
        given |board|. Returns True on success, and False on failure.
    """
    m = match(r'Wire %s %s' % (RE_INT_PAIR, RE_INT_PAIR), item_str)
    if m:
      x1, y1, x2, y2 = map(int, m.groups())
      board.add_wire(x1, y1, x2, y2)
      return True
    return False

class Wire_Connector_Drawable(Drawable):
  """
  Drawable to connect wires. This can be used to "bend" wires as well us as an
      ending to wires that outherwise would not have endings.
  """
  def __init__(self):
    Drawable.__init__(self, CONNECTOR_RADIUS * 2, CONNECTOR_RADIUS * 2,
        CONNECTOR_CENTER)
  def draw_on(self, canvas, offset=(0, 0)):
    # nothing to draw
    pass
  def serialize(self, offset):
    return 'Wire connector %s' % str(offset)
  @staticmethod
  def deserialize(item_str, board):
    m = match(r'Wire connector %s' % RE_INT_PAIR, item_str)
    if m:
      ox, oy = map(int, m.groups())
      board.add_drawable(Wire_Connector_Drawable(), (ox, oy))
      return True
    return False

class Run_Drawable(Drawable):
  """
  Abstract Drawable to serve as a "Run" button.
  """
  def __init__(self, text):
    Drawable.__init__(self, RUN_RECT_SIZE, RUN_RECT_SIZE)
    self.text = text
  def draw_on(self, canvas, offset=(0, 0)):
    ox, oy = offset
    self.parts.add(canvas.create_rectangle((ox, oy, ox + RUN_RECT_SIZE,
        oy + RUN_RECT_SIZE), fill=RUN_RECT_FILL, outline=RUN_RECT_OUTLINE))
    self.parts.add(canvas.create_text(ox + RUN_RECT_SIZE / 2, oy +
        RUN_RECT_SIZE / 2, text=self.text, fill=RUN_TEXT_FILL,
        activefill=RUN_TEXT_ACTIVE_FILL))
  def serialize(self, offset):
    # should never be needed
    return ''
  @staticmethod
  def deserialize(item_str, board):
    # should never be needed
    return False
