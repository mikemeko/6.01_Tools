"""
Unittests for undo.py.
TODO(mikemeko): better test for Multi_Action.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonne)'

from core.undo.undo import Action
from core.undo.undo import Action_History
from core.undo.undo import Multi_Action
from unittest import main
from unittest import TestCase

class Undo_Test(TestCase):
  """
  Tests for core/undo/undo.py.
  """
  def setUp(self):
    self._action_history = Action_History()
    self._A = self._create_action('A')
    self._B = self._create_action('B')
    self._actions = []
  def _create_action(self, val):
    def do_action():
      self._actions.append(val)
    def undo_action():
      self._actions.pop()
    return Action(do_action, undo_action)
  def _last_action(self):
    return self._actions[-1]
  def _do(self, action):
    action.do_action()
    self._action_history.record_action(action)
  def _undo(self):
    return self._action_history.undo()
  def _redo(self):
    return self._action_history.redo()
  def _clear(self):
    self._action_history.clear()
  def test_history_init(self):
    self.assertFalse(self._undo())
    self.assertFalse(self._redo())
  def test_undo_redo(self):
    self._do(self._A)
    self.assertEqual('A', self._last_action())
    self._do(self._B)
    self.assertEqual('B', self._last_action())
    self.assertTrue(self._undo())
    self.assertEqual('A', self._last_action())
    self.assertTrue(self._undo())
    self.assertFalse(self._actions)
    self.assertFalse(self._undo())
    self.assertTrue(self._redo())
    self.assertEqual('A', self._last_action())
    self.assertTrue(self._redo())
    self.assertEqual('B', self._last_action())
    self.assertFalse(self._redo())
  def test_clear(self):
    self._do(self._A)
    self._do(self._B)
    self._clear()
    self.assertFalse(self._undo())
    self.assertFalse(self._redo())
  def test_multi_action(self):
    multi_action = Multi_Action([self._A, self._B])
    self._do(multi_action)
    self.assertEqual('B', self._last_action())
    self.assertTrue(self._undo())
    self.assertFalse(self._actions)
    self.assertTrue(self._redo())
    self.assertEqual('B', self._last_action())
    self.assertFalse(self._redo())

if __name__ == '__main__':
  main()
