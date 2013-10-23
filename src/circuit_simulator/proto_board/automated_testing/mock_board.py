"""
Mocks for test automation, most importantly a mock drawing board.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.gui.components import Wire
from core.gui.wire_labeling import label_wires

class Mock_Board:
  """
  Mock drawing board (a bit hacky, but very useful for testing, includes all
      necessary board methods for protoboard layout). Methods here without
      docstrings have the same purpose as in core.gui.board.Board.
  """
  def __init__(self):
    self._canvas = Mock_Canvas()
    self._drawables = []
  def _connector_centered_at(self, center):
    """
    Returns the connector on this Mock_Board centered at the given |center|
        point, or None if no such connector could be found.
    """
    for drawable in self._drawables:
      for connector in drawable.connectors:
        if connector.center == center:
          return connector
    return None
  # method called by deserializers in circuit_simulator.main.circuit_drawables
  def add_drawable(self, drawable, offset):
    drawable.draw_connectors(self._canvas, offset)
    self._drawables.append(drawable)
  # method called by Wire deserializer
  def add_wire(self, wire_path):
    x1, y1 = wire_path[0]
    start_connector = self._connector_centered_at((x1, y1))
    assert start_connector
    x2, y2 = wire_path[-1]
    end_connector = self._connector_centered_at((x2, y2))
    assert end_connector
    wire = Wire([], start_connector, end_connector, [(x1, y1), (x1, y2),
        (x2, y2)], False)
    start_connector.start_wires.add(wire)
    end_connector.end_wires.add(wire)
  # methoed called in circuit_simulator.main.analyze_board.run_analysis
  def get_drawables(self):
    # label wires (very important, this is how we extract connectivity)
    label_wires(self._drawables)
    # label drawables (not important)
    for drawable in self._drawables:
      drawable.label = ''
    return self._drawables
  def display_message(self, message, *args, **kwargs):
    print message
  def remove_message(self):
    pass
  # methods called in core.save.save.open_board_from_file
  def reset_cursor_state(self):
    pass
  def clear(self):
    pass
  def reset(self):
    pass
  def relabel_wires(self, f):
    pass

class Mock_Canvas:
  """
  Mock Tk canvas.
  """
  def create_oval(self, *args, **kwargs):
    return 0
  def create_text(self, *args, **kwargs):
    return 0
