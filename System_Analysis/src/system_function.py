"""
Representation for a system function.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from numpy import roots
from poly import R_Polynomial

class System_Function:
  """
  Representation for a system function.
  """
  def __init__(self, numerator, denominator):
    assert isinstance(numerator, R_Polynomial), 'numerator must be a poly'
    assert isinstance(denominator, R_Polynomial), 'denominator must be a poly'
    self.numerator = numerator
    self.denominator = denominator
    self._pad_coeffs()
  def _pad_coeffs(self):
    """
    Pad the numerator and denominator with 0s so that poles and zeros are
    computed correctly.
    """
    diff = abs(self.numerator.degree - self.denominator.degree)
    if self.numerator.degree < self.denominator.degree:
      self.numerator.coeffs = self.numerator.coeffs + [0] * diff
    elif self.numerator.degree > self.denominator.degree:
      self.denominator.coeffs = self.denominator.coeffs + [0] * diff
  def poles(self):
    """
    Returns the poles of this system (may include hidden poles).
    """
    return set(roots(self.denominator.coeffs))
  def zeros(self):
    """
    Returns the zeros of this system (may include hidden zeros).
    """
    return set(roots(self.numerator.coeffs))
  def __str__(self):
    return '(%s)/(%s)' % (str(self.numerator), str(self.denominator))
