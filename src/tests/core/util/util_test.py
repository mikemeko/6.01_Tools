"""
Unittests for util.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonne)'

from core.util.util import clip
from core.util.util import empty
from core.util.util import in_bounds
from core.util.util import is_number
from core.util.util import overlap
from core.util.util import rects_overlap
from unittest import main
from unittest import TestCase

class Util_Test(TestCase):
  """
  Tests for util.py.
  """
  def test_clip(self):
    assert clip(-1, 0, 2) == 0
    assert clip(0, 0, 2) == 0
    assert clip(1, 0, 2) == 1
    assert clip(2, 0, 2) == 2
    assert clip(3, 0, 2) == 2
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
  def test_overlap(self):
    assert not overlap((1, 2), (3, 4))
    assert not overlap((3, 4), (1, 2))
    assert overlap((1, 2), (2, 3))
    assert overlap((2, 3), (1, 2))
    assert overlap((1, 3), (2, 4))
    assert overlap((2, 4), (1, 3))
    assert overlap((1, 4), (2, 3))
    assert overlap((2, 3), (1, 4))
  def test_rects_overlap(self):
    assert not rects_overlap((0, 0, 1, 1), (2, 2, 3, 3))
    assert rects_overlap((0, 0, 1, 1), (1, 1, 2, 2))
    assert rects_overlap((0, 0, 2, 2), (1, 1, 3, 3))

if __name__ == '__main__':
  main()
