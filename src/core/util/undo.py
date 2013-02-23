"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Mihchael Mekonnen)'

from core.util.util import is_callable

class Action:
  """
  TODO(mikemeko)
  """
  def __init__(self, do_action, undo_action):
    """
    TODO(mikemeko)
    """
    assert is_callable(do_action)
    assert is_callable(undo_action)
    self.do_action = do_action
    self.undo_action = undo_action

class Action_History:
  """
  TODO(mikemeko)
  """
  def __init__(self):
    self._undo_stack = []
    self._redo_stack = []
  def record_action(self, action):
    """
    TODO(mikemeko)
    """
    assert isinstance(action, Action), 'action must be an Action'
    self._undo_stack.append(action)
    self._redo_stack = []
  def undo(self):
    """
    TODO(mikemeko)
    """
    if self._undo_stack:
      last_action = self._undo_stack.pop()
      last_action.undo_action()
      self._redo_stack.append(last_action)
  def redo(self):
    """
    TODO(mikemeko)
    """
    if self._redo_stack:
      next_action = self._redo_stack.pop()
      next_action.do_action()
      self._undo_stack.append(next_action)
  def clear(self):
    """
    TODO(mikemeko)
    """
    self._undo_stack = []
    self._redo_stack = []
