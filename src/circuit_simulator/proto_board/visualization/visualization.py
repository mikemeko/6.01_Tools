"""
Proto board visualization.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.main.constants import NEGATIVE_COLOR
from circuit_simulator.main.constants import POSITIVE_COLOR
from circuit_simulator.proto_board.constants import COLUMNS
from circuit_simulator.proto_board.constants import GROUND_RAIL
from circuit_simulator.proto_board.constants import POWER_RAIL
from circuit_simulator.proto_board.constants import PROTO_BOARD_HEIGHT
from circuit_simulator.proto_board.constants import PROTO_BOARD_WIDTH
from circuit_simulator.proto_board.constants import ROWS
from circuit_simulator.proto_board.util import num_vertical_separators
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
from constants import WIRE_COLORS
from constants import WIRE_OUTLINE
from Tkinter import Canvas
from Tkinter import Frame

class Proto_Board_Visualizer(Frame):
  """
  Tk Frame to visualize Proto boards.
  """
  def __init__(self, parent, proto_board, show_pwr_gnd_pins):
    """
    |proto_board|: the proto board to visualize.
    |show_pwr_gnd_pins|: flag whether to show pwr and gnd pins as a reminder to
        connect to a power supply.
    """
    Frame.__init__(self, parent, background=BACKGROUND_COLOR)
    parent.title(WINDOW_TITLE)
    parent.resizable(0, 0)
    self._proto_board = proto_board
    self._show_pwr_gnd_pins = show_pwr_gnd_pins
    self._canvas = Canvas(self, width=WIDTH, height=HEIGHT,
        background=BACKGROUND_COLOR)
    self._draw_proto_board()
  def _rc_to_xy(self, loc):
    """
    Returns the top left corner of the connector located at row |r| column |c|.
    """
    r, c = loc
    x = c * (CONNECTOR_SIZE + CONNECTOR_SPACING) + PADDING
    y = r * (CONNECTOR_SIZE + CONNECTOR_SPACING) + PADDING + (
        num_vertical_separators(r) * (VERTICAL_SEPARATION - CONNECTOR_SPACING))
    return x, y
  def _draw_connector(self, x, y, fill=CONNECTOR_COLOR,
      outline=CONNECTOR_COLOR):
    """
    Draws a connector at the given coordinate and with the given colors.
    """
    self._canvas.create_rectangle(x, y, x + CONNECTOR_SIZE, y + CONNECTOR_SIZE,
        fill=fill, outline=outline)
  def _draw_connectors(self):
    """
    Draws the connectors on the proto board.
    """
    for r in ROWS:
      for c in COLUMNS:
        if valid_loc((r, c)):
          self._draw_connector(*self._rc_to_xy((r, c)))
  def _draw_bus_line(self, y, color):
    """
    Draws a bus line at the given horizontal position |y| and with the given
        |color|.
    """
    x_1 = self._rc_to_xy((0, 1))[0]
    x_2 = self._rc_to_xy((0, PROTO_BOARD_WIDTH - 1))[0]
    self._canvas.create_line(x_1, y, x_2, y, fill=color)
  def _draw_bus_lines(self):
    """
    Draws all four bus lines on the proto board.
    """
    offset = 10
    self._draw_bus_line(self._rc_to_xy((0, 0))[1] - offset, NEGATIVE_COLOR)
    self._draw_bus_line(self._rc_to_xy((1, 0))[1] + CONNECTOR_SIZE + offset,
        POSITIVE_COLOR)
    self._draw_bus_line(self._rc_to_xy((PROTO_BOARD_HEIGHT - 2, 0))[1] - (
        offset), NEGATIVE_COLOR)
    self._draw_bus_line(self._rc_to_xy((PROTO_BOARD_HEIGHT - 1, 0))[1] + (
        CONNECTOR_SIZE + offset), POSITIVE_COLOR)
  def _draw_labels(self):
    """
    Draws the row and column labels.
    """
    # row labels
    row_labels = dict(zip(range(11, 1, -1), ['A', 'B', 'C', 'D', 'E', 'F', 'G',
        'H', 'I', 'J']))
    for r in filter(lambda r: r in row_labels, ROWS):
      self._canvas.create_text(self._rc_to_xy((r, -1)), text=row_labels[r])
      x, y = self._rc_to_xy((r, PROTO_BOARD_WIDTH))
      self._canvas.create_text(x + CONNECTOR_SIZE, y, text=row_labels[r])
    # columns labels
    h_offset = 2
    v_offset = 10
    for c in filter(lambda c: c == 0 or (c + 1) % 5 == 0, COLUMNS):
      x_1, y_1 = self._rc_to_xy((2, c))
      self._canvas.create_text(x_1 + h_offset, y_1 - v_offset, text=(c + 1))
      x_2, y_2 = self._rc_to_xy((PROTO_BOARD_HEIGHT - 3, c))
      self._canvas.create_text(x_2 + h_offset, y_2 + CONNECTOR_SIZE + v_offset,
          text=(c + 1))
  def _draw_gnd_pwr_pins(self):
    """
    Draws pins to show the ground and power rails.
    """
    # pin positions
    g_x, g_y = self._rc_to_xy((GROUND_RAIL, PROTO_BOARD_WIDTH - 3))
    p_x, p_y = self._rc_to_xy((POWER_RAIL, PROTO_BOARD_WIDTH - 3))
    # big rectangles
    large_h_offset = 3 * CONNECTOR_SIZE + 2 * CONNECTOR_SPACING
    small_h_offset = 2
    large_v_offset = 7
    small_v_offset = 3
    self._canvas.create_rectangle(g_x - small_h_offset, g_y - large_v_offset,
        g_x + large_h_offset, g_y + CONNECTOR_SIZE + small_v_offset,
        fill=NEGATIVE_COLOR)
    self._canvas.create_rectangle(p_x - small_h_offset, p_y - small_v_offset,
        p_x + large_h_offset, p_y + CONNECTOR_SIZE + large_v_offset,
        fill=POSITIVE_COLOR)
    # connectors
    self._draw_connector(g_x, g_y, outline='black')
    self._draw_connector(p_x, p_y, outline='black')
    # text
    text_v_offset = 2
    text_h_offset = 17
    self._canvas.create_text(g_x + text_h_offset, g_y - text_v_offset,
        text='gnd', fill='white')
    self._canvas.create_text(p_x + text_h_offset, p_y + text_v_offset,
        text='+10', fill='white')
  def _draw_piece(self, piece):
    """
    Draws the given circuit |piece| on the canvas.
    """
    piece.draw_on(self._canvas, self._rc_to_xy(piece.top_left_loc))
  def _draw_pieces(self):
    """
    Draws all the pieces on the proto board.
    """
    for piece in self._proto_board.get_pieces():
      self._draw_piece(piece)
  def _draw_wire(self, wire):
    """
    Draws the given |wire| on the canvas.
    """
    x_1, y_1 = self._rc_to_xy(wire.loc_1)
    x_2, y_2 = self._rc_to_xy(wire.loc_2)
    if x_1 > x_2 or y_1 > y_2:
      x_1, y_1, x_2, y_2 = x_2, y_2, x_1, y_1
    length = wire.length()
    fill = 'white'
    if 1 < length < 10:
      fill = WIRE_COLORS[length]
    elif 10 <= length < 50:
      fill = WIRE_COLORS[(length + 9) / 10]
    def draw_wire(wire_id=None):
      if wire_id:
        self._canvas.delete(wire_id)
      new_wire_id = self._canvas.create_rectangle(x_1, y_1,
          x_2 + CONNECTOR_SIZE, y_2 + CONNECTOR_SIZE, fill=fill,
          outline=WIRE_OUTLINE)
      self._canvas.tag_bind(new_wire_id, '<Button-1>', lambda event: draw_wire(
          new_wire_id))
    draw_wire()
  def _draw_wires(self):
    """
    Draws all the wires on the proto board.
    """
    for wire in self._proto_board.get_wires():
      self._draw_wire(wire)
  def _draw_proto_board(self):
    """
    Draws the given |proto_board|.
    """
    self._draw_connectors()
    self._draw_bus_lines()
    self._draw_labels()
    self._draw_pieces()
    self._draw_wires()
    self._canvas.pack()
    if self._show_pwr_gnd_pins:
      self._draw_gnd_pwr_pins()
    self.pack()

def visualize_proto_board(proto_board, toplevel, show_pwr_gnd_pins=True):
  """
  Displays a nice window portraying the given |proto_board|.
  """
  Proto_Board_Visualizer(toplevel, proto_board, show_pwr_gnd_pins)
