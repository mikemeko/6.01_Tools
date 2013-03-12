"""
Proto board visualization.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.constants import COLUMNS
from circuit_simulator.proto_board.constants import PROTO_BOARD_HEIGHT
from circuit_simulator.proto_board.constants import ROWS
from circuit_simulator.proto_board.util import valid_loc
from constants import BACKGROUND_COLOR
from constants import CONNECTOR_COLOR
from constants import CONNECTOR_SIZE
from constants import CONNECTOR_SPACING
from constants import HEIGHT
from constants import PADDING
from constants import VERTICAL_SEPARATION
from constants import WIDTH
from constants import WINDOW_TITLE
from constants import WIRE_COLOR
from constants import WIRE_OUTLINE
from Tkinter import Canvas
from Tkinter import Frame
from Tkinter import Tk

class Proto_Board_Visualizer(Frame):
  """
  Tk Frame to visualize Proto boards.
  """
  def __init__(self, parent):
    """
    |wires|: a list of Wire objects to display on this proto board.
    """
    self.parent = parent
    Frame.__init__(self, self.parent, background=BACKGROUND_COLOR)
    self.parent.title(WINDOW_TITLE)
    self._canvas = Canvas(self, width=WIDTH, height=HEIGHT,
        background=BACKGROUND_COLOR)
    self._set_up()
  def _vertical_section(self, r):
    """
    Returns the number of vertical separators that stand between the top of the
        proto board and the given row |r|.
    """
    return sum (r >= barrier for barrier in (2, PROTO_BOARD_HEIGHT / 2,
        PROTO_BOARD_HEIGHT - 2))
  def _rc_to_xy(self, r, c):
    """
    Returns the top left corner of the connector located at row |r| column |c|.
    """
    x = c * (CONNECTOR_SIZE + CONNECTOR_SPACING) + PADDING
    y = r * (CONNECTOR_SIZE + CONNECTOR_SPACING) + PADDING + (
        self._vertical_section(r) * (VERTICAL_SEPARATION - CONNECTOR_SPACING))
    return x, y
  def _set_up(self):
    """
    Draws the connectors as well as labels for the rows and columns.
    """
    # connectors
    for r in ROWS:
      for c in COLUMNS:
        if valid_loc((r, c)):
          x, y = self._rc_to_xy(r, c)
          self._canvas.create_rectangle(x, y, x + CONNECTOR_SIZE,
              y + CONNECTOR_SIZE, fill=CONNECTOR_COLOR,
              outline=CONNECTOR_COLOR)
    # row labels
    for r in ROWS:
      self._canvas.create_text(self._rc_to_xy(r, -1), text=r)
    # columns labels
    for c in COLUMNS:
      if c % 5 == 0:
        self._canvas.create_text(self._rc_to_xy(-1, c), text=c)
    self._canvas.pack()
    self.pack()
  def visualize(self, proto_board):
    """
    Draws the wires on the proto board.
    TODO(mikemeko): update
    """
    for wire in proto_board.get_wires():
      x_1, y_1 = self._rc_to_xy(wire.r_1, wire.c_1)
      x_2, y_2 = self._rc_to_xy(wire.r_2, wire.c_2)
      if x_1 > x_2 or y_1 > y_2:
        x_1, y_1, x_2, y_2 = x_2, y_2, x_1, y_1
      self._canvas.create_rectangle(x_1, y_1, x_2 + CONNECTOR_SIZE,
          y_2 + CONNECTOR_SIZE, fill=WIRE_COLOR, outline=WIRE_OUTLINE)
    self.parent.mainloop()

def visualize_proto_board(proto_board):
  """
  TODO(mikemeko)
  """
  Proto_Board_Visualizer(Tk()).visualize(proto_board)
