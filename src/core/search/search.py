"""
Search infrastructure.
Credit to Chapter 7 of MIT 6.01 notes
    (http://mit.edu/6.01/www/handouts/readings.pdf).
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.data_structures.priority_queue import Priority_Queue

class Search_Node:
  """
  Representation for a node in the search graph. Clients of the search
      infrastructure should use subclasses of Search_Node implementing the
      get_children method.
  """
  def __init__(self, state, parent=None, cost=0):
    """
    |state|: state of the search node, dependent on the application.
    |parent|: parent node to this node, None if this node is the root.
    |cost|: cost to reach from the root node to this node.
    """
    self.state = state
    self.parent = parent
    self.cost = cost
  @property
  def get_children(self):
    """
    Should return a list of the Search_Nodes that are reachable from this node.
    """
    raise NotImplementedError('subclasses should implement this')

def a_star(start_node, goal_test, heuristic=lambda state: 0,
    progress=lambda state, cost: None):
  """
  Runs an A* search starting at |start_node| until a node that satisfies the
      |goal_test| is found. |goal_test| should be a function that takes in a
      state of a node and returns True if the desired goal has been satisfied.
      |heuristic| is a map from node states to estimates of distance to the
      goal, should be admissible to produce optimal value, and can result in
      considerable speed-up! (See Chapter 7 of MIT 6.01 course notes for more.)
  Returns the state found that satisfies the |goal_test|, or None if no such
      state is found.
  TODO(mikemeko): update
  """
  if goal_test(start_node.state):
    return start_node.state
  agenda = Priority_Queue()
  agenda.push(start_node, start_node.cost + heuristic(start_node.state))
  expanded = set()
  while agenda:
    parent, cost = agenda.pop()
    progress(parent.state, cost)
    if parent.state not in expanded:
      expanded.add(parent.state)
      if goal_test(parent.state):
        return parent.state
      for child in parent.get_children():
        if child.state not in expanded:
          agenda.push(child, child.cost + heuristic(child.state))
  return None
