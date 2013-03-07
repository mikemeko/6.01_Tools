"""
TODO(mikemeko)
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
from constants import WIRE_COLOR
from constants import WIRE_OUTLINE
from Tkinter import Canvas
from Tkinter import Frame
from Tkinter import mainloop
from Tkinter import Tk

class Proto_Board_Visualizer(Frame):
  """
  TODO(mikemeko)
  """
  def __init__(self, wires, parent=Tk()):
    Frame.__init__(self, parent, background=BACKGROUND_COLOR)
    self._canvas = Canvas(self, width=WIDTH, height=HEIGHT,
        background=BACKGROUND_COLOR)
    self._wires = wires
    self._set_up()
    self._display_wires()
  def _vertical_section(self, r):
    return sum (r >= barrier for barrier in (2, PROTO_BOARD_HEIGHT / 2,
        PROTO_BOARD_HEIGHT - 2))
  def _rc_to_xy(self, r, c):
    x = c * (CONNECTOR_SIZE + CONNECTOR_SPACING) + PADDING
    y = r * (CONNECTOR_SIZE + CONNECTOR_SPACING) + PADDING + (
        self._vertical_section(r) * (VERTICAL_SEPARATION - CONNECTOR_SPACING))
    return x, y
  def _set_up(self):
    for r in ROWS:
      for c in COLUMNS:
        if valid_loc((r, c)):
          x, y = self._rc_to_xy(r, c)
          self._canvas.create_rectangle(x, y, x + CONNECTOR_SIZE,
              y + CONNECTOR_SIZE, fill=CONNECTOR_COLOR,
              outline=CONNECTOR_COLOR)
    self._canvas.pack()
    self.pack()
  def _display_wires(self):
    for ((r_1, c_1), (r_2, c_2)) in self._wires:
      x_1, y_1 = self._rc_to_xy(r_1, c_1)
      x_2, y_2 = self._rc_to_xy(r_2, c_2)
      if x_1 > x_2 or y_1 > y_2:
        x_1, y_1, x_2, y_2 = x_2, y_2, x_1, y_1
      self._canvas.create_rectangle(x_1, y_1, x_2 + CONNECTOR_SIZE,
          y_2 + CONNECTOR_SIZE, fill=WIRE_COLOR, outline=WIRE_OUTLINE)
  def show(self):
    mainloop()
