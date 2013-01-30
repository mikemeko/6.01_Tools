"""
Unittests for core/util.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonne)'

from core.util import is_number
from core.util import complex_str
from core.util import empty
from core.util import in_bounds
from unittest import main
from unittest import TestCase

class Util_Test(TestCase):
  """
  Tests for core/util.
  """
  def test_complex_str(self):
    self.assertEquals('1.23 + 5.68j', complex_str(complex(1.234, 5.678)))
    self.assertEquals('1.23 - 5.68j', complex_str(complex(1.234, -5.678)))
    self.assertEquals('1.234 + 5.678j', complex_str(complex(1.234, 5.678), 3))
    self.assertEquals('1.23', complex_str(complex(1.234, 0)))
    self.assertEquals('5.68j', complex_str(complex(0, 5.678)))
    self.assertEquals('0.0', complex_str(complex(0, 0)))
  def test_empty(self):
    assert empty([])
    assert not empty([22])
  def test_in_bounds(self):
    assert not in_bounds(0, 1, 3)
    assert in_bounds(1, 1, 3)
    assert in_bounds(2, 1, 3)
    assert in_bounds(3, 1, 3)
    assert not in_bounds(4, 1, 3)
  def test_is_number(self):
    assert is_number(22)
    assert is_number(22.0)
    assert is_number(2222222222222222222222222222222222222l)
    assert not is_number('22')
    assert not is_number('mikemeko')

if __name__ == '__main__':
  main()
