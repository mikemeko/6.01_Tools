"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import BACKGROUND
from constants import HEIGHT
from constants import WIDTH
from Tkinter import Canvas
from Tkinter import Frame
from Tkinter import mainloop
from Tkinter import Tk

class Proto_Board_Visualization(Frame):
  """
  TODO(mikemeko)
  """
  def __init__(self, parent):
    Frame.__init__(self, parent, background=BACKGROUND)
    self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
    self._set_up()
  def _set_up(self):
    self.canvas.pack()
    self.pack()

if __name__ == '__main__':
  root = Tk()
  vis = Proto_Board_Visualization(root)
  mainloop()
