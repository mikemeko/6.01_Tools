"""
TODO: docstring
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.gui.board import Board
from core.gui.constants import CTRL_DOWN
from core.gui.palette import Palette
from core.save.save import get_board_file_name
from core.save.save import open_board_from_file
from core.save.save import request_save_board
from core.save.save import save_board
from core.save.util import strip_file_name
from Tkinter import Menu
from Tkinter import Tk

class App_Runner:
  """
  TODO: docstring
  """
  def __init__(self, on_init, app_name, dev_stage, file_extension,
      deserializers, board_width, board_height, palette_height,
      directed_wires, init_file=None):
    """
    TODO: docstring
    """
    self._on_init = on_init
    self._app_name = app_name
    self._dev_stage = dev_stage
    self._file_extension = file_extension
    self._deserializers = deserializers
    self._board_width = board_width
    self._board_height = board_height
    self._palette_height = palette_height
    self._directed_wires = directed_wires
    self._init_file = init_file
    self._init()
    self._setup_menu()
    self._setup_shortcuts()
  def _init(self):
    """
    TODO: docstring
    """
    self._file_name = None
    self._root = Tk()
    self._root.resizable(0, 0)
    self.board = Board(self._root, width=self._board_width,
        height=self._board_height, directed_wires=self._directed_wires,
        on_changed=self._on_changed, on_exit=self._request_save)
    self._init_board()
    self.palette = Palette(self._root, self.board, width=self._board_width,
        height=self._palette_height)
  def _setup_menu(self):
    """
    TODO: docstring
    """
    self._menu = Menu(self._root, tearoff=0)
    file_menu = Menu(self._menu, tearoff=0)
    file_menu.add_command(label='New', command=self._new_file,
        accelerator='Ctrl+N')
    file_menu.add_command(label='Open', command=self._open_file,
        accelerator='Ctrl+O')
    file_menu.add_command(label='Save', command=self._save_file,
        accelerator='Ctrl+S')
    file_menu.add_separator()
    file_menu.add_command(label='Quit', command=self.board.quit,
        accelerator='Ctrl+Q')
    self._menu.add_cascade(label='File', menu=file_menu)
    edit_menu = Menu(self._menu, tearoff=0)
    edit_menu.add_command(label='Undo', command=self.board.undo,
        accelerator='Ctrl+Z')
    edit_menu.add_command(label='Redo', command=self.board.redo,
        accelerator='Ctrl+Y')
    self._menu.add_cascade(label='Edit', menu=edit_menu)
    self._root.config(menu=self._menu)
  def _setup_shortcuts(self):
    """
    TODO: docstring
    """
    self.board.add_key_binding('n', self._new_file, CTRL_DOWN)
    self.board.add_key_binding('o', self._open_file, CTRL_DOWN)
    self.board.add_key_binding('q', self.board.quit, CTRL_DOWN)
    self.board.add_key_binding('s', self._save_file, CTRL_DOWN)
    self.board.add_key_binding('y', self.board.redo, CTRL_DOWN)
    self.board.add_key_binding('z', self.board.undo, CTRL_DOWN)
  def _init_board(self):
    """
    TODO: docstring
    """
    self.board.clear()
    self._on_init(self.board)
    self.board.reset()
  def _on_changed(self, board_changed):
    """
    TODO: docstring
    """
    self._root.title('%s (%s) %s %s' % (self._app_name, self._dev_stage,
        strip_file_name(self._file_name), '*' if board_changed else ''))
  def _save_file(self):
    """
    TODO: docstring
    """
    saved_file_name = save_board(self.board, self._file_name, self._app_name,
        self._file_extension)
    if saved_file_name:
      self._file_name = saved_file_name
      self.board.set_changed(False)
  def _request_save(self):
    """
    TODO: docstring
    """
    if self.board.changed() and request_save_board():
      self._save_file()
  def _open_file(self, new_file_name=None):
    """
    TODO: docstring
    """
    self._request_save()
    new_file_name = new_file_name or get_board_file_name(self._file_name,
        self._app_name, self._file_extension)
    if open_board_from_file(self.board, new_file_name, self._deserializers,
        self._file_extension):
      self._file_name = new_file_name
      self._on_changed(False)
    self.board.reset_cursor_state()
  def _new_file(self):
    """
    TODO: docstring
    """
    self._request_save()
    self._file_name = None
    self._init_board()
  def run(self):
    """
    TODO: docstring
    """
    self.board.clear_action_history()
    self._root.title('%s (%s)' % (self._app_name, self._dev_stage))
    if self._init_file:
      self._open_file(self._init_file)
    self._root.mainloop()
