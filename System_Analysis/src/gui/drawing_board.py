"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import DRAWING_BOARD_BACKGROUND_COLOR
from constants import DRAWING_BOARD_HEIGHT
from constants import DRAWING_BOARD_MARKER_COLOR
from constants import DRAWING_BOARD_MARKER_SEPARATION
from constants import DRAWING_BOARD_MARKER_RADIUS
from constants import DRAWING_BOARD_WIDHT
from Tkinter import Canvas
from Tkinter import Frame
from Tkinter import Tk

class Drawing_Board(Frame):
  """
  TODO(mikemeko)
  """
  def __init__(self, parent, width=DRAWING_BOARD_WIDHT,
      height=DRAWING_BOARD_HEIGHT):
    """
    TODO(mikemeko)
    """
    Frame.__init__(self, parent)
    self.width = width
    self.height = height
    self._setup_drawing_board()
  def _setup_drawing_board(self):
    """
    TODO(mikemeko)
    """
    canvas = Canvas(self, width=self.width, height=self.height)
    for r in xrange(0, self.width, DRAWING_BOARD_MARKER_SEPARATION):
      for c in xrange(0, self.height, DRAWING_BOARD_MARKER_SEPARATION):
        canvas.create_oval(r - DRAWING_BOARD_MARKER_RADIUS,
            c - DRAWING_BOARD_MARKER_RADIUS, r + DRAWING_BOARD_MARKER_RADIUS,
            c + DRAWING_BOARD_MARKER_RADIUS, fill=DRAWING_BOARD_MARKER_COLOR)
    canvas.configure(background=DRAWING_BOARD_BACKGROUND_COLOR)
    canvas.pack()
    self.configure(background=DRAWING_BOARD_BACKGROUND_COLOR)
    self.pack()
  def show(self):
    """
    TODO(mikemeko)
    """
    self.mainloop()

if __name__ == '__main__':
  root = Tk()
  root.resizable(0, 0)
  Drawing_Board(root).show()
