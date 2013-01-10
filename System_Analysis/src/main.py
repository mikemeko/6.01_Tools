"""
Main.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.constants import X
from core.constants import Y
from core.pole_zero_diagram import plot_pole_zero_diagram
from core.system import Adder
from core.system import Delay
from core.system import Gain
from core.system import System
from core.unit_sample_response import plot_unit_sample_response
from threading import Thread

if __name__ == '__main__':
  # sample system
  sys = System([Adder([X, 'E'], 'A'), Gain('D', 'E', -1),
      Gain('A', 'B', 0.5), Adder(['B', Y], 'C'), Delay('C', Y),
      Delay(Y, 'D')])
  Thread(target=plot_pole_zero_diagram, args=(sys,)).start()
  Thread(target=plot_unit_sample_response, args=(sys,)).start()
