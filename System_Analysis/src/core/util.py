"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Mike Mekonnen)'

def empty(items):
  """
  Returns True if |items| is empty, False otherwise.
  """
  return len(items) == 0

def in_bounds(val, min_val, max_val):
  """
  Returns True if min_val <= val <= max_val, False otherwise.
  """
  return min_val <= val <= max_val
