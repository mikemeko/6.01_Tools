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
from core.util.undo import Action
from core.util.undo import Multi_Action
from util import create_connector
from util import create_wire
from util import snap

class Drawable:
  """
  An abstract class to represent an item that is drawn on the board. All
      subclasses should impement the draw_on(canvas) method.
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
    # canvas ids for the parts on this item, updated by draw_on(canvas)
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
    This method is called exactly once per Drawable.
    """
    raise NotImplementedError('subclasses should implement this')
  def rotated(self):
    """
    Returns a rotated version of this drawable. On a board, Shift-click will
        result in this rotation. The default implementation is no rotation.
    """
    return self
  def is_live(self):
    """
    Returns True if this drawable is still on the board, or False if it has
        been deleted.
    """
    return self._live
  def set_live(self):
    """
    TODO(mikemeko)
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
  def redraw(self, canvas):
    """
    TODO(mikemeko)
    """
    # TODO(mikemeko): probably write a method to do all this work
    # and use it in board._add_drawable
    self.draw_on(canvas, self.offset)
    for part in self.parts:
      canvas.itemconfig(part, tags=(DRAG_TAG, ROTATE_TAG))
    for connector in self.connectors:
      connector.redraw(canvas)
    # mark this drawable live
    self._live = True
  def _delete_from(self, canvas):
    """
    TODO(mikemeko)
    """
    def delete():
      """
      TODO(mikemeko)
      """
      for part in self.parts:
        canvas.delete(part)
      self.parts.clear()
      # mark this drawable deleted
      self._live = False
    delete()
    return Action(delete, lambda: self.redraw(canvas), 'delete drawable parts')
  def delete_from(self, canvas):
    """
    Deletes this item from the |canvas|.
    """
    assert self._live, 'this drawable has already been deleted'
    # delete all connectors for this drawable
    delete_actions = []
    for connector in self.connectors:
      delete_actions.append(connector.delete_from(canvas))
    delete_actions.append(self._delete_from(canvas))
    return Multi_Action(delete_actions, 'delete drawable')
  def move(self, canvas, dx, dy):
    """
    Moves this item by |dx| in the x direction and |dy| in the y direction on
        the given |canvas|.
    """
    if dx != 0 or dy != 0:
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
  Pieces used to connect items using wires.
  """
  def __init__(self, canvas_id, center, drawable):
    """
    |canvas_id|: the canvas id of this connector.
    |center|: a tuple of the form (x, y) indicating the center of this
        connector.
    |drawable|: the item to which this connector belongs.
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
    TODO(mikemeko)
    """
    def delete():
      """
      TODO(mikemeko)
      """
      canvas.delete(self.canvas_id)
    def undelete():
      """
      TODO(mikemeko)
      """
      self.redraw(canvas)
    delete()
    return Action(delete, undelete, 'delete connector parts')
  def delete_from(self, canvas):
    """
    Deletes this connector from the |canvas|.
    """
    # delete all wires attached to this connector
    delete_actions = []
    for wire in list(self.wires()):
      delete_actions.append(wire.delete_from(canvas))
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
    if dx != 0 or dy != 0:
      x, y = self.center
      self.center = (x + dx, y + dy)
      canvas.move(self.canvas_id, dx, dy)
      self._redraw_wires(canvas)
  def redraw(self, canvas):
    """
    Redraws this connector, most importantly to mark it connected or not
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
    # TODO(mikemeko)
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
    TODO(mikemeko)
    """
    def delete():
      """
      TODO(mikemeko)
      """
      for part in self.parts:
        canvas.delete(part)
    def undelete():
      """
      TODO(mikemeko)
      """
      x1, y1 = self.start_connector.center
      x2, y2 = self.end_connector.center
      self.parts = create_wire(canvas, x1, y1, x2, y2, self.directed)
      self.redraw(canvas)
    delete()
    return Action(delete, undelete, 'delete wire parts')
  def _remove_from_connectors(self, canvas):
    """
    TODO(mikemeko)
    """
    def remove():
      """
      TODO(mikemeko)
      """
      self.start_connector.start_wires.remove(self)
      self.end_connector.end_wires.remove(self)
      # TODO(mikemeko): self.connectors()
      for connector in self.connectors():
        connector.redraw(canvas)
    def unremove():
      """
      TODO(mikemeko)
      """
      self.start_connector.start_wires.add(self)
      self.end_connector.end_wires.add(self)
      for connector in self.connectors():
        connector.redraw(canvas)
    remove()
    return Action(remove, unremove, 'remove wire from connectors')
  def _maybe_delete_empty_wire_connector(self, canvas, connector):
    """
    Deletes |connector| if it is a wire connector and it is not connected to
        any wires. Returns True if |connector| is deleted, False otherwise.
    """
    if not connector.num_wires() and isinstance(connector.drawable,
        Wire_Connector_Drawable) and connector.drawable.is_live():
      return connector.drawable.delete_from(canvas)
  def delete_from(self, canvas):
    """
    Deletes this wire from the |canvas|.
    """
    delete_actions = [self._delete_from(canvas),
        self._remove_from_connectors(canvas)]
    for connector in (self.start_connector, self.end_connector):
      delete_connector = self._maybe_delete_empty_wire_connector(canvas,
          connector)
      if delete_connector:
        delete_actions.append(delete_connector)
    return Multi_Action(delete_actions, 'delete wire')
  def _draw_label(self, canvas):
    """
    Draws the label of this wire.
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
