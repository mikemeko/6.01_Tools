"""
Unittests for system.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from system_simulator.simulation.constants import X
from system_simulator.simulation.constants import Y
from system_simulator.simulation.poly import R_Polynomial
from system_simulator.simulation.poly import R_Ratio
from system_simulator.simulation.system import Adder
from system_simulator.simulation.system import Delay
from system_simulator.simulation.system import Gain
from system_simulator.simulation.system import System
from system_simulator.simulation.system import System_Function
from unittest import main
from unittest import TestCase
from util import assert_system_functions_equal

class System_Test(TestCase):
  """
  Tests for System.
  """
  def test_gain(self):
    sys = System([Gain(X, Y, 10)])
    assert_system_functions_equal(sys.sf, System_Function(R_Ratio(
        R_Polynomial([10]), R_Polynomial([1]))))
  def test_delay(self):
    sys = System([Delay(X,Y)])
    assert_system_functions_equal(sys.sf, System_Function(R_Ratio(
        R_Polynomial([0,1]), R_Polynomial([1]))))
  def test_adder(self):
    sys = System([Delay('A',Y), Adder([X,Y], 'A')])
    assert_system_functions_equal(sys.sf, System_Function(R_Ratio(
        R_Polynomial([0,1]), R_Polynomial([1, -1]))))
  def test_big_system(self):
    sys = System([Adder([X, 'D'], 'A'), Gain('A', 'B', 10),
        Adder(['B', Y], 'C'), Delay('C', Y), Delay(Y, 'D')])
    assert_system_functions_equal(sys.sf, System_Function(R_Ratio(
        R_Polynomial([0,10]), R_Polynomial([1,-1,-10]))))

if __name__ == '__main__':
  main()
