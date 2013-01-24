"""
Unittests for core/util.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonne)'

from core.util import empty
from core.util import in_bounds
from unittest import main
from unittest import TestCase

class Util_Test(TestCase):
  """
  Tests for core/util.
  """
  def test_empty(self):
    assert empty([])
    assert not empty([22])
  def test_in_bounds(self):
    assert not in_bounds(0, 1, 3)
    assert in_bounds(1, 1, 3)
    assert in_bounds(2, 1, 3)
    assert in_bounds(3, 1, 3)
    assert not in_bounds(4, 1, 3)

if __name__ == '__main__':
  main()
