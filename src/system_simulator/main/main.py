"""
Runs system simulator.
TODO(mikemeko): bug: USR or FR blocks UI.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from analyze_board import run_analysis
from constants import APP_NAME
from constants import DEV_STAGE
from constants import FILE_EXTENSION
from constants import INIT_UI_HELP
from constants import IO_PADDING
from core.gui.board import Board
from core.gui.components import Wire
from core.gui.components import Wire_Connector_Drawable
from core.gui.constants import CTRL_DOWN
from core.gui.constants import INFO
from core.gui.constants import LEFT
from core.gui.constants import RIGHT
from core.gui.palette import Palette
from core.save.save import open_board
from core.save.save import request_save_board
from core.save.save import save_board
from core.save.util import strip_file_name
from system_drawables import Adder_Drawable
from system_drawables import Delay_Drawable
from system_drawables import FR_Run_Drawable
from system_drawables import Gain_Drawable
from system_drawables import IO_X_Drawable
from system_drawables import IO_Y_Drawable
from system_drawables import PZD_Run_Drawable
from system_drawables import USR_Run_Drawable
from system_simulator.simulation.frequency_response import (
    plot_frequency_response)
from system_simulator.simulation.pole_zero_diagram import (
    plot_pole_zero_diagram)
from system_simulator.simulation.unit_sample_response import (
    plot_unit_sample_response)
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
    Clears the board and puts the the input (X) and output (Y) drawables.
    """
    global board
    # clear board
    board.clear()
    # create input and output drawables
    inp = IO_X_Drawable()
    board.add_drawable(inp, (IO_PADDING, (board.height - inp.height) / 2))
    out = IO_Y_Drawable()
    board.add_drawable(out, (board.width - out.width - IO_PADDING,
        (board.height - out.height) / 2))
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
    deserializers = (Adder_Drawable, Delay_Drawable, Gain_Drawable,
        IO_X_Drawable, IO_Y_Drawable, Wire_Connector_Drawable, Wire)
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
  # create empty board
  board = Board(root, on_changed=on_changed, on_exit=request_save)
  init_board()
  # create palette
  palette = Palette(root, board)
  # add DT LTI system components to palette
  palette.add_drawable_type(Gain_Drawable, LEFT, None,
      on_gain_changed=lambda: board.set_changed(True))
  palette.add_drawable_type(Delay_Drawable, LEFT, None)
  palette.add_drawable_type(Adder_Drawable, LEFT, None)
  # add buttons to create PZR and USR
  palette.add_drawable_type(PZD_Run_Drawable, RIGHT,
      lambda event: run_analysis(board, plot_pole_zero_diagram))
  palette.add_drawable_type(USR_Run_Drawable, RIGHT,
      lambda event: run_analysis(board, plot_unit_sample_response))
  palette.add_drawable_type(FR_Run_Drawable, RIGHT,
      lambda event: run_analysis(board, plot_frequency_response))
  # shortcuts
  board.add_key_binding('f', lambda: run_analysis(board,
      plot_frequency_response))
  board.add_key_binding('n', new_file, CTRL_DOWN)
  board.add_key_binding('o', open_file, CTRL_DOWN)
  board.add_key_binding('p', lambda: run_analysis(board,
      plot_pole_zero_diagram))
  board.add_key_binding('q', board.quit, CTRL_DOWN)
  board.add_key_binding('s', save_file, CTRL_DOWN)
  board.add_key_binding('u', lambda: run_analysis(board,
      plot_unit_sample_response))
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
  analyze_menu.add_command(label='FR', command=lambda: run_analysis(board,
      plot_frequency_response), accelerator='F')
  analyze_menu.add_command(label='PZD', command=lambda: run_analysis(board,
      plot_pole_zero_diagram), accelerator='P')
  analyze_menu.add_command(label='USR', command=lambda: run_analysis(board,
      plot_unit_sample_response), accelerator='U')
  menu.add_cascade(label='Analyze', menu=analyze_menu)
  root.config(menu=menu)
  # some UI help
  board.display_message(INIT_UI_HELP, INFO)
  # run main loop
  root.mainloop()
