"""
Runs system simulator.
TODO(mikemeko): bug: USR or FR blocks UI.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from analyze_board import run_analysis
from constants import APP_NAME
from constants import DEV_STAGE
from constants import FILE_EXTENSION
from constants import IO_PADDING
from core.gui.app_runner import App_Runner
from core.gui.components import Wire
from core.gui.components import Wire_Connector_Drawable
from core.gui.constants import BOARD_HEIGHT
from core.gui.constants import BOARD_WIDTH
from core.gui.constants import LEFT
from core.gui.constants import PALETTE_HEIGHT
from core.gui.constants import RIGHT
from sys import argv
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
from Tkinter import Toplevel

def on_init(board):
  """
  TODO: docstring
  """
  # create input and output drawables
  inp = IO_X_Drawable()
  board.add_drawable(inp, (IO_PADDING, (board.height - inp.height) / 2))
  out = IO_Y_Drawable()
  board.add_drawable(out, (board.width - out.width - IO_PADDING,
      (board.height - out.height) / 2))

if __name__ == '__main__':
  app_runner = App_Runner(on_init, APP_NAME, DEV_STAGE, FILE_EXTENSION, (
      Adder_Drawable, Delay_Drawable, Gain_Drawable, IO_X_Drawable,
      IO_Y_Drawable, Wire_Connector_Drawable, Wire), BOARD_WIDTH, BOARD_HEIGHT,
      PALETTE_HEIGHT, True, argv[1] if len(argv) > 1 else None)
  def pzd(system):
    """
    Plots the pole-zero diagram of the given |system|.
    """
    plot_pole_zero_diagram(system, Toplevel())
  # add DT LTI system components to palette
  app_runner.palette.add_drawable_type(Gain_Drawable, LEFT, None,
      board=app_runner.board)
  app_runner.palette.add_drawable_type(Delay_Drawable, LEFT, None)
  app_runner.palette.add_drawable_type(Adder_Drawable, LEFT, None)
  # add buttons to create PZR and USR
  app_runner.palette.add_drawable_type(PZD_Run_Drawable, RIGHT,
      lambda event: run_analysis(app_runner.board, pzd))
  app_runner.palette.add_drawable_type(USR_Run_Drawable, RIGHT,
      lambda event: run_analysis(app_runner.board, plot_unit_sample_response))
  app_runner.palette.add_drawable_type(FR_Run_Drawable, RIGHT,
      lambda event: run_analysis(app_runner.board, plot_frequency_response))
  # shortcuts
  app_runner.board.add_key_binding('f', lambda: run_analysis(app_runner.board,
      plot_frequency_response))
  app_runner.board.add_key_binding('p', lambda: run_analysis(app_runner.board,
      pzd))
  app_runner.board.add_key_binding('u', lambda: run_analysis(app_runner.board,
      plot_unit_sample_response))
  # run
  app_runner.run()
