"""
Unittests for system.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from poly import R_Polynomial
from poly import Polynomial
from system import Adder
from system import Delay
from system import Gain
from system import System
from test_util import assert_polys_equal
from unittest import main
from unittest import TestCase

class Test_System(TestCase):
  """
  Tests for System.
  """
  def test_gain(self):
    sys = System([Gain('X', 'Y', 10)])
    assert_polys_equal(sys.solve(), Polynomial({'X':R_Polynomial([10])}))
  def test_delay(self):
    sys = System([Delay('X','Y')])
    assert_polys_equal(sys.solve(), Polynomial({'X':R_Polynomial([0,1])}))
  def test_adder(self):
    sys = System([Delay('A','Y'), Adder(['X','Y'], 'A')])
    assert_polys_equal(sys.solve(), Polynomial({'X':R_Polynomial([0,1]),
        'Y':R_Polynomial([0,1])}))
  def test_big_system(self):
    sys = System([Adder(['X', 'D'], 'A'), Gain('A', 'B', 10),
        Adder(['B', 'Y'], 'C'), Delay('C', 'Y'), Delay('Y', 'D')])
    assert_polys_equal(sys.solve(), Polynomial({'X':R_Polynomial([0,10]),
        'Y':R_Polynomial([0,1,10])}))

if __name__ == '__main__':
  main()
