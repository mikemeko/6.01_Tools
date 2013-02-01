"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import APP_NAME
from gui.board import Board
from gui.components import Wire
from gui.components import Wire_Connector_Drawable
from system_drawables import Adder_Drawable
from system_drawables import Delay_Drawable
from system_drawables import Gain_Drawable
from system_drawables import IO_Drawable
from tkFileDialog import asksaveasfilename

def is_system_drawable(drawable):
  """
  TODO(mikemeko)
  """
  return isinstance(drawable, (Adder_Drawable, Delay_Drawable, Gain_Drawable,
      IO_Drawable, Wire_Connector_Drawable))

def wire_rep(wire):
  """
  TODO(mikemeko)
  """
  assert isinstance(wire, Wire)
  return 'Wire %s %s' % (str(wire.start_connector.center),
      str(wire.end_connector.center))

def get_board_rep(board):
  """
  TODO(mikemeko)
  """
  assert isinstance(board, Board), 'board must be a Board'
  rep = []
  # first record all drawables on the board (except for IO drawables)
  for drawable in board.get_drawables():
    assert is_system_drawable(drawable)
    if not isinstance(drawable, IO_Drawable):
      rep.append(drawable.get_rep(board.get_drawable_offset(drawable)))
  # then record all wires on the board
  rep.extend(map(wire_rep, reduce(set.union, (drawable.wires() for drawable in
      board.get_drawables()), set())))
  return '\n'.join(rep)

def save_board(board, file_name):
  """
  TODO(mikemeko)
  """
  assert isinstance(board, Board), 'board must be a Board'
  if not file_name:
    # if file name is not provided, ask for one
    file_name = asksaveasfilename(title='Save file as ...',
        filetypes=[('%s files' % APP_NAME,'.sys')])
    # TODO(mikemeko): attache .sys if not already provided
  else:
    # TODO(mikemeko): check that file name is valid
    pass
  save_file = open(file_name, 'w')
  save_file.write(get_board_rep(board))
  save_file.close()
  return file_name

def build_board_from_rep(board, rep):
  """
  TODO(mikemeko)
  """
