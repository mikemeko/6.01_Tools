"""
Unittests for search.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.search.search import a_star
from core.search.search import Search_Node
from unittest import main
from unittest import TestCase

class Test_Search_Node(Search_Node):
  """
     S
    / \
   /   \
  A     B
  |    / \
  |   /   \
  C  D     E
  """
  def __init__(self, state='S', parent=None, cost=0):
    Search_Node.__init__(self, state, parent, cost)
  def get_children(self):
    return [Test_Search_Node(new_state, self, self.cost + 1) for new_state in
        {'S': ['A', 'B'], 'A': ['C'], 'B': ['D', 'E']}.get(self.state, [])]

class Search_Test(TestCase):
  """
  Tests for core/search/search.
  """
  def test_search(self):
    assert a_star(Test_Search_Node(), lambda state: state == 'S') == 'S'
    assert a_star(Test_Search_Node(), lambda state: state == 'E') == 'E'
    assert a_star(Test_Search_Node(), lambda state: state == 'F') is None
    assert a_star(Test_Search_Node(), lambda state: state in ['A', 'D']) == 'A'

if __name__ == '__main__':
  main()
