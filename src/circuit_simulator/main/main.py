"""
Runs circuit simulator.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_drawables import Ground
from circuit_drawables import Power
from constants import APP_NAME
from constants import DEV_STAGE
from core.gui.board import Board
from core.gui.constants import LEFT
from core.gui.palette import Palette
from Tkinter import Tk

if __name__ == '__main__':
  # create root
  root = Tk()
  root.resizable(0, 0)
  # create empty board
  board = Board(root)
  # create palette
  palette = Palette(root, board)
  # add circuit components to palette
  palette.add_drawable_type(Ground, LEFT, None)
  palette.add_drawable_type(Power, LEFT, None)
  # set title
  root.title('%s (%s)' % (APP_NAME, DEV_STAGE))
  # run main loop
  root.mainloop()
