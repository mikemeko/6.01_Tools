"""
Support for undo/redo.
"""

__author__ = 'mikemeko@mit.edu (Mihchael Mekonnen)'

from constants import DEBUG_UNDO
from core.util.util import is_callable

class Action:
  """
  Representation for an action that can be done or undone.
  """
  def __init__(self, do_action, undo_action, description='Action'):
    """
    |do_action|: method to call to do the action.
    |undo_action|: method to call to undo the action.
    |description|: a description of this action (for debugging).
    """
    assert is_callable(do_action), 'do_action must be callable'
    assert is_callable(undo_action), 'undo_action must be callable'
    self.do_action = do_action
    self.undo_action = undo_action
    self.description = description
  def __str__(self):
    return self.description

class Multi_Action(Action):
  """
  Representation for an action composed of multiple small actions.
  """
  def __init__(self, actions, description='Multi_Action'):
    """
    |actions|: a list containing the small Actions of which this Multi_Action
        is composed.
    """
    assert isinstance(actions, list), 'actions must be a list'
    assert all(isinstance(item, Action) for item in actions), (
        'all sub-actions must be Actions')
    self.actions = actions
    def do_actions():
      """
      Does the actions in the given order.
      """
      for action in actions:
        action.do_action()
    def undo_actions():
      """
      Undoes the actions in the reverse order.
      """
      for action in reversed(actions):
        action.undo_action()
    Action.__init__(self, do_actions, undo_actions, description)
  def __str__(self):
    return '%s[%s]' % (self.description, ', '.join(map(str, self.actions)))

class Action_History:
  """
  Data structure to record a history of actions.
  """
  def __init__(self):
    self._undo_stack = []
    self._redo_stack = []
    if DEBUG_UNDO:
      print 'empty Action_History created'
  def record_action(self, action):
    """
    Records the given |action| as the latest action done.
    """
    assert isinstance(action, Action), 'action must be an Action'
    self._undo_stack.append(action)
    # clear redo stack since a new action has been performed
    self._redo_stack = []
    if DEBUG_UNDO:
      print self
  def undo(self):
    """
    If an action has been done since creation or last clear, undoes the latest
        action and returns True. Otherwise returns False.
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
    If an action has been undone since creation or last clear, does the latest
        such action and returns True. Otherwise returns False.
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
    Clears the history recorded so far.
    """
    self._undo_stack = []
    self._redo_stack = []
    if DEBUG_UNDO:
      print 'Action_History cleared'
  def combine_last_n(self, n):
    """
    Combines the last |n| actions into one action. |n| must be an integer
        greater than 1. This is kind of hacky, but useful :P
    """
    assert isinstance(n, int) and n > 1
    assert len(self._undo_stack) >= n
    self._undo_stack = self._undo_stack[:-n] + [Multi_Action(
        self._undo_stack[-n:])]
  def __str__(self):
    return '%s <|> %s' % (', '.join(map(str, self._undo_stack)),
        ', '.join(map(str, reversed(self._redo_stack))))
