"""
Unittests for system.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from poly import R_Polynomial
from system import Adder
from system import Delay
from system import Gain
from system import System
from system import System_Function
from test_util import assert_system_functions_equal
from unittest import main
from unittest import TestCase

class Test_System_Function(TestCase):
  """
  Tests for System_Function.
  """
  def setUp(self):
    self.sf1 = System_Function(R_Polynomial([1]), R_Polynomial([1]))
    self.sf2 = System_Function(R_Polynomial([0,0,1]), R_Polynomial([1]))
    self.sf3 = System_Function(R_Polynomial([1]), R_Polynomial([1, -0.5]))
    self.sf4 = System_Function(R_Polynomial([1,1]), R_Polynomial([1,-3,2]))
  def test_poles(self):
    assert self.sf1.poles() == set([])
    assert self.sf2.poles() == set([0])
    assert self.sf3.poles() == set([0.5])
    assert self.sf4.poles() == set([1,2])
  def test_zeros(self):
    assert self.sf1.zeros() == set([])
    assert self.sf2.zeros() == set([])
    assert self.sf3.zeros() == set([0])
    assert self.sf4.zeros() == set([-1,0])

class Test_System(TestCase):
  """
  Tests for System.
  """
  def test_gain(self):
    sys = System([Gain('X', 'Y', 10)])
    assert_system_functions_equal(sys.sf, System_Function(R_Polynomial([10]),
        R_Polynomial([1])))
  def test_delay(self):
    sys = System([Delay('X','Y')])
    assert_system_functions_equal(sys.sf, System_Function(R_Polynomial([0,1]),
        R_Polynomial([1])))
  def test_adder(self):
    sys = System([Delay('A','Y'), Adder(['X','Y'], 'A')])
    assert_system_functions_equal(sys.sf, System_Function(R_Polynomial([0,1]),
        R_Polynomial([1, -1])))
  def test_big_system(self):
    sys = System([Adder(['X', 'D'], 'A'), Gain('A', 'B', 10),
        Adder(['B', 'Y'], 'C'), Delay('C', 'Y'), Delay('Y', 'D')])
    assert_system_functions_equal(sys.sf, System_Function(R_Polynomial([0,10]),
        R_Polynomial([1,-1,-10])))

if __name__ == '__main__':
  main()
