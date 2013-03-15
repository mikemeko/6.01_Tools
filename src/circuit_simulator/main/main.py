"""
Runs circuit simulator.
TODO(mikemeko): code here and system_simulator/main are almost identical,
    maybe there should be an app runner.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from analyze_board import run_analysis
from circuit_drawables import Ground_Drawable
from circuit_drawables import Op_Amp_Drawable
from circuit_drawables import Power_Drawable
from circuit_drawables import Probe_Minus_Drawable
from circuit_drawables import Probe_Plus_Drawable
from circuit_drawables import Resistor_Drawable
from circuit_drawables import Simulate_Run_Drawable
from constants import APP_NAME
from constants import DEV_STAGE
from constants import FILE_EXTENSION
from constants import PALETTE_HEIGHT
from constants import PROBE_INIT_PADDING
from constants import PROBE_SIZE
from core.gui.board import Board
from core.gui.components import Wire
from core.gui.components import Wire_Connector_Drawable
from core.gui.constants import CTRL_DOWN
from core.gui.constants import INFO
from core.gui.constants import LEFT
from core.gui.constants import RIGHT
from core.gui.constants import ERROR
from core.gui.constants import WARNING
from core.gui.palette import Palette
from core.save.save import open_board
from core.save.save import request_save_board
from core.save.save import save_board
from core.save.util import strip_file_name
from Tkinter import Menu
from Tkinter import Tk

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
  def open_file():
    """
    Opens a saved board.
    """
    global board
    global file_name
    # if the board has been changed, request save first
    request_save()
    # open a new board
    deserializers = (Power_Drawable, Ground_Drawable, Probe_Plus_Drawable,
        Probe_Minus_Drawable, Resistor_Drawable, Op_Amp_Drawable,
        Wire_Connector_Drawable, Wire)
    new_file_name = open_board(board, file_name, deserializers, APP_NAME,
        FILE_EXTENSION)
    if new_file_name:
      # update to new file name
      file_name = new_file_name
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
  def analyze(circuit, probe_plus, probe_minus):
    """
    Displays a message on the board showing the voltage difference between
        nodes |probe_plus| and |probe_minus| of the given |circuit|.
    """
    assert probe_plus and probe_minus, 'need both +probe and -probs'
    if not circuit.data:
      board.display_message('Could not solve circuit', ERROR)
      return
    if probe_plus not in circuit.data:
      board.display_message('+probe is disconnected from circuit', WARNING)
    elif probe_minus not in circuit.data:
      board.display_message('-probe is disconnected from circuit', WARNING)
    else:
      probe_difference = circuit.data[probe_plus] - circuit.data[probe_minus]
      board.display_message('%.3f V' % probe_difference, message_type=INFO,
          auto_remove=False)
  # create empty board
  board = Board(root, directed_wires=False, on_changed=on_changed,
      on_exit=request_save)
  init_board()
  # create palette
  palette = Palette(root, board, height=PALETTE_HEIGHT)
  # add circuit components to palette
  palette.add_drawable_type(Power_Drawable, LEFT, None)
  palette.add_drawable_type(Ground_Drawable, LEFT, None)
  palette.add_drawable_type(Resistor_Drawable, LEFT, None,
      on_resistance_changed=lambda: board.set_changed(True))
  palette.add_drawable_type(Op_Amp_Drawable, LEFT, None)
  # add button to simulate circuit
  palette.add_drawable_type(Simulate_Run_Drawable, RIGHT,
      lambda event: run_analysis(board, analyze))
  # shortcuts
  board.add_key_binding('a', lambda: run_analysis(board, analyze))
  board.add_key_binding('n', new_file, CTRL_DOWN)
  board.add_key_binding('o', open_file, CTRL_DOWN)
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
      analyze), accelerator='A')
  menu.add_cascade(label='Analyze', menu=analyze_menu)
  root.config(menu=menu)
  # clear board undo / redo history
  board.clear_action_history()
  # set title
  root.title('%s (%s)' % (APP_NAME, DEV_STAGE))
  # run main loop
  root.mainloop()
