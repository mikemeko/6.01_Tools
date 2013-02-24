"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Mihchael Mekonnen)'

from core.util.util import is_callable

class Action:
  """
  TODO(mikemeko)
  """
  def __init__(self, do_action, undo_action, description='Action'):
    """
    TODO(mikemeko)
    """
    assert is_callable(do_action)
    assert is_callable(undo_action)
    self.do_action = do_action
    self.undo_action = undo_action
    self.description = description
  def __str__(self):
    return self.description

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
    print self
  def undo(self):
    """
    TODO(mikemeko)
    """
    if self._undo_stack:
      last_action = self._undo_stack.pop()
      last_action.undo_action()
      self._redo_stack.append(last_action)
    print self
  def redo(self):
    """
    TODO(mikemeko)
    """
    if self._redo_stack:
      next_action = self._redo_stack.pop()
      next_action.do_action()
      self._undo_stack.append(next_action)
    print self
  def clear(self):
    """
    TODO(mikemeko)
    """
    self._undo_stack = []
    self._redo_stack = []
    print self
  def __str__(self):
    return '%s <|> %s' % (str(map(str, self._undo_stack)),
        str(map(str, reversed(self._redo_stack))))
