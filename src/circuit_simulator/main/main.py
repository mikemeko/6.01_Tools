"""
Runs circuit simulator.
TODO(mikemeko): code here and system_simulator/main are almost identical,
    maybe there should be an app runner.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from analyze_board import run_analysis
from circuit_drawables import Ground_Drawable
from circuit_drawables import Motor_Connector_Drawable
from circuit_drawables import Op_Amp_Drawable
from circuit_drawables import Pot_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Proto_Board_Run_Drawable
from circuit_drawables import Resistor_Drawable
from circuit_drawables import Simulate_Run_Drawable
from circuit_simulator.proto_board.circuit_piece_placement import (
    loc_pairs_to_connect)
from circuit_simulator.proto_board.circuit_to_circuit_pieces import (
    get_piece_placement)
from circuit_simulator.proto_board.find_proto_board_wiring import find_wiring
from circuit_simulator.proto_board.proto_board import Proto_Board
from circuit_simulator.proto_board.visualization.visualization import (
    visualize_proto_board)
from constants import APP_NAME
from constants import BOARD_HEIGHT
from constants import BOARD_WIDTH
from constants import DEV_STAGE
from constants import FILE_EXTENSION
from constants import PALETTE_HEIGHT
from constants import PROBE_INIT_PADDING
from constants import PROBE_SIZE
from core.gui.board import Board
from core.gui.components import Wire
from core.gui.components import Wire_Connector_Drawable
from core.gui.constants import CTRL_DOWN
from core.gui.constants import LEFT
from core.gui.constants import RIGHT
from core.gui.constants import ERROR
from core.gui.palette import Palette
from core.save.save import get_board_file_name
from core.save.save import open_board_from_file
from core.save.save import request_save_board
from core.save.save import save_board
from core.save.util import strip_file_name
from pylab import figure
from pylab import show
from sys import argv
from Tkinter import Menu
from Tkinter import Tk
from Tkinter import Toplevel

if __name__ == '__main__':
  # create root
  root = Tk()
  root.resizable(0, 0)
  # global variables (sorry!) used by various methods below
  global board
  global file_name
  # no opened file initially
  file_name = None
  def init_board():
    """
    Clears the board and puts the probe drawables.
    """
    global board
    # clear board
    board.clear()
    # create probe drawables
    board.add_drawable(Probe_Plus_Drawable(), (PROBE_INIT_PADDING,
        PROBE_INIT_PADDING))
    board.add_drawable(Probe_Minus_Drawable(), (
        PROBE_SIZE + 2 * PROBE_INIT_PADDING, PROBE_INIT_PADDING))
    board.reset()
  def on_changed(board_changed):
    """
    This will be called every time the board is changed. |board_changed| is
        True if the board has been changed (i.e. requires saving),
        False otherwise.
    """
    global file_name
    # reset title to indicate need for save
    root.title('%s (%s) %s %s' % (APP_NAME, DEV_STAGE,
        strip_file_name(file_name), '*' if board_changed else ''))
  def save_file():
    """
    Saves the current board.
    """
    global board
    global file_name
    # save board
    saved_file_name = save_board(board, file_name, APP_NAME, FILE_EXTENSION)
    if saved_file_name:
      file_name = saved_file_name
      # mark the board unchanged
      board.set_changed(False)
  def request_save():
    """
    Checks if the board has been changed, and asks the user to save the file.
    """
    global board
    if board.changed() and request_save_board():
      save_file()
  def open_file(new_file_name=None):
    """
    Opens a saved board.
    """
    global board
    global file_name
    # if the board has been changed, request save first
    request_save()
    # get a new file name if not given
    new_file_name = new_file_name or get_board_file_name(file_name,
        APP_NAME, FILE_EXTENSION)
    # open a new board with the new file name
    deserializers = (Power_Drawable, Ground_Drawable, Probe_Plus_Drawable,
        Probe_Minus_Drawable, Resistor_Drawable, Op_Amp_Drawable,
        Pot_Drawable, Motor_Connector_Drawable, Wire_Connector_Drawable, Wire)
    if open_board_from_file(board, new_file_name, deserializers,
        FILE_EXTENSION):
      # update to new file name
      file_name = new_file_name
      on_changed(False)
  def new_file():
    """
    Opens a new board.
    """
    global file_name
    # if the board has been changed, request save first
    request_save()
    # update to no file name
    file_name = None
    # reset to empty board
    init_board()
  def simulate(circuit, plotters):
    """
    Displays the plot that are drawn by the |plotters|.
    """
    # ensure that circuit was successfully solved
    if circuit.data:
      # show analysis plots
      for plotter in plotters:
        figure()
        plotter.plot(board, circuit.data)
      show()
    else:
      board.display_message('Could not solve circuit', ERROR)
  def proto_board_layout(circuit, plotters):
    """
    Finds a way to layout the given |circuit| on a proto board and displays the
        discovered proto board.
    """
    placement = get_piece_placement(circuit)
    proto_board = Proto_Board()
    for piece in placement:
      proto_board = proto_board.with_piece(piece)
    proto_board = find_wiring(loc_pairs_to_connect(placement), proto_board)
    visualize_proto_board(proto_board, Toplevel())
  # create empty board
  board = Board(root, width=BOARD_WIDTH, height=BOARD_HEIGHT,
      directed_wires=False, on_changed=on_changed, on_exit=request_save)
  init_board()
  # create palette
  palette = Palette(root, board, width=BOARD_WIDTH, height=PALETTE_HEIGHT)
  # add circuit components to palette
  palette.add_drawable_type(Power_Drawable, LEFT, None)
  palette.add_drawable_type(Ground_Drawable, LEFT, None)
  palette.add_drawable_type(Resistor_Drawable, LEFT, None,
      on_resistance_changed=lambda: board.set_changed(True))
  palette.add_drawable_type(Pot_Drawable, LEFT, None,
      on_signal_file_changed=lambda: board.set_changed(True))
  palette.add_drawable_type(Op_Amp_Drawable, LEFT, None)
  palette.add_drawable_type(Motor_Connector_Drawable, LEFT, None)
  # add buttons to analyze circuit
  palette.add_drawable_type(Simulate_Run_Drawable, RIGHT,
      lambda event: run_analysis(board, simulate))
  palette.add_drawable_type(Proto_Board_Run_Drawable, RIGHT,
      lambda event: run_analysis(board, proto_board_layout))
  # shortcuts
  board.add_key_binding('a', lambda: run_analysis(board, simulate))
  board.add_key_binding('n', new_file, CTRL_DOWN)
  board.add_key_binding('o', open_file, CTRL_DOWN)
  board.add_key_binding('p', lambda: run_analysis(board, proto_board_layout))
  board.add_key_binding('q', board.quit, CTRL_DOWN)
  board.add_key_binding('s', save_file, CTRL_DOWN)
  board.add_key_binding('y', board.redo, CTRL_DOWN)
  board.add_key_binding('z', board.undo, CTRL_DOWN)
  # menu
  menu = Menu(root, tearoff=0)
  file_menu = Menu(menu, tearoff=0)
  file_menu.add_command(label='New', command=new_file, accelerator='Ctrl+N')
  file_menu.add_command(label='Open', command=open_file, accelerator='Ctrl+O')
  file_menu.add_command(label='Save', command=save_file, accelerator='Ctrl+S')
  file_menu.add_separator()
  file_menu.add_command(label='Quit', command=board.quit, accelerator='Ctrl+Q')
  menu.add_cascade(label='File', menu=file_menu)
  edit_menu = Menu(menu, tearoff=0)
  edit_menu.add_command(label='Undo', command=board.undo, accelerator='Ctrl+Z')
  edit_menu.add_command(label='Redo', command=board.redo, accelerator='Ctrl+Y')
  menu.add_cascade(label='Edit', menu=edit_menu)
  analyze_menu = Menu(menu, tearoff=0)
  analyze_menu.add_command(label='Analyze', command=lambda: run_analysis(board,
      simulate), accelerator='A')
  analyze_menu.add_command(label='Proto Board', command=lambda: run_analysis(
      board, proto_board_layout), accelerator='P')
  menu.add_cascade(label='Analyze', menu=analyze_menu)
  root.config(menu=menu)
  # clear board undo / redo history
  board.clear_action_history()
  # set title
  root.title('%s (%s)' % (APP_NAME, DEV_STAGE))
  # open starting file, if given
  if len(argv) > 1:
    open_file(argv[1])
  # run main loop
  root.mainloop()
