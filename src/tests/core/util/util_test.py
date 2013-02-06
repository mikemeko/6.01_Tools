"""
Unittests for util.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonne)'

from core.util.util import empty
from core.util.util import in_bounds
from core.util.util import is_number
from unittest import main
from unittest import TestCase

class Util_Test(TestCase):
  """
  Tests for util.py.
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
  def test_is_number(self):
    assert is_number(22)
    assert is_number(22.0)
    assert is_number(2222222222222222222222222222222222222l)
    assert not is_number('22')
    assert not is_number('mikemeko')

if __name__ == '__main__':
  main()
