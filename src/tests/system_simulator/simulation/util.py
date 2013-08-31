"""
Utilities for testing.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from system_simulator.simulation.poly import Polynomial
from system_simulator.simulation.poly import R_Polynomial
from system_simulator.simulation.poly import R_Ratio
from system_simulator.simulation.system import System_Function

def assert_r_polys_identical(r_poly_1, r_poly_2):
  """
  Checks that two R_Polynomials are identical.
  """
  assert isinstance(r_poly_1, R_Polynomial)
  assert isinstance(r_poly_2, R_Polynomial)
  assert r_poly_1.degree == r_poly_2.degree
  for exp in xrange(r_poly_1.degree + 1):
    assert r_poly_1.coeff(exp) == r_poly_2.coeff(exp)

def assert_r_ratios_identical(r_ratio_1, r_ratio_2):
  """
  Checks that two R_Ratios are identical.
  """
  assert isinstance(r_ratio_1, R_Ratio)
  assert isinstance(r_ratio_2, R_Ratio)
  assert_r_polys_identical(r_ratio_1.numerator, r_ratio_2.numerator)
  assert_r_polys_identical(r_ratio_1.denominator, r_ratio_2.denominator)

def assert_polys_identical(poly_1, poly_2):
  """
  Checks that two Polynomials are identical.
  """
  assert isinstance(poly_1, Polynomial)
  assert isinstance(poly_2, Polynomial)
  assert poly_1.variables() == poly_2.variables()
  for var in poly_1.variables():
    assert_r_ratios_identical(poly_1.coeff(var), poly_2.coeff(var))

def assert_system_functions_identical(sf_1, sf_2):
  """
  Checks that two system functions are identical.
  """
  assert isinstance(sf_1, System_Function)
  assert isinstance(sf_2, System_Function)
  assert_r_ratios_identical(sf_1.ratio, sf_2.ratio)
