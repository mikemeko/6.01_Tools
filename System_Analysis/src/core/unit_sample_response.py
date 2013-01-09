"""
Unit sample response.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from pylab import show
from pylab import stem
from pylab import title
from pylab import xlabel
from pylab import ylabel
from system import System

def plot_unit_sample_response(sys):
  """
  Plots the unit sample response of the given system.
  """
  assert isinstance(sys, System), 'sys must be a System'
  h = sys.unit_sample_response()
  stem(range(len(h)), h)
  title('H(R) = %s' % str(sys.sf))
  xlabel('n')
  ylabel('h[n]')
  show()
