"""
Unittests for priority_queue.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.data_structures.priority_queue import Priority_Queue
from unittest import main
from unittest import TestCase

class Priority_Queue_Test(TestCase):
  """
  Tests for core/data_structures/priority_queue.
  """
  def test_priority_queue(self):
    q = Priority_Queue()
    assert q.pop() is None
    q.push('2', 2)
    q.push('1', 1)
    assert q.pop() == '1'
    q.push('3', 3)
    assert q.pop() == '2'
    assert q.pop() == '3'
    assert q.pop() == None

if __name__ == '__main__':
  main()
