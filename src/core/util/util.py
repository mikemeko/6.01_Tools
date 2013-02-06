"""
Miscellaneous utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

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

def is_callable(obj):
  """
  Returns True if |obj| is callable, False otherwise.
  """
  return hasattr(obj, '__call__')

def is_number(val):
  """
  Returns True if |val| is a number, False otherwise.
  """
  return isinstance(val, (complex, float, int, long))
