"""
Miscellaneous utility methods.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

def is_callable(obj):
  """
  Returns True if |obj| is callable, False otherwise.
  """
  return hasattr(obj, '__call__')
