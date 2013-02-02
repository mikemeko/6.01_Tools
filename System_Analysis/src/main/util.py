"""
Utility methods.
"""

__author__ = 'mikemeko@mit.edu (Mike Mekonnen)'

def is_callable(obj):
  """
  Returns True if |obj| is callable, False otherwise.
  """
  return hasattr(obj, '__call__')
