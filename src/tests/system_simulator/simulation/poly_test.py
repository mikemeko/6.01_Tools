"""
Unittests for poly.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from system_simulator.simulation.poly import Polynomial
from system_simulator.simulation.poly import R_Polynomial
from system_simulator.simulation.poly import R_Ratio
from unittest import main
from unittest import TestCase
from util import assert_polys_equal
from util import assert_r_polys_equal
from util import assert_r_ratios_equal

class R_Polynomial_Test(TestCase):
  """
  Tests for R_Polynomial.
  """
  def setUp(self):
    self.r_poly_1 = R_Polynomial([1,0,2])
    self.r_poly_2 = R_Polynomial([2,1])
  def test_preconditions(self):
    self.assertRaises(Exception, R_Polynomial, '')
    self.assertRaises(Exception, R_Polynomial, [])
    self.assertRaises(Exception, R_Polynomial, [''])
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
  def test_is_zero(self):
    assert not self.r_poly_1.is_zero()
    assert R_Polynomial([0]).is_zero()
  def test_add(self):
    assert_r_polys_equal(self.r_poly_1 + self.r_poly_2, R_Polynomial([3,1,2]))
  def test_sub(self):
    assert_r_polys_equal(self.r_poly_1 - self.r_poly_2,
        R_Polynomial([-1,-1,2]))
  def test_mul(self):
    assert_r_polys_equal(self.r_poly_1 * self.r_poly_2,
        R_Polynomial([2, 1, 4, 2]))
  def test_str(self):
    self.assertEquals('0', str(R_Polynomial.zero()))
    self.assertEquals('1', str(R_Polynomial.one()))
    self.assertEquals('22', str(R_Polynomial([22])))
    self.assertEquals('22R', str(R_Polynomial([0, 22])))
    self.assertEquals('22 + 22R', str(R_Polynomial([22, 22])))
    self.assertEquals('22 + 22R + R^2', str(R_Polynomial([22, 22, 1])))
    self.assertEquals('22R^2', str(R_Polynomial([0, 0, 22])))

class R_Ratio_Test(TestCase):
  """
  Tests for R_Ratio.
  """
  def setUp(self):
    self.ratio_1 = R_Ratio(R_Polynomial.one(), R_Polynomial([1, 0, 1]))
    self.ratio_2 = R_Ratio(R_Polynomial([0, 1]), R_Polynomial([2, 1]))
  def test_preconditions(self):
    self.assertRaises(Exception, R_Ratio, 'numerator')
    self.assertRaises(Exception, R_Ratio, R_Polynomial.one(), 'denominator')
    self.assertRaises(Exception, R_Ratio, R_Polynomial.one(),
        R_Polynomial.zero())
  def test_scalar_mult(self):
    assert_r_ratios_equal(self.ratio_1.scalar_mult(22),
        R_Ratio(R_Polynomial([22]), R_Polynomial([1, 0, 1])))
  def test_shift(self):
    assert_r_ratios_equal(self.ratio_1.shift(),
        R_Ratio(R_Polynomial([0,1]), R_Polynomial([1, 0, 1])))
  def test_add(self):
    assert_r_ratios_equal(self.ratio_1 + self.ratio_2,
        R_Ratio(R_Polynomial([2,2,0,1]), R_Polynomial([2,1,2,1])))
  def test_sub(self):
    assert_r_ratios_equal(self.ratio_1 - self.ratio_2,
        R_Ratio(R_Polynomial([2,0,0,-1]), R_Polynomial([2,1,2,1])))
  def test_mul(self):
    assert_r_ratios_equal(self.ratio_1 * self.ratio_2,
        R_Ratio(R_Polynomial([0,1]), R_Polynomial([2,1,2,1])))
  def test_div(self):
    assert_r_ratios_equal(self.ratio_1 / self.ratio_2,
        R_Ratio(R_Polynomial([2,1]), R_Polynomial([0,1,0,1])))

class Polynomial_Test(TestCase):
  """
  Tests for Polynomial.
  """
  def setUp(self):
    self.poly_1 = Polynomial({'A': R_Ratio(R_Polynomial.one(),
        R_Polynomial([0,1])), 'B': R_Ratio(R_Polynomial([1,1]))})
    self.poly_2 = Polynomial({'A': R_Ratio(R_Polynomial([0,1])),
        'C': R_Ratio(R_Polynomial.one())})
  def test_variables(self):
    self.assertEquals(set(['A', 'B']), set(self.poly_1.variables()))
  def test_has_variable(self):
    assert self.poly_1.has_variable('A')
    assert not self.poly_1.has_variable('C')
  def test_coeff(self):
    assert_r_ratios_equal(self.poly_1.coeff('A'), R_Ratio(R_Polynomial.one(),
        R_Polynomial([0,1])))
    assert_r_ratios_equal(self.poly_1.coeff('C'), R_Ratio.zero())
  def test_substitute(self):
    assert_polys_equal(self.poly_1.substitute('A', Polynomial({'C':
        R_Ratio(R_Polynomial([0, 1]))})), Polynomial({'C': R_Ratio(
        R_Polynomial([0,1]), R_Polynomial([0,1])), 'B': R_Ratio(
        R_Polynomial([1,1]))}))
  def test_add(self):
    assert_polys_equal(self.poly_1 + self.poly_2, Polynomial({'A': R_Ratio(
        R_Polynomial([1,0,1]), R_Polynomial([0,1])), 'B': R_Ratio(
        R_Polynomial([1,1])), 'C': R_Ratio(R_Polynomial.one())}))

if __name__ == '__main__':
  main()
