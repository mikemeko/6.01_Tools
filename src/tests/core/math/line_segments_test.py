"""
Unittests for line_segments.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.math.line_segments import intersect
from unittest import main
from unittest import TestCase

class Line_Segment_Intersect_Test(TestCase):
  """
  Tests for core/math/line_segments.
  """
  def _assert_intersect(self, segment1, segment2):
    assert intersect(segment1, segment2)
    assert intersect(segment2, segment1)
  def _assert_dont_intersect(self, segment1, segment2):
    assert not intersect(segment1, segment2)
    assert not intersect(segment2, segment1)
  def test_intersect(self):
    self._assert_intersect(((0, 0), (2, 2)), ((0, 2), (2, 0)))
    self._assert_intersect(((0, 0), (0, 2)), ((0, 2), (2, 2)))
    self._assert_intersect(((0, 0), (0, 2)), ((0, 2), (0, 4)))
    self._assert_intersect(((0, 0), (2, 2)), ((2, 2), (4, 0)))
    self._assert_intersect(((0, 0), (4, 0)), ((2, 0), (6, 0)))
    self._assert_intersect(((0, 0), (6, 0)), ((2, 0), (4, 0)))
    self._assert_intersect(((0, 0), (0, 6)), ((0, 2), (0, 4)))
    self._assert_intersect(((0, 0), (6, 6)), ((2, 2), (4, 4)))
    self._assert_intersect(((0, 0), (4, 4)), ((2, 2), (6, 6)))
    self._assert_intersect(((0, 0), (4, 4)), ((2, 2), (4, 0)))
    self._assert_dont_intersect(((0, 0), (0, 2)), ((3, 0), (4, 0)))
    self._assert_dont_intersect(((0, 0), (0, 2)), ((0, 3), (0, 4)))
    self._assert_dont_intersect(((0, 0), (2, 2)), ((1, 0), (3, 2)))
    self._assert_dont_intersect(((0, 0), (2, 2)), ((5, 2), (4, 6)))
    self._assert_dont_intersect(((8, 29), (11, 29)), ((12, 29), (14, 29)))

if __name__ == '__main__':
  main()
