"""
TODO(mikemeko)
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from cmath import phase
from constants import FREQUENCY_RESPONSE_MAGNITUDE_LABEL
from constants import FREQUENCY_RESPONSE_PHASE_LABEL
from constants import FREQUENCY_RESPONSE_TITLE
from constants import FREQUENCY_RESPONSE_X_LABEL
from constants import NUM_FREQUENCY_RESPONSE_SAMPLES
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
  TODO(mikemeko)
  """
  return sum(coeffs[i] * z ** i for i in xrange(len(coeffs)))

def plot_frequency_response(sys, num_samples=NUM_FREQUENCY_RESPONSE_SAMPLES):
  """
  TODO(mikemeko)
  """
  assert isinstance(sys, System), 'sys must be a System'
  # TODO(mikemeko): what to do otherwise
  if sys.sf:
    numerator_z_coeffs = list(reversed(sys.sf.numerator_coeffs))
    denominator_z_coeffs = list(reversed(sys.sf.denominator_coeffs))
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
    gcf().canvas.set_window_title(FREQUENCY_RESPONSE_TITLE)
    subplot(211)
    plot(W, H_w_magnitude)
    ylabel(FREQUENCY_RESPONSE_MAGNITUDE_LABEL)
    subplot(212)
    plot(W, H_w_phase)
    ylabel(FREQUENCY_RESPONSE_PHASE_LABEL)
    xlabel(FREQUENCY_RESPONSE_X_LABEL)
    show()
