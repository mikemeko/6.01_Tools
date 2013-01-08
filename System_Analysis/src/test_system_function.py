# -*- coding: utf-8 -*-
"""
Unittests for system_function.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from poly import R_Polynomial
from system_function import System_Function
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
    assert self.sf1.poles() == []
    assert self.sf2.poles() == [0, 0]
    assert self.sf3.poles() == [0.5]
    assert sorted(self.sf4.poles()) == [1,2]
  def test_zeros(self):
    assert self.sf1.zeros() == []
    assert self.sf2.zeros() == []
    assert self.sf3.zeros() == [0]
    assert sorted(self.sf4.zeros()) == [-1,0]

if __name__ == '__main__':
  main()
