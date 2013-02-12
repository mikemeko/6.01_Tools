"""
Unittests for equation_solver.py.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.math.equation_solver import solve_equations
from unittest import main
from unittest import TestCase

class Equation_Solver_Test(TestCase):
  """
  Tests for gui/math/equation_solver.
  """
  def test_simple_equation(self):
    solution = solve_equations([[(1, 'x')]])
    self.assertDictEqual(solution, {'x': 0})
  def test_one_equation(self):
    solution = solve_equations([[(2, 'x'), (4, None)]])
    self.assertDictEqual(solution, {'x': -2})
  def test_two_equations(self):
    eq_1 = [(5, 'x'), (-2, 'y'), (-3, None)]
    eq_2 = [(3, 'x'), (4, 'y'), (-33, None)]
    solution = solve_equations([eq_1, eq_2])
    self.assertDictEqual(solution, {'x': 3, 'y': 6})
  def test_fail(self):
    self.assertRaises(Exception, solve_equations, [[(1, 'x'), (1, 'y')]])

if __name__ == '__main__':
  main()
