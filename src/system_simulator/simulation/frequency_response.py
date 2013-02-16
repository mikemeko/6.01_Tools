"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from cmath import phase
from math import e
from math import pi
from numpy import arange
from poly import R_Polynomial
from poly import R_Ratio
from pylab import plot
from pylab import show
from pylab import subplot
from system_function import System_Function

def eval_poly(coeffs, z):
  """
  TODO(mikemeko)
  """
  return sum(coeffs[i] * z ** i for i in xrange(len(coeffs)))

def plot_frequency_response(sf, num_samples=100):
  """
  TODO(mikemeko)
  """
  assert isinstance(sf, System_Function), 'sf must be a System_Function'
  numerator_z_coeffs = list(reversed(sf.numerator_coeffs))
  denominator_z_coeffs = list(reversed(sf.denominator_coeffs))
  def H(w):
    """
    TODO(mikemeko)
    """
    z = e ** complex(0, w)
    denominator = eval_poly(denominator_z_coeffs, z)
    if not denominator:
      # TODO(mikemeko)
      return 0
    numerator = eval_poly(numerator_z_coeffs, z)
    return numerator / denominator
  W = list(arange(-pi, pi, 2 * pi / num_samples))
  H_w = map(H, W)
  H_w_magnitude = map(abs, H_w)
  H_w_phase = map(phase, H_w)
  subplot(211)
  plot(W, H_w_magnitude)
  subplot(212)
  plot(W, H_w_phase)
  show()

if __name__ == '__main__':
  a = 0.5
  r_numerator = R_Polynomial([-a, 1])
  r_denominator = R_Polynomial([1, -a])
  ratio = R_Ratio(r_numerator, r_denominator)
  sf = System_Function(ratio)
  plot_frequency_response(sf)
