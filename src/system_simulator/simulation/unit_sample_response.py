"""
Unit sample response.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import DEFAULT_NUM_SAMPLES
from lib601.plotWindow import PlotWindow
from system import System

def plot_unit_sample_response(sys, num_samples=DEFAULT_NUM_SAMPLES):
  """
  Plots the unit sample response of the given system.
  """
  assert isinstance(sys, System), 'sys must be a System'
  h = sys.unit_sample_response(num_samples)
  if h:
    usr_plot = PlotWindow('H(R) = %s' % str(sys.sf))
    usr_plot.stem(range(len(h)), h)
