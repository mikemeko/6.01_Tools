"""
The things that may exist on a board: drawable items, connectors, and wires.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from util import create_wire

class Drawable:
  """
  An abstract class to represent an item that is drawn on the board. All
      subclasses should impement the draw_on(canvas) method.
  """
  def __init__(self, bounding_box, connector_flags=0):
    """
    |bounding_box|: a tuple of the form (x1, y1, x2, y2) indicating the
        bounding box of this item.
    |connector_flags|: an indicator for the places where this item should have
        connectors. For example: CONNECTOR_TOP | CONNECTOR_RIGHT.
    """
    self.bounding_box = bounding_box
    self.connector_flags = connector_flags
    # canvas ids for the parts on this item, updated by draw_on(canvas)
    self.parts = set()
    # connectors on this item, updated by board
    self.connectors = set()
  @property
  def draw_on(self, canvas):
    """
    Draws the parts of this item on the |canvas|. Should add the canvas ids of
        all drawn objects to self.parts.
    All subclasses should implement this.
    """
    raise NotImplementedError('subclasses should implement this')
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
    Moves this item by |dx| in the x direction and |dy| in the y direction.
    """
    if dx != 0 or dy != 0:
      # update bounding box
      x1, y1, x2, y2 = self.bounding_box
      self.bounding_box = (x1 + dx, y1 + dy, x2 + dx, y2 + dy)
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
    # delete all wires that start at this connector
    for wire in set(self.start_wires):
      wire.delete_from(canvas)
    # delete all wires that end at this connector
    for wire in set(self.end_wires):
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

class Wire:
  """
  Representation for a wire connecting Drawables via Connectors.
  """
  def __init__(self, canvas_id, start_connector, end_connector):
    """
    |canvas_id|: the canvas id of this wire.
    |start_connector|: the start Connector for this wire.
    |end_connector|: the end Connector for this wire.
    """
    assert isinstance(start_connector, Connector), ('start_connector must be a'
        ' Connector')
    assert isinstance(end_connector, Connector), ('end_connector must be a '
        'Connector')
    self.canvas_id = canvas_id
    self.start_connector = start_connector
    self.end_connector = end_connector
  def delete_from(self, canvas):
    """
    Deletes this wire from the |canvas|.
    """
    # delete this wire
    canvas.delete(self.canvas_id)
    # remove this wire from the connectors' wire lists
    self.start_connector.start_wires.remove(self)
    self.end_connector.end_wires.remove(self)
  def redraw(self, canvas):
    """
    Redraws this wire.
    """
    canvas.delete(self.canvas_id)
    x1, y1 = self.start_connector.center
    x2, y2 = self.end_connector.center
    self.canvas_id = create_wire(canvas, x1, y1, x2, y2)
