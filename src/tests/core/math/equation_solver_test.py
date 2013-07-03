"""
Unittests for equation_solver.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.math.equation_solver import solve_equations
from unittest import main
from unittest import TestCase

class Equation_Solver_Test(TestCase):
  """
  Tests for core/math/equation_solver.
  """
  def _assert_dict_equal(self, dict_1, dict_2):
    assert isinstance(dict_1, dict)
    assert isinstance(dict_2, dict)
    assert len(dict_1) == len(dict_2)
    for key in dict_1:
      assert key in dict_2
      assert dict_1[key] == dict_2[key]
  def test_simple_equation(self):
    solution = solve_equations([[(1, 'x')]])
    self._assert_dict_equal(solution, {'x': 0})
  def test_one_equation(self):
    solution = solve_equations([[(2, 'x'), (4, None)]])
    self._assert_dict_equal(solution, {'x': -2})
  def test_two_equations(self):
    eq_1 = [(5, 'x'), (-2, 'y'), (-3, None)]
    eq_2 = [(3, 'x'), (4, 'y'), (-33, None)]
    solution = solve_equations([eq_1, eq_2])
    self._assert_dict_equal(solution, {'x': 3, 'y': 6})
  def test_fail(self):
    self.assertRaises(Exception, solve_equations, [[(1, 'x'), (1, 'y')]])

if __name__ == '__main__':
  main()
