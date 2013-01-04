"""
Utilities for testing.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from poly import Polynomial
from poly import R_Polynomial

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
  assert isinstance(poly_1, Polynomial)
  assert isinstance(poly_2, Polynomial)
  assert poly_1.variables() == poly_2.variables()
  for var in poly_1.variables():
    assert_r_polys_equal(poly_1.coeff(var), poly_2.coeff(var))
