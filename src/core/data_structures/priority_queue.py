"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from heapq import heappop
from heapq import heappush

class Priority_Queue:
  """
  TODO(mikemeko)
  """
  def __init__(self):
    self.data = []
  def push(self, item, cost):
    """
    TODO(mikemeko)
    """
    heappush(self.data, (cost, item))
  def pop(self):
    """
    TODO(mikemeko)
    """
    cost, item = heappop(self.data)
    return item
  def __bool__(self):
    return bool(self.data)
  def __len__(self):
    return len(self.data)
  def __str__(self):
    return str(self.data)
