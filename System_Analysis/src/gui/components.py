"""
The things that may exist on a board: drawable items, connectors, and wires.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import WIRE_COLOR
from constants import WIRE_WIDTH

class Drawable:
  def __init__(self, bounding_box, connector_flags=0):
    # TODO(mikemeko): check coiditions
    self.bounding_box = bounding_box
    self.connector_flags = connector_flags
    self.parts = []
    self.connectors = []
  @property
  def draw_on(self, canvas):
    raise NotImplementedError('subclasses should implement this')
  def delete_from(self, canvas):
    for part in self.parts:
      canvas.delete(part)
    for connector in self.connectors:
      connector.delete_from(canvas)
  def move(self, canvas, dx, dy):
    if dx != 0 or dy != 0:
      old_x1, old_y1, old_x2, old_y2 = self.bounding_box
      self.bounding_box = (old_x1 + dx, old_y1 + dy, old_x2 + dx, old_y2 + dy)
      for part in self.parts:
        canvas.move(part, dx, dy)
      for connector in self.connectors:
        canvas.move(connector.canvas_id, dx, dy)
        old_x, old_y = connector.center
        connector.center = (old_x + dx, old_y + dy)
        connector.redraw_wires(canvas)
  def remove_wire(self, canvas_id):
    for connector in self.connectors:
      connector.remove_wire(canvas_id)
  def _check_rep(self):
    # TODO
    pass

class Connector:
  def __init__(self, canvas_id, center, drawable):
    self.canvas_id = canvas_id
    self.center = center
    self.drawable = drawable
    self.start_wires = []
    self.end_wires = []
  def delete_from(self, canvas):
    canvas.delete(self.canvas_id)
    for wire in self.start_wires[:]:
      wire.delete_from(canvas)
    for wire in self.end_wires[:]:
      wire.delete_from(canvas)
  def redraw_wires(self, canvas):
    for wire in self.start_wires:
      canvas.delete(wire.canvas_id)
      x1, y1 = self.center
      x2, y2 = wire.end_connector.center
      wire.canvas_id = canvas.create_line(x1, y1, x2, y2, fill=WIRE_COLOR,
          width=WIRE_WIDTH)
    for wire in self.end_wires:
      canvas.delete(wire.canvas_id)
      x1, y1 = wire.start_connector.center
      x2, y2 = self.center
      wire.canvas_id = canvas.create_line(x1, y1, x2, y2, fill=WIRE_COLOR,
          width=WIRE_WIDTH)
  def remove_wire(self, canvas_id):
    for wire in self.start_wires:
      if wire.canvas_id == canvas_id:
        self.start_wires.remove(wire)
        return
    for wire in self.end_wires:
      if wire.canvas_id == canvas_id:
        self.end_wires.remove(wire)
        return

class Wire:
  def __init__(self, canvas_id, start_connector, end_connector):
    self.canvas_id = canvas_id
    self.start_connector = start_connector
    self.end_connector = end_connector
  def delete_from(self, canvas):
    canvas.delete(self.canvas_id)
    self.start_connector.start_wires.remove(self)
    self.end_connector.end_wires.remove(self)
