"""
Unit sample response.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from pylab import show
from pylab import stem
from pylab import xlabel
from pylab import ylabel
from system import Adder
from system import Delay
from system import Gain
from system import System

def plot_unit_sample_response(sys):
  """
  Plots the unit sample response of the given system.
  """
  assert isinstance(sys, System), 'sys must be a System'
  h = sys.unit_sample_response()
  stem(range(len(h)), h)
  xlabel('n')
  ylabel('h[n]')
  show()

if __name__ == '__main__':
  # TODO: remove when have main.py
  sys = System([Adder(['X', 'E'], 'A'), Gain('D', 'E', -1),
      Gain('A', 'B', 2), Adder(['B', 'Y'], 'C'), Delay('C', 'Y'),
      Delay('Y', 'D')])
  plot_unit_sample_response(sys)
