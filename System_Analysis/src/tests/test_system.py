"""
Unittests for system.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.constants import X
from core.constants import Y
from core.poly import R_Polynomial
from core.system import Adder
from core.system import Delay
from core.system import Gain
from core.system import System
from core.system import System_Function
from test_util import assert_system_functions_equal
from unittest import main
from unittest import TestCase

class Test_System(TestCase):
  """
  Tests for System.
  """
  def test_gain(self):
    sys = System([Gain(X, Y, 10)])
    assert_system_functions_equal(sys.sf, System_Function(R_Polynomial([10]),
        R_Polynomial([1])))
  def test_delay(self):
    sys = System([Delay(X,Y)])
    assert_system_functions_equal(sys.sf, System_Function(R_Polynomial([0,1]),
        R_Polynomial([1])))
  def test_adder(self):
    sys = System([Delay('A',Y), Adder([X,Y], 'A')])
    assert_system_functions_equal(sys.sf, System_Function(R_Polynomial([0,1]),
        R_Polynomial([1, -1])))
  def test_big_system(self):
    sys = System([Adder([X, 'D'], 'A'), Gain('A', 'B', 10),
        Adder(['B', Y], 'C'), Delay('C', Y), Delay(Y, 'D')])
    assert_system_functions_equal(sys.sf, System_Function(R_Polynomial([0,10]),
        R_Polynomial([1,-1,-10])))

if __name__ == '__main__':
  main()
