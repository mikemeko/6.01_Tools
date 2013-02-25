"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Mihchael Mekonnen)'

from constants import DEBUG_UNDO
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

class Multi_Action(Action):
  """
  TODO(mikemeko)
  """
  def __init__(self, actions, description='Multi_Action'):
    """
    TODO(mikemeko)
    """
    assert isinstance(actions, list)
    assert all(isinstance(item, Action) for item in actions)
    self.actions = actions
    def do_actions():
      """
      TODO(mikemeko)
      """
      for action in actions:
        action.do_action()
    def undo_actions():
      """
      TODO(mikemeko)
      """
      for action in reversed(actions):
        action.undo_action()
    Action.__init__(self, do_actions, undo_actions, description)
  def __str__(self):
    return '%s[%s]' % (self.description, ', '.join(map(str, self.actions)))

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
    if DEBUG_UNDO:
      print self
  def undo(self):
    """
    TODO(mikemeko)
    """
    if self._undo_stack:
      last_action = self._undo_stack.pop()
      last_action.undo_action()
      self._redo_stack.append(last_action)
      if DEBUG_UNDO:
        print self
      return True
    return False
  def redo(self):
    """
    TODO(mikemeko)
    """
    if self._redo_stack:
      next_action = self._redo_stack.pop()
      next_action.do_action()
      self._undo_stack.append(next_action)
      if DEBUG_UNDO:
        print self
      return True
    return False
  def clear(self):
    """
    TODO(mikemeko)
    """
    self._undo_stack = []
    self._redo_stack = []
    if DEBUG_UNDO:
      print self
  def __str__(self):
    return '%s <|> %s' % (', '.join(map(str, self._undo_stack)),
        ', '.join(map(str, reversed(self._redo_stack))))
