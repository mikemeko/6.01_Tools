"""
Unittests for gui/util.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from gui.constants import BOARD_GRID_SEPARATION
from gui.util import dist
from gui.util import point_inside_bbox
from gui.util import point_inside_circle
from gui.util import snap
from math import sqrt
from unittest import main
from unittest import TestCase

class Util_Test(TestCase):
  """
  Tests for gui/util.
  """
  def test_point_inside_bbox(self):
    bbox = (0, 0, 10, 10)
    assert point_inside_bbox((0, 0), bbox)
    assert point_inside_bbox((5, 5), bbox)
    assert point_inside_bbox((10, 10), bbox)
    assert not point_inside_bbox((-1, -1), bbox)
    assert not point_inside_bbox((11, 11), bbox)
  def test_dist(self):
    self.assertEquals(1, dist((0, 0), (1, 0)))
    self.assertEquals(sqrt(2), dist((0, 0), (1, 1)))
  def test_point_inside_circle(self):
    assert point_inside_circle((0, 0), (0, 0, 1))
    assert point_inside_circle((0, 1), (0, 0, 1))
    assert not point_inside_circle((1, 1), (0, 0, 1))
  def test_snap(self):
    self.assertEquals(0, snap(BOARD_GRID_SEPARATION / 4))
    self.assertEquals(BOARD_GRID_SEPARATION, snap(3 * BOARD_GRID_SEPARATION /
        4))

if __name__ == '__main__':
  main()
