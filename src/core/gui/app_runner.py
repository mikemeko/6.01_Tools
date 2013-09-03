"""
Bare bones infrastructure to run an app using a Board and a Palette.
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
  App runner that uses a Board and a Palette.
  """
  def __init__(self, on_init, app_name, dev_stage, file_extension,
      deserializers, board_width, board_height, palette_height,
      directed_wires, label_tooltips_enabled, init_file=None):
    """
    |on_init|: method called every time a new board of this app's type is
        created.
    |app_name|: name of this app.
    |dev_stage|: development stage of this app.
    |file_extension|: the file extension used for boards of this app's type.
    |deserializers|: drawabel types to open files of this app's type.
    |board_width|, |board_height|: board dimensions.
    |palette_height|: height of palette, width will be the same as board width.
    |directed_wires|: True if the board is to have directed wires, False
        otherwise.
    |label_tooltips_enabled|: if True, show wire and drawable label tooltips.
    |init_file|: file to open at init time.
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
    self._label_tooltips_enabled = label_tooltips_enabled
    self._init_file = init_file
    self._init()
    self._setup_menu()
    self._setup_shortcuts()
  def _init(self):
    """
    Creates the board and palette.
    """
    self._file_name = None
    self._root = Tk()
    self._root.resizable(0, 0)
    self.board = Board(self._root, width=self._board_width,
        height=self._board_height, directed_wires=self._directed_wires,
        label_tooltips_enabled=self._label_tooltips_enabled,
        on_changed=self._on_changed, on_exit=self._request_save)
    self._init_board()
    self.palette = Palette(self._root, self.board, width=self._board_width,
        height=self._palette_height)
  def _setup_menu(self):
    """
    Creates the menu.
    """
    menu = Menu(self._root, tearoff=0)
    file_menu = Menu(menu, tearoff=0)
    file_menu.add_command(label='New', command=self._new_file,
        accelerator='Ctrl+N')
    file_menu.add_command(label='Open', command=self._open_file,
        accelerator='Ctrl+O')
    file_menu.add_command(label='Save', command=self._save_file,
        accelerator='Ctrl+S')
    file_menu.add_separator()
    file_menu.add_command(label='Quit', command=self.board.quit,
        accelerator='Ctrl+Q')
    menu.add_cascade(label='File', menu=file_menu)
    edit_menu = Menu(menu, tearoff=0)
    edit_menu.add_command(label='Undo', command=self.board.undo,
        accelerator='Ctrl+Z')
    edit_menu.add_command(label='Redo', command=self.board.redo,
        accelerator='Ctrl+Y')
    menu.add_cascade(label='Edit', menu=edit_menu)
    self._root.config(menu=menu)
  def _setup_shortcuts(self):
    """
    Adds basic shortcuts.
    """
    self.board.parent.bind('<Control-n>', lambda event: self._new_file())
    self.board.parent.bind('<Control-o>', lambda event: self._open_file())
    self.board.parent.bind('<Control-q>', lambda event: self.board.quit())
    self.board.parent.bind('<Control-s>', lambda event: self._save_file())
    self.board.parent.bind('<Control-y>', lambda event: self.board.redo())
    self.board.parent.bind('<Control-z>', lambda event: self.board.undo())
  def _init_board(self):
    """
    (Re)Initializes the board based on this app's specific needs, as per
        self._on_init.
    """
    self.board.clear()
    self._on_init(self.board)
    self.board.reset()
  def _on_changed(self, board_changed):
    """
    Callback for when the board is changed. Updates the title of the app window
        to indicate whether we need to save the file.
    """
    self._root.title('%s (%s) %s %s' % (self._app_name, self._dev_stage,
        strip_file_name(self._file_name), '*' if board_changed else ''))
  def _save_file(self):
    """
    Saves the current state of the app.
    """
    saved_file_name = save_board(self.board, self._file_name, self._app_name,
        self._file_extension)
    if saved_file_name:
      self._file_name = saved_file_name
      self.board.set_changed(False)
  def _request_save(self):
    """
    Requests for a file save if necessary.
    """
    if self.board.changed() and request_save_board():
      self._save_file()
  def _open_file(self, new_file_name=None):
    """
    Opens a saved file of this app's type.
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
    Opens a new file of this app's type.
    """
    self._request_save()
    self._file_name = None
    self._init_board()
  def run(self):
    """
    Runs this app.
    """
    self.board.clear_action_history()
    self._root.title('%s (%s)' % (self._app_name, self._dev_stage))
    if self._init_file:
      self._open_file(self._init_file)
    self._root.mainloop()
