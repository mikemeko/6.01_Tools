"""
Unittests for poly.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from poly import Polynomial
from poly import R_Polynomial
from unittest import main
from unittest import TestCase

def assert_r_polys_equal(r_poly_1, r_poly_2):
  """
  Checks that two R_Polynomials are equal.
  """
  assert isinstance(r_poly_1, R_Polynomial)
  assert isinstance(r_poly_2, R_Polynomial)
  assert r_poly_1.degree == r_poly_2.degree
  for exp in xrange(r_poly_1.degree + 1):
    assert r_poly_1.coeff(exp) == r_poly_2.coeff(exp)

def assert_polys_equal(poly_1, poly_2):
  """
  Checks that two Polynomials are equal.
  """
  assert poly_1.variables() == poly_2.variables()
  for var in poly_1.variables():
    assert_r_polys_equal(poly_1.coeff(var), poly_2.coeff(var))

class Test_R_Polynomial(TestCase):
  """
  Tests for R_Polynomial.
  """
  def setUp(self):
    self.r_poly_1 = R_Polynomial([1,0,2])
    self.r_poly_2 = R_Polynomial([2,1])
  def test_degree(self):
    assert self.r_poly_1.degree == 2
    assert self.r_poly_2.degree == 1
  def test_coeff(self):
    assert self.r_poly_1.coeff(0) == 1
    assert self.r_poly_1.coeff(1) == 0
    assert self.r_poly_1.coeff(2) == 2
    assert self.r_poly_1.coeff(3) == 0
  def test_scalar_mult(self):
    assert_r_polys_equal(self.r_poly_1.scalar_mult(2), R_Polynomial([2,0,4]))
  def test_shift(self):
    assert_r_polys_equal(self.r_poly_1.shift(), R_Polynomial([0,1,0,2]))
  def test_add(self):
    assert_r_polys_equal(self.r_poly_1 + self.r_poly_2, R_Polynomial([3,1,2]))

class Test_Polynomial(TestCase):
  """
  Tests for Polynomial.
  """
  def setUp(self):
    self.poly_1 = Polynomial({'X':R_Polynomial([0,1]), 'Y':R_Polynomial([2])})
    self.poly_2 = Polynomial({'X':R_Polynomial([1]), 'A':R_Polynomial([1])})
  def test_variables(self):
    assert self.poly_1.variables() == set(['X','Y'])
  def test_coeff(self):
    assert_r_polys_equal(self.poly_1.coeff('X'), R_Polynomial([0,1]))
    assert_r_polys_equal(self.poly_1.coeff('Y'), R_Polynomial([2]))
  def test_scalar_mult(self):
    assert_polys_equal(self.poly_1.scalar_mult(2), Polynomial(
        {'X':R_Polynomial([0,2]), 'Y':R_Polynomial([4])}))
  def test_shift(self):
    assert_polys_equal(self.poly_1.shift(), Polynomial(
        {'X':R_Polynomial([0,0,1]), 'Y':R_Polynomial([0,2])}))
  def test_add(self):
    assert_polys_equal(self.poly_1 + self.poly_2, Polynomial(
        {'X':R_Polynomial([1,1]), 'Y':R_Polynomial([2]),
        'A':R_Polynomial([1])}))

if __name__ == '__main__':
  main()