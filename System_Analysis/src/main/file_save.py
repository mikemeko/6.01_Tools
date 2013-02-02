"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import APP_NAME
from core.constants import X
from core.constants import Y
from gui.board import Board
from gui.components import Wire
from gui.components import Wire_Connector_Drawable
from re import match
from system_drawables import Adder_Drawable
from system_drawables import Delay_Drawable
from system_drawables import Gain_Drawable
from system_drawables import IO_Drawable
from system_drawables import IO_X_Drawable
from system_drawables import IO_Y_Drawable
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename

def is_system_drawable(drawable):
  """
  TODO(mikemeko)
  """
  return isinstance(drawable, (Adder_Drawable, Delay_Drawable, Gain_Drawable,
      IO_Drawable, Wire_Connector_Drawable))

def serialize_system_drawable(drawable, offset):
  """
  TODO(mikemeko)
  """
  assert is_system_drawable(drawable)
  if isinstance(drawable, Adder_Drawable):
    return 'Adder %d %s' % (drawable.connector_flags, str(offset))
  elif isinstance(drawable, Delay_Drawable):
    return 'Delay %d %s' % (drawable.connector_flags, str(offset))
  elif isinstance(drawable, Gain_Drawable):
    return 'Gain %s %s %s' % (drawable.get_K(), str(drawable.vertices),
        str(offset))
  elif isinstance(drawable, IO_Drawable):
    return 'IO %s %s' % (drawable.signal, str(offset))
  elif isinstance(drawable, Wire_Connector_Drawable):
    return 'Wire connector %s %s' % (drawable.label, offset)
  else:
    # should never get here
    raise Exception('Unexpected Drawable type')

def serialize_wire(wire):
  """
  TODO(mikemeko)
  """
  assert isinstance(wire, Wire)
  return 'Wire %s %s %s' % (wire.label, str(wire.start_connector.center),
      str(wire.end_connector.center))

def deserialize_item(item_str, board):
  """
  TODO(mikemeko)
  """
  # TODO(mikemeko): greate nice regexps to reuse at places
  assert isinstance(item_str, str)
  assert isinstance(board, Board), 'board must be a Board'
  adder_match = match(r'Adder (\d+) \((\d+), (\d+)\)', item_str)
  if adder_match:
    connector_flags, ox, oy = map(int, adder_match.groups())
    board.add_drawable(Adder_Drawable(connector_flags), (ox, oy))
    return
  delay_match = match(r'Delay (\d+) \((\d+), (\d+)\)', item_str)
  if delay_match:
    connector_flags, ox, oy = map(int, delay_match.groups())
    board.add_drawable(Delay_Drawable(connector_flags), (ox, oy))
    return
  gain_match = match(r'Gain ([-+]?\d*[.]?\d+) \((\d+), (\d+), (\d+), (\d+), '
      '(\d+), (\d+)\) \((\d+), (\d+)\)', item_str)
  if gain_match:
    K = float(gain_match.group(1))
    x1, y1, x2, y2, x3, y3, ox, oy = map(int, gain_match.groups()[1:])
    gain_drawable = Gain_Drawable((x1, y1, x2, y2, x3, y3))
    board.add_drawable(gain_drawable, (ox, oy))
    gain_drawable.set_K(K)
    return
  io_match = match(r'IO (\w+) \((\d+), (\d+)\)', item_str)
  if io_match:
    signal = io_match.group(1)
    ox, oy = map(int, io_match.groups()[1:])
    if signal is X:
      board.add_drawable(IO_X_Drawable(), (ox, oy))
    elif signal is Y:
      board.add_drawable(IO_Y_Drawable(), (ox, oy))
    else:
      # should never get here
      raise Exception('Unexpected IO signal')
    return
  wire_connector_match = match(r'Wire connector (\w+) \((\d+), (\d+)\)',
      item_str)
  if wire_connector_match:
    label = wire_connector_match.group(1)
    ox, oy = map(int, wire_connector_match.groups()[1:])
    board.add_drawable(Wire_Connector_Drawable(label), (ox, oy))
    return
  wire_match = match(r'Wire (\w+) \((\d+), (\d+)\) \((\d+), (\d+)\)', item_str)
  if wire_match:
    label = wire_match.group(1)
    x1, y1, x2, y2 = map(int, wire_match.groups()[1:])
    board.add_wire(x1, y1, x2, y2, label)
    return
  # should never get here
  raise Exception('Could not deserialize serialized item')

def get_board_rep(board):
  """
  TODO(mikemeko)
  """
  assert isinstance(board, Board), 'board must be a Board'
  rep = []
  # first record all drawables on the board (except for IO drawables)
  for drawable in board.get_drawables():
    assert is_system_drawable(drawable)
    rep.append(serialize_system_drawable(drawable, board.get_drawable_offset(
        drawable)))
  # then record all wires on the board
  rep.extend(map(serialize_wire, reduce(set.union, (drawable.wires() for
      drawable in board.get_drawables()), set())))
  return '\n'.join(rep)

def save_board(board, file_name):
  """
  TODO(mikemeko)
  """
  assert isinstance(board, Board), 'board must be a Board'
  if not file_name:
    # TODO(mikemeko): not .sys
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

def open_board(board):
  """
  TODO(mikemeko)
  """
  assert isinstance(board, Board), 'board must be a Board'
  file_name = askopenfilename(title="Open File ...",
      filetypes=[('%s files' % APP_NAME,'.sys')])
  # TODO(mikemeko): check that file name is valid
  # clear the board
  if file_name:
    board.clear()
    open_file = open(file_name, 'r')
    for line in open_file:
      deserialize_item(line, board)
    open_file.close()
  return file_name

def build_board_from_rep(board, rep):
  """
  TODO(mikemeko)
  """
