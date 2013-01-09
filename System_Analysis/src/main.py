"""
Main.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.pole_zero_diagram import plot_pole_zero_diagram
from core.system import Adder
from core.system import Delay
from core.system import Gain
from core.system import System
from core.unit_sample_response import plot_unit_sample_response

if __name__ == '__main__':
  # test system
  sys = System([Adder(['X', 'E'], 'A'), Gain('D', 'E', -1),
      Gain('A', 'B', 0.1), Adder(['B', 'Y'], 'C'), Delay('C', 'Y'),
      Delay('Y', 'D')])
  plot_pole_zero_diagram(sys)
  plot_unit_sample_response(sys)
