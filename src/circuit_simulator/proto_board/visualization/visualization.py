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
from circuit_simulator.proto_board.util import loc_to_cmax_rep
from circuit_simulator.proto_board.util import num_vertical_separators
from circuit_simulator.proto_board.util import valid_loc
from constants import BACKGROUND_COLOR
from constants import CMAX_FILE_EXTENSION
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
from core.gui.tooltip_helper import Tooltip_Helper
from tkFileDialog import asksaveasfilename
from Tkinter import Canvas
from Tkinter import Frame
from Tkinter import Label
from Tkinter import LEFT
from Tkinter import Menu
from Tkinter import SOLID
from Tkinter import TclError
from Tkinter import Toplevel

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
    self._parent = parent
    self._parent.title(WINDOW_TITLE)
    self._parent.resizable(0, 0)
    self._proto_board = proto_board
    self._show_pwr_gnd_pins = show_pwr_gnd_pins
    self._canvas = Canvas(self, width=WIDTH, height=HEIGHT,
        background=BACKGROUND_COLOR)
    self._tooltip_helper = Tooltip_Helper(self._canvas)
    self._wire_bbox = {}
    self._setup_bindings()
    self._setup_menu()
    self._draw_proto_board()
  def _point_inside_wire(self, wire, x, y):
    """
    Returns True if the point (|x|, |y|) is on the given |wire|. |wire| must be
        one of the wires on the proto board.
    """
    assert wire in self._wire_bbox
    x_1, y_1, x_2, y_2 = self._wire_bbox[wire]
    return x_1 <= x <= x_2 and y_1 <= y <= y_2
  def _maybe_show_tooltip(self, event):
    """
    Shows a tooltip of the respective node if the cursor is on a wire or a valid
        location on the proto board.
    """
    text = None
    for wire in self._proto_board.get_wires():
      if self._point_inside_wire(wire, event.x, event.y):
        text = wire.node
        break
    else:
      loc = self._xy_to_rc(event.x, event.y)
      if loc:
        text = self._proto_board.node_for(loc)
    if text is not None:
      self._tooltip_helper.show_tooltip(event.x, event.y, text)
    else:
      self._tooltip_helper.hide_tooltip()
  def _setup_bindings(self):
    """
    Sets up event bindings.
    """
    self._canvas.bind('<Motion>', self._maybe_show_tooltip)
  def _rc_to_xy(self, loc):
    """
    Returns the top left corner of the connector located at row |r| column |c|.
    """
    r, c = loc
    x = c * (CONNECTOR_SIZE + CONNECTOR_SPACING) + PADDING
    y = r * (CONNECTOR_SIZE + CONNECTOR_SPACING) + PADDING + (
        num_vertical_separators(r) * (VERTICAL_SEPARATION - CONNECTOR_SPACING))
    return x, y
  def _xy_to_rc(self, x, y):
    """
    Returns the row and column of the valid location on the proto board
        containing the point (|x|, |y|), or None if no such location exists.
    """
    for r in xrange(PROTO_BOARD_HEIGHT):
      for c in xrange(PROTO_BOARD_WIDTH):
        if valid_loc((r, c)):
          x1, y1 = self._rc_to_xy((r, c))
          x2, y2 = x1 + CONNECTOR_SIZE, y1 + CONNECTOR_SIZE
          if x1 <= x <= x2 and y1 <= y <= y2:
            return r, c
    return None
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
    self._wire_bbox[wire] = (x_1, y_1, x_2 + CONNECTOR_SIZE,
        y_2 + CONNECTOR_SIZE)
    length = wire.length()
    fill = 'white'
    if 1 < length < 10:
      fill = WIRE_COLORS[length]
    elif 10 <= length < 50:
      fill = WIRE_COLORS[(length + 9) / 10]
    def draw_wire(wire_id=None):
      if wire_id:
        self._canvas.delete(wire_id)
      new_wire_id = self._canvas.create_rectangle(self._wire_bbox[wire],
          fill=fill, outline=WIRE_OUTLINE)
      self._canvas.tag_bind(new_wire_id, '<Button-1>', lambda event: draw_wire(
          new_wire_id))
    draw_wire()
  def _draw_wires(self):
    """
    Draws all the wires on the proto board.
    """
    for wire in sorted(self._proto_board.get_wires(),
        key=lambda wire: -wire.length()):
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
    if self._show_pwr_gnd_pins:
      self._draw_gnd_pwr_pins()
    self._canvas.pack()
    self.pack()
  def _wire_to_cmax_str(self, wire):
    """
    Returns a CMax representation (when saved in a file) of the given |wire|.
    """
    c1, r1 = loc_to_cmax_rep(wire.loc_1)
    c2, r2 = loc_to_cmax_rep(wire.loc_2)
    return 'wire: (%d,%d)--(%d,%d)' % (c1, r1, c2, r2)
  def _to_cmax_str(self):
    """
    Returns a string CMax representation of the proto board we are visualizing.
    """
    # header
    lines = ['#CMax circuit']
    # wires
    for wire in self._proto_board.get_wires():
      lines.append(self._wire_to_cmax_str(wire))
    # circuit pieces
    for piece in self._proto_board.get_pieces():
      cmax_str = piece.to_cmax_str()
      if cmax_str:
        lines.append(cmax_str)
    # power and ground pins
    if self._show_pwr_gnd_pins:
      lines.append('+10: (61,20)')
      lines.append('gnd: (61,19)')
    return '\n'.join(lines)
  def _save_as_cmax_file(self):
    """
    Presents a dialog box that will save the proto board we are visualizing as a
        CMax file.
    """
    file_name = asksaveasfilename(title='Save as CMax file ...',
        filetypes=[('CMax files', CMAX_FILE_EXTENSION)])
    if file_name and not file_name.endswith(CMAX_FILE_EXTENSION):
      file_name += CMAX_FILE_EXTENSION
    if file_name:
      save_file = open(file_name, 'w')
      save_file.write(self._to_cmax_str())
      save_file.close()
  def _setup_menu(self):
    """
    Sets up a menu that lets the user save the proto board we are visualizing as
        a CMax file.
    """
    menu = Menu(self._parent, tearoff=0)
    save_menu = Menu(menu, tearoff=0)
    save_menu.add_command(label='Save as CMax file',
        command=self._save_as_cmax_file)
    menu.add_cascade(label='File', menu=save_menu)
    self._parent.config(menu=menu)

def visualize_proto_board(proto_board, toplevel, show_pwr_gnd_pins=True):
  """
  Displays a nice window portraying the given |proto_board|.
  """
  Proto_Board_Visualizer(toplevel, proto_board, show_pwr_gnd_pins)
