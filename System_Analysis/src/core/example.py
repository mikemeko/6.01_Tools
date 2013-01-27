"""
System analysis example.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from constants import X
from constants import Y
from pole_zero_diagram import plot_pole_zero_diagram
from system import Adder
from system import Delay
from system import Gain
from system import System
from unit_sample_response import plot_unit_sample_response
from threading import Thread

if __name__ == '__main__':
  # sample system
  sys = System([Adder([X, 'B'], Y), Delay(Y, 'A'), Gain('A', 'B', 0.5)])
  Thread(target=plot_pole_zero_diagram, args=(sys, True)).start()
  Thread(target=plot_unit_sample_response, args=(sys,)).start()
