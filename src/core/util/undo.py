"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Mihchael Mekonnen)'

class Action:
  """
  TODO(mikemeko)
  """
  @property
  def do_action(self):
    """
    TODO(mikemeko)
    """
    raise Exception('subclasses should implement this')
  def undo_action(self):
    """
    TODO(mikemeko)
    """
    raise Exception('subclasses should implement this')

class Action_History:
  """
  TODO(mikemeko)
  """
  def __init__(self):
    self._undo_stack = []
    self._redo_stack = []
  def take_action(self, action):
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
