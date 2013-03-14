"""
Methods to save and open boards.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import OPEN_FILE_TITLE
from constants import REQUEST_SAVE_MESSAGE
from constants import REQUEST_SAVE_TITLE
from constants import SAVE_AS_TITLE
from core.gui.board import Board
from core.gui.components import Wire
from tkFileDialog import askopenfilename
from tkMessageBox import askquestion
from tkFileDialog import asksaveasfilename
from util import strip_dir
from util import strip_file_name

def get_board_rep(board):
  """
  Returns a string representing the content of the given |board|.
  Note that the order (i.e. Drawables then Wires) is important to how the rest
      of the methods here behave.
  """
  assert isinstance(board, Board), 'board must be a Board'
  rep = []
  # record all drawables on the board
  for drawable in board.get_drawables():
    rep.append(drawable.serialize(board.get_drawable_offset(drawable)))
  # record all wires on the board
  rep.extend(map(Wire.serialize, reduce(set.union, (drawable.wires() for
      drawable in board.get_drawables()), set())))
  # delimit with line breaks
  return '\n'.join(rep)

def save_board(board, file_name, file_type, file_extension):
  """
  Saves the given |board|. If the given |file_name| is not valid, asks the user
      for a new file name of with given |file_extension|. |file_type| is a
      description of the intended type of file to help the user.
  Returns the file name that was used to save the board.
  """
  assert isinstance(board, Board), 'board must be a Board'
  if not file_name or not file_name.endswith(file_extension):
    # if valid file name is not provided, ask for one
    file_name = asksaveasfilename(title=SAVE_AS_TITLE,
        filetypes=[('%s files' % file_type, file_extension)])
    # ensure extension is tagged
    if file_name and not file_name.endswith(file_extension):
      file_name += file_extension
  if file_name:
    # write serialized board into file
    save_file = open(file_name, 'w')
    save_file.write(get_board_rep(board))
    save_file.close()
  return file_name

def request_save_board():
  """
  Presents a pop-up window asking the user whether to save the file. Returns
      True if the user responds yes, False otherwise.
  """
  return askquestion(title=REQUEST_SAVE_TITLE,
      message=REQUEST_SAVE_MESSAGE) == 'yes'

def open_board(board, current_file_name, deserializers, file_type,
    file_extension):
  """
  Opens a saved board and sets the content of the given |board| to be that
      saved content. The content of the file is determined using the given
      |deserializers|. |current_file_name| is the path for the board currently
      open. It is used to suggest what new file to open.
  Returns the name of the file that was openned, or '' if no file was openned.
  """
  assert isinstance(board, Board), 'board must be a Board'
  file_name = askopenfilename(title=OPEN_FILE_TITLE,
      filetypes=[('%s files' % file_type, file_extension)],
      initialfile=strip_file_name(current_file_name),
      initialdir=strip_dir(current_file_name))
  if file_name:
    assert file_name.endswith(file_extension), 'invalid file type'
    # clear board
    board.clear()
    # update board with content
    open_file = open(file_name, 'r')
    for line in open_file:
      for deserializer in deserializers:
        if deserializer.deserialize(line, board):
          break
    open_file.close()
    board.reset()
  return file_name
