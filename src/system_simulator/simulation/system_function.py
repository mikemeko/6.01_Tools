"""
Representation for a system function.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from numpy import roots
from poly import R_Ratio

class System_Function:
  """
  Representation for a system function.
  """
  def __init__(self, ratio):
    """
    |ratio|: an R_Ratio equivalent to the transfer function (Y/X) of a system.
    """
    assert isinstance(ratio, R_Ratio)
    self.ratio = ratio
    # store lists of the coefficients of the numerator and denominator
    # polynomials in R
    self.numerator_coeffs = list(ratio.numerator.coeffs)
    self.denominator_coeffs = list(ratio.denominator.coeffs)
    self._pad_coeffs()
  def _pad_coeffs(self):
    """
    Pad the numerator and denominator coeffs with 0s so that poles and zeros
        are computed correctly.
    """
    ln = len(self.numerator_coeffs)
    dn = len(self.denominator_coeffs)
    diff = abs(ln - dn)
    if ln < dn:
      self.numerator_coeffs += [0] * diff
    elif dn < ln:
      self.denominator_coeffs += [0] * diff
  def poles(self):
    """
    Returns the poles of this system (may include hidden poles).
    """
    return list(roots(self.denominator_coeffs))
  def zeros(self):
    """
    Returns the zeros of this system (may include hidden zeros).
    """
    return list(roots(self.numerator_coeffs))
  def __str__(self):
    return str(self.ratio)
