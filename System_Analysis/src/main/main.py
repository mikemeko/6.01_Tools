"""
Main.
Runs system analysis tool.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from analyze_board import run_analysis
from constants import APP_NAME
from constants import DEV_STAGE
from constants import IO_PADDING
from constants import X_CONNECTORS
from constants import Y_CONNECTORS
from core.constants import X
from core.constants import Y
from core.pole_zero_diagram import plot_pole_zero_diagram
from core.unit_sample_response import plot_unit_sample_response
from file_save import open_board
from file_save import save_board
from gui.board import Board
from gui.constants import INFO
from gui.constants import LEFT
from gui.constants import RIGHT
from gui.palette import Palette
from system_drawables import Adder_Drawable
from system_drawables import Delay_Drawable
from system_drawables import Gain_Drawable
from system_drawables import IO_Drawable
from system_drawables import PZD_Run_Drawable
from system_drawables import USR_Run_Drawable
from tkMessageBox import askquestion
from Tkinter import Tk

if __name__ == '__main__':
  # create root, board, and palette
  root = Tk()
  root.resizable(0, 0)
  root.title('%s (%s)' % (APP_NAME, DEV_STAGE))
  board = Board(root)
  palette = Palette(root, board)
  # create input and output boxes (added to board automatically)
  inp = IO_Drawable(X, X_CONNECTORS)
  board.add_drawable(inp, (IO_PADDING, (board.height - inp.height) / 2))
  out = IO_Drawable(Y, Y_CONNECTORS)
  board.add_drawable(out, (board.width - out.width - IO_PADDING,
      (board.height - out.height) / 2))
  # mark the board unchanged
  board.reset_changed()
  # add LTI system components to palette
  palette.add_drawable_type(Gain_Drawable, LEFT, None)
  palette.add_drawable_type(Delay_Drawable, LEFT, None)
  palette.add_drawable_type(Adder_Drawable, LEFT, None)
  # add buttons to create pzr and usr
  palette.add_drawable_type(PZD_Run_Drawable, RIGHT,
      lambda event: run_analysis(board, plot_pole_zero_diagram))
  palette.add_drawable_type(USR_Run_Drawable, RIGHT,
      lambda event: run_analysis(board, plot_unit_sample_response))
  # shortcuts
  board.add_key_binding('p', lambda: run_analysis(board,
      plot_pole_zero_diagram))
  board.add_key_binding('u', lambda: run_analysis(board,
      plot_unit_sample_response))
  # file opening / saving
  # TODO(mikemeko): global variable :(
  global file_name
  file_name = None
  def save_file():
    """
    TODO(mikemeko)
    """
    global file_name
    file_name = save_board(board, file_name)
  # TODO(mikemeko): Ctrl-s instead of s
  board.add_key_binding('s', save_file)
  def open_file():
    """
    TODO(mikemeko)
    """
    global file_name
    # save first if the board has been changed
    if board.changed():
      if askquestion(title='Save?',
          message='System has been changed, save first?') == 'yes':
        save_file()
    file_name = open_board(board)
  # TODO(mikemeko): Ctrl-o instead of o
  board.add_key_binding('o', open_file)
  # some UI help
  board.display_message('Ctrl-click to delete.\nShift-click to rotate.', INFO)
  # run main loop
  root.mainloop()
