"""
Unit sample response.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import DEFAULT_NUM_SAMPLES
from pylab import gcf
from pylab import show
from pylab import stem
from pylab import xlabel
from pylab import ylabel
from system import System

def plot_unit_sample_response(sys, num_samples=DEFAULT_NUM_SAMPLES):
  """
  Plots the unit sample response of the given system.
  """
  assert isinstance(sys, System), 'sys must be a System'
  h = sys.unit_sample_response(num_samples)
  if h:
    stem(range(len(h)), h)
    gcf().canvas.set_window_title('H(R) = %s' % str(sys.sf))
    xlabel('n')
    ylabel('h[n]')
    show()
