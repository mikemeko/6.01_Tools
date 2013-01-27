"""
The things that may exist on a board: drawable items, connectors, and wires.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import CONNECTOR_BOTTOM
from constants import CONNECTOR_CENTER
from constants import CONNECTOR_COLOR
from constants import CONNECTOR_LEFT
from constants import CONNECTOR_RADIUS
from constants import CONNECTOR_RIGHT
from constants import CONNECTOR_TAG
from constants import CONNECTOR_TOP
from Tkinter import Canvas
from util import create_circle
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
  @property
  def draw_on(self, canvas, offset):
    """
    Draws the parts of this item on the |canvas| at the given |offset|. Should
        add the canvas ids of all drawn objects to self.parts.
    All subclasses should implement this.
    This method is called exactly once per Drawable.
    """
    raise NotImplementedError('subclasses should implement this')
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
    Draws a connector for this Drawable at the indicated |point|.
    """
    x, y = map(snap, point)
    canvas_id = create_circle(canvas, x, y, CONNECTOR_RADIUS,
        fill=CONNECTOR_COLOR, activewidth=2, tags=CONNECTOR_TAG)
    self.connectors.add(Connector(canvas_id, (x, y), self))
  def draw_connectors(self, canvas, offset=(0, 0)):
    """
    Draws the connectors for this Drawable on the given |canvas|, with the
        Drawable drawn with the given |offset|.
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
  def delete_from(self, canvas):
    """
    Deletes this item from the |canvas|.
    """
    # delete all parts of this item
    for part in self.parts:
      canvas.delete(part)
    # delete all connectors for this item
    for connector in self.connectors:
      connector.delete_from(canvas)
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
  def delete_from(self, canvas):
    """
    Deletes this connector from the |canvas|.
    """
    # delete this connector
    canvas.delete(self.canvas_id)
    # delete all wires attached to this connector
    for wire in self.wires():
      wire.delete_from(canvas)
  def move(self, canvas, dx, dy):
    """
    Moves this connector by |dx| in the x direction and |dy| in the y
        direction.
    """
    if dx != 0 or dy != 0:
      x, y = self.center
      self.center = (x + dx, y + dy)
      canvas.move(self.canvas_id, dx, dy)
      self.redraw_wires(canvas)
  def lift(self, canvas):
    """
    TODO(mikemeko)
    """
    canvas.tag_raise(self.canvas_id)
  def redraw_wires(self, canvas):
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
  def __init__(self, parts, start_connector, end_connector, label):
    """
    |parts|: a list of the canvas ids of the lines the wire is composed of.
    |start_connector|: the start Connector for this wire.
    |end_connector|: the end Connector for this wire.
    TODO(mikemeko)
    """
    assert isinstance(start_connector, Connector), ('start_connector must be a'
        ' Connector')
    assert isinstance(end_connector, Connector), ('end_connector must be a '
        'Connector')
    self.parts = parts
    self.start_connector = start_connector
    self.end_connector = end_connector
    self.label = label
  def delete_from(self, canvas):
    """
    Deletes this wire from the |canvas|.
    """
    assert isinstance(canvas, Canvas), 'canvas must be a Canvas'
    # delete the lines the wire is composed of
    for part in self.parts:
      canvas.delete(part)
    # remove this wire from the connectors' wire lists
    self.start_connector.start_wires.remove(self)
    self.end_connector.end_wires.remove(self)
  def redraw(self, canvas):
    """
    Redraws this wire.
    """
    assert isinstance(canvas, Canvas), 'canvas must be a Canvas'
    # delete the lines the wire is composed of
    for part in self.parts:
      canvas.delete(part)
    # redraw the wire
    x1, y1 = self.start_connector.center
    x2, y2 = self.end_connector.center
    self.parts = create_wire(canvas, x1, y1, x2, y2)
  # TODO(mikemeko): str and repr for others
  def __str__(self):
    return str(self.label)
  def __repr__(self):
    return str(self)

class Wire_Connector_Drawable(Drawable):
  """
  Drawable to connect wires. This can be used to "bend" wires as well us as an
      ending to wires that outherwise would not have endings.
  TODO(mikemeko): when a wire connected to a wire connector drawable is deleted
      the wire connector drawable should also be deleted if there are no other
      wires attached to it.
  """
  def __init__(self, label):
    """
    TODO(mikemeko)
    """
    Drawable.__init__(self, CONNECTOR_RADIUS * 2, CONNECTOR_RADIUS * 2,
        CONNECTOR_CENTER)
    self.label = label
  def draw_on(self, canvas, offset=(0, 0)):
    # nothing to draw
    pass
