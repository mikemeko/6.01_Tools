"""
Utility methods to save and open DT LTI system boards.
TODO(mikemeko): refactor
  serialize and deserialize should be supported by Drawable
  file_util should be in core
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import ADDER_MARK
from constants import APP_NAME
from constants import DELAY_MARK
from constants import FILE_EXTENSION
from constants import GAIN_MARK
from constants import IO_MARK
from constants import OPEN_FILE_TITLE
from constants import RE_GAIN_VERTICES
from constants import RE_INT
from constants import RE_INT_PAIR
from constants import SAVE_AS_TITLE
from constants import WIRE_CONNECTOR_MARK
from constants import WIRE_MARK
from core.gui.board import Board
from core.gui.components import Wire
from core.gui.components import Wire_Connector_Drawable
from core.util.io import strip_dir
from core.util.io import strip_file_name
from re import match
from system_drawables import Adder_Drawable
from system_drawables import Delay_Drawable
from system_drawables import Gain_Drawable
from system_drawables import IO_Drawable
from system_drawables import IO_X_Drawable
from system_drawables import IO_Y_Drawable
from system_simulator.simulation.constants import X
from system_simulator.simulation.constants import Y
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename

def is_system_drawable(drawable):
  """
  Returns True if |drawable| is a Drawable that can be found in a DT LTI system
      board, False otherwise.
  """
  return isinstance(drawable, (Adder_Drawable, Delay_Drawable, Gain_Drawable,
      IO_Drawable, Wire_Connector_Drawable))

def serialize_system_drawable(drawable, offset):
  """
  Serializes the given |drawable| that is placed at the given |offset| on the
      board.
  """
  assert is_system_drawable(drawable), ('drawable must be a DT LTI system '
      'drawable')
  # adder
  if isinstance(drawable, Adder_Drawable):
    return '%s %d %s' % (ADDER_MARK, drawable.connector_flags, str(offset))
  # delay
  elif isinstance(drawable, Delay_Drawable):
    return '%s %d %s' % (DELAY_MARK, drawable.connector_flags, str(offset))
  # gain
  elif isinstance(drawable, Gain_Drawable):
    return '%s %s %s %s' % (GAIN_MARK, drawable.get_K(),
        str(drawable.vertices), str(offset))
  # X or Y
  elif isinstance(drawable, IO_Drawable):
    return '%s %s %s' % (IO_MARK, drawable.signal, str(offset))
  # wire connector
  elif isinstance(drawable, Wire_Connector_Drawable):
    return '%s %s' % (WIRE_CONNECTOR_MARK, offset)
  else:
    # should never get here
    raise Exception('Unexpected Drawable type')

def serialize_wire(wire):
  """
  Serializes the given |wire|.
  """
  assert isinstance(wire, Wire), 'wire must be a Wire'
  return '%s %s %s' % (WIRE_MARK, str(wire.start_connector.center),
      str(wire.end_connector.center))

def deserialize_item(item_str, board):
  """
  Deserializes the given |item_str| and adds it appropriately to the |board|.
  """
  assert isinstance(item_str, str), 'item_str must be a string'
  assert isinstance(board, Board), 'board must be a Board'
  # adder
  adder_match = match(r'%s %s %s' % (ADDER_MARK, RE_INT, RE_INT_PAIR),
      item_str)
  if adder_match:
    connector_flags, ox, oy = map(int, adder_match.groups())
    board.add_drawable(Adder_Drawable(connector_flags), (ox, oy))
    return
  # delay
  delay_match = match(r'%s %s %s' % (DELAY_MARK, RE_INT, RE_INT_PAIR),
      item_str)
  if delay_match:
    connector_flags, ox, oy = map(int, delay_match.groups())
    board.add_drawable(Delay_Drawable(connector_flags), (ox, oy))
    return
  # gain
  gain_match = match(r'%s (.+) %s %s' % (GAIN_MARK, RE_GAIN_VERTICES,
      RE_INT_PAIR), item_str)
  if gain_match:
    K = gain_match.group(1)
    x1, y1, x2, y2, x3, y3, ox, oy = map(int, gain_match.groups()[1:])
    gain_drawable = Gain_Drawable(on_gain_changed=lambda: board.set_changed(
        True), vertices=(x1, y1, x2, y2, x3, y3))
    board.add_drawable(gain_drawable, (ox, oy))
    gain_drawable.set_K(K)
    return
  # X or Y
  io_match = match(r'%s (\w+) %s' % (IO_MARK, RE_INT_PAIR), item_str)
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
  # wire connector
  wire_connector_match = match(r'%s %s' % (WIRE_CONNECTOR_MARK, RE_INT_PAIR),
      item_str)
  if wire_connector_match:
    ox, oy = map(int, wire_connector_match.groups())
    board.add_drawable(Wire_Connector_Drawable(), (ox, oy))
    return
  # wire
  wire_match = match(r'%s %s %s' % (WIRE_MARK, RE_INT_PAIR, RE_INT_PAIR),
      item_str)
  if wire_match:
    x1, y1, x2, y2 = map(int, wire_match.groups())
    board.add_wire(x1, y1, x2, y2)
    return
  # should never get here
  raise Exception('Could not deserialize serialized item: %s' % item_str)

def get_board_rep(board):
  """
  Serializes the DT LTI system drawn on the given |board|
  """
  assert isinstance(board, Board), 'board must be a Board'
  rep = []
  # record all drawables on the board
  for drawable in board.get_drawables():
    rep.append(serialize_system_drawable(drawable, board.get_drawable_offset(
        drawable)))
  # record all wires on the board
  rep.extend(map(serialize_wire, reduce(set.union, (drawable.wires() for
      drawable in board.get_drawables()), set())))
  # delimit with line breaks
  return '\n'.join(rep)

def save_board(board, file_name):
  """
  Saves the given |board|. If the given |file_name| is not valid, asks the user
      for a new file name.
  Returns the file name that was used.
  """
  assert isinstance(board, Board), 'board must be a Board'
  if not file_name or not file_name.endswith(FILE_EXTENSION):
    # if valid file name is not provided, ask for one
    file_name = asksaveasfilename(title=SAVE_AS_TITLE,
        filetypes=[('%s files' % APP_NAME, FILE_EXTENSION)])
    # ensure extension is tagged
    if file_name and not file_name.endswith(FILE_EXTENSION):
      file_name += FILE_EXTENSION
  if file_name:
    # write serialized board into file
    save_file = open(file_name, 'w')
    save_file.write(get_board_rep(board))
    save_file.close()
  return file_name

def open_board(board, current_file_name):
  """
  Opens a new system and adds the components to the given |board|.
  |current_file_name| is the path for the board currently open. It is used to
      suggest what new file to open.
  Returns the name of the file that was openned, or '' if no file was openned.
  """
  assert isinstance(board, Board), 'board must be a Board'
  file_name = askopenfilename(title=OPEN_FILE_TITLE,
      filetypes=[('%s files' % APP_NAME, FILE_EXTENSION)],
      initialfile=strip_file_name(current_file_name),
      initialdir=strip_dir(current_file_name))
  if file_name:
    assert file_name.endswith(FILE_EXTENSION), 'invalid DT LTI system file'
    # clear board
    board.clear()
    # update board with new system
    open_file = open(file_name, 'r')
    for line in open_file:
      deserialize_item(line, board)
    open_file.close()
  return file_name
