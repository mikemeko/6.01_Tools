"""
TODO(mikemeko)
Don't forget to mention 6.01 notes.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.data_structures.priority_queue import Priority_Queue

class Search_Node:
  """
  TODO(mikemeko)
  """
  def __init__(self, state, parent=None, cost=0):
    """
    TODO(mikemeko)
    """
    self.state = state
    self.parent = parent
    self.cost = cost
  @property
  def get_children(self):
    """
    TODO(mikemeko)
    """
    raise NotImplementedError('subclasses should implement this')

def a_star(start_node, goal_test, heuristic=lambda state: 0):
  """
  TODO(mikemeko)
  """
  if goal_test(start_node.state):
    return start_node.state
  agenda = Priority_Queue()
  agenda.push(start_node, start_node.cost + heuristic(start_node.state))
  expanded = set()
  while agenda:
    parent = agenda.pop()
    if parent.state not in expanded:
      expanded.add(parent.state)
      if goal_test(parent.state):
        return parent.state
      for child in parent.get_children():
        if child.state not in expanded:
          agenda.push(child, child.cost + heuristic(child.state))
  return None
