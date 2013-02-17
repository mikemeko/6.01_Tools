"""
Frequency response.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from cmath import phase
from constants import FREQUENCY_RESPONSE_MAGNITUDE_LABEL
from constants import FREQUENCY_RESPONSE_PHASE_LABEL
from constants import FREQUENCY_RESPONSE_TITLE
from constants import FREQUENCY_RESPONSE_X_LABEL
from constants import NUM_FREQUENCY_RESPONSE_SAMPLES
from core.util.util import is_number
from math import e
from math import pi
from numpy import arange
from pylab import gcf
from pylab import plot
from pylab import show
from pylab import subplot
from pylab import xlabel
from pylab import ylabel
from system import System

def eval_poly(coeffs, z):
  """
  Given the represenation of a polynomial in the list |coeffs|, evaluates the
      polynomial at the given point |z|.
  Returns coeffs[0] + coeffs[1] * z + ... + coeffs[n-1] * z ** (n-1).
  """
  assert all(map(is_number, coeffs)), 'all coefficients must be numbers'
  assert is_number(z), 'z must be a number'
  return sum(coeffs[i] * z ** i for i in xrange(len(coeffs)))

def plot_frequency_response(sys, num_samples=NUM_FREQUENCY_RESPONSE_SAMPLES):
  """
  Plots the frequency response for the given |system|, assuming that its
      system function has been successfully computed. Uses |num_samples| points
      to approximate the frequency response.
  """
  assert isinstance(sys, System), 'sys must be a System'
  if sys.sf:
    # compute polynomials in z from polynomials in R by replacing R by 1/z
    numerator_z_coeffs = list(reversed(sys.sf.numerator_coeffs))
    denominator_z_coeffs = list(reversed(sys.sf.denominator_coeffs))
    def H(w):
      """
      Computes the frequency response at the given frequency |w|. Returns 0 if
          the frequency response explodes at |w|.
      """
      z = e ** complex(0, w)
      denominator = eval_poly(denominator_z_coeffs, z)
      if not denominator:
        # frequency response blows up
        return 0
      numerator = eval_poly(numerator_z_coeffs, z)
      return numerator / denominator
    W = list(arange(-pi, pi, 2 * pi / num_samples))
    H_w = map(H, W)
    H_w_magnitude = map(abs, H_w)
    H_w_phase = map(phase, H_w)
    gcf().canvas.set_window_title(FREQUENCY_RESPONSE_TITLE)
    subplot(211)
    plot(W, H_w_magnitude)
    ylabel(FREQUENCY_RESPONSE_MAGNITUDE_LABEL)
    subplot(212)
    plot(W, H_w_phase)
    xlabel(FREQUENCY_RESPONSE_X_LABEL)
    ylabel(FREQUENCY_RESPONSE_PHASE_LABEL)
    show()
