"""
Unittests for util.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonne)'

from system_simulator.simulation.util import complex_str
from unittest import main
from unittest import TestCase

class Util_Test(TestCase):
  """
  Tests for util.py.
  """
  def test_complex_str(self):
    self.assertEquals('1.23 + 5.68j', complex_str(complex(1.234, 5.678)))
    self.assertEquals('1.23 - 5.68j', complex_str(complex(1.234, -5.678)))
    self.assertEquals('1.234 + 5.678j', complex_str(complex(1.234, 5.678), 3))
    self.assertEquals('1.23', complex_str(complex(1.234, 0)))
    self.assertEquals('5.68j', complex_str(complex(0, 5.678)))
    self.assertEquals('0.0', complex_str(complex(0, 0)))

if __name__ == '__main__':
  main()
